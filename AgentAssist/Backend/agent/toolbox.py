import zipfile, uuid
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import logging

import torch
import torch.nn as nn
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error

# Try to import plotly, fall back to matplotlib if not available
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Importing plotly failed. Interactive plots will not work.")

try:
    from prophet import Prophet
except ImportError:
    Prophet = None

logger = logging.getLogger(__name__)

# PyTorch Autoencoder model
class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(32, input_dim),
            nn.Linear(input_dim, input_dim)
        )
    
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

def read_csv_from_zip(zip_path: str, file_name: str) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path, 'r') as z:
        if file_name not in z.namelist():
            raise FileNotFoundError(f"'{file_name}' not in '{zip_path}'")
        return pd.read_csv(z.open(file_name))

def load_dataset(path: str) -> pd.DataFrame:
    """Load a CSV or first CSV inside a ZIP."""
    if path.lower().endswith('.zip'):
        with zipfile.ZipFile(path, 'r') as z:
            csvs = [f for f in z.namelist() if f.lower().endswith('.csv')]
        if not csvs:
            raise IOError(f"No CSV in archive '{path}'")
        return read_csv_from_zip(path, csvs[0])
    elif path.lower().endswith('.csv'):
        return pd.read_csv(path)
    else:
        raise ValueError("Provide a .csv or .zip file")

def prune_alarm_logs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(['serial','timestamp']).copy()
    out = []
    for serial, grp in df.groupby('serial'):
        g = grp.copy()
        g['keep'] = g['alarm'] != g['alarm'].shift()
        out.append(g[g['keep']].drop(columns='keep'))
    return pd.concat(out)

def create_sequences(alarms: list, window_size=10, forecast_horizon=1):
    fc, anom = [], []
    L = len(alarms)
    if L < window_size:
        return fc, anom
    for i in range(L - window_size + 1):
        w = alarms[i:i+window_size]
        fc.append((w[:-forecast_horizon], w[-forecast_horizon:]))
        anom.append(w)
    return fc, anom

def start_preprocessing(df, window_size=10, forecast_horizon=1, requirement='forecasting'):
    df['timestamp'] = pd.to_timedelta(df['timestamp'])
    pr = prune_alarm_logs(df)
    out = {'forecasting':{}, 'anomaly':{}}
    for serial, grp in pr.groupby('serial'):
        fc, an = create_sequences(
            grp.sort_values('timestamp')['alarm'].tolist(),
            window_size, forecast_horizon
        )
        out['forecasting'][serial] = fc
        out['anomaly'][serial]     = an
    return out['forecasting'] if requirement=='forecasting' else out['anomaly']

def fig_to_base64(fig):
    """Convert a figure to base64 string, handling both plotly and matplotlib figures"""
    buf = BytesIO()
    if PLOTLY_AVAILABLE and isinstance(fig, go.Figure):
        fig.write_image(buf, format='png')
    else:
        fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    if not PLOTLY_AVAILABLE:
        plt.close(fig)
    return img_str

def parse_timestamp(ts):
    # Handles hh:mm:ss, mm:ss, and MM:SS.s formats
    try:
        parts = ts.split(':')
        if len(parts) == 3:
            hours, mins, secs = parts
            return int(hours) * 3600 + int(mins) * 60 + float(secs)
        elif len(parts) == 2:
            mins, secs = parts
            return int(mins) * 60 + float(secs)
        else:
            return float(ts)
    except Exception:
        return None

def run_anomaly_detection(path: str, window_size=10, forecast_horizon=1, machine_serial=None):
    logger.info(f"Starting anomaly detection on {path}")
    try:
        print(f"Loading dataset from {path}")
        # Load dataset with better error handling
        try:
            df = load_dataset(path)
        except Exception as e:
            logger.error(f"Failed to load dataset: {str(e)}")
            return {"summary": f"Error loading dataset: {str(e)}", "figures": []}
        
        logger.info("Converting timestamp column to datetime")
        # More robust timestamp conversion with error handling
        try:
            # First check if timestamp column exists
            if 'timestamp' not in df.columns:
                logger.error("No 'timestamp' column found in data")
                return {"summary": "Error: No timestamp column found in data", "figures": []}
                
            # Try to convert with more flexible format handling
            df['timestamp'] = df['timestamp'].apply(parse_timestamp)
            
            # Check for NaT values after conversion
            if df['timestamp'].isna().any():
                logger.warning("Some timestamp values could not be parsed. Dropping those rows.")
                df = df.dropna(subset=['timestamp'])
                
            # If we have no data left after dropping NaT values
            if len(df) == 0:
                return {"summary": "Error: No valid timestamp data after conversion", "figures": []}
        except Exception as e:
            logger.error(f"Timestamp conversion failed: {str(e)}")
            return {"summary": f"Error processing timestamps: {str(e)}", "figures": []}
        
        # Check for required columns
        if 'alarm' not in df.columns or 'serial' not in df.columns:
            missing = []
            if 'alarm' not in df.columns:
                missing.append('alarm')
            if 'serial' not in df.columns:
                missing.append('serial')
            msg = f"Missing required columns: {', '.join(missing)}"
            logger.error(msg)
            return {"summary": f"Error: {msg}", "figures": []}
        
        # Ensure data types are correct
        try:
            df['alarm'] = pd.to_numeric(df['alarm'], errors='coerce')
            df['serial'] = pd.to_numeric(df['serial'], errors='coerce')
            df = df.dropna(subset=['alarm', 'serial'])
        except Exception as e:
            logger.error(f"Error converting data types: {str(e)}")
            return {"summary": f"Error converting data types: {str(e)}", "figures": []}
            
        logger.info("Starting preprocessing")
        # Check data size before preprocessing
        if len(df) < window_size:
            msg = f"Insufficient data: need at least {window_size} rows, but have {len(df)}"
            logger.error(msg)
            return {"summary": msg, "figures": []}
            
        seqs = start_preprocessing(df, window_size, forecast_horizon, requirement='anomaly')
        logger.info(f"Preprocessing complete. Found {len(seqs)} sequences")
        
        if not seqs:
            logger.warning("No sequences generated.")
            return {"summary":"No sequences generated. Check that data contains valid machine serial numbers.", "figures":[]}
            
        # If no specific machine_serial provided, use the first one from the data
        if machine_serial is None:
            available_serials = list(seqs.keys())
            if not available_serials:
                return {"summary": "No machine serials found in data", "figures": []}
                
            machine_serial = next(iter(seqs))
            logger.info(f"No machine_serial specified, using: {machine_serial}")
        else:
            # Check if the specified machine_serial exists in the data
            if str(machine_serial) not in [str(s) for s in seqs.keys()]:
                available = ", ".join([str(s) for s in seqs.keys()])
                logger.warning(f"Specified machine_serial {machine_serial} not found in data. Available: {available}")
                return {"summary": f"Machine {machine_serial} not found in data. Available: {available}", "figures": []}
        
        # Convert machine_serial to correct type if needed
        if isinstance(next(iter(seqs.keys())), int) and not isinstance(machine_serial, int):
            try:
                machine_serial = int(machine_serial)
            except:
                pass
                
        data = np.array(seqs.get(machine_serial, []))
        if data.size == 0:
            logger.warning(f"No data for machine {machine_serial}.")
            return {"summary":f"No data for machine {machine_serial}.", "figures":[]}
            
        # Check if we have enough data for splitting
        if len(data) < 3:  # Arbitrary minimum
            return {"summary": f"Insufficient data for machine {machine_serial}: need at least 3 sequences", "figures": []}
            
        split = max(1, int(0.7*len(data)))  # Ensure at least 1 sample in training
        train, future = data[:split], data[split:]
        
        # Handle the case where either set is empty
        if len(train) == 0 or len(future) == 0:
            if len(data) >= 2:
                # Use minimum split of 1 item in future set
                train, future = data[:-1], data[-1:]
            else:
                # If we have only 1 item, duplicate it for demonstration
                train, future = data, data
                
        if train.ndim == 1:
            train = train.reshape(-1, window_size)
                
        train_tensor = torch.FloatTensor(train)
        future_tensor = torch.FloatTensor(future)
        dim = train.shape[1]
        model = Autoencoder(dim)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        model.train()
        
        # Rest of the function remains the same
        for epoch in range(20):
            optimizer.zero_grad()
            outputs = model(train_tensor)
            loss = criterion(outputs, train_tensor)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            recon_f = model(future_tensor).numpy()
            recon_t = model(train_tensor).numpy()
        errs = np.mean(np.abs(future-recon_f), axis=1)
        errs_t = np.mean(np.abs(train-recon_t), axis=1)
        thresh = np.quantile(errs_t, 0.95)
        n_anom = int((errs>thresh).sum())
        figures = []
        if PLOTLY_AVAILABLE:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(y=errs, name="Error"))
            fig1.add_hline(y=thresh, line_dash="dash", line_color="red", name="Threshold")
            fig1.update_layout(title="Reconstruction Error", showlegend=True)
        else:
            fig1 = plt.figure(figsize=(10,4))
            plt.plot(errs, label="Error")
            plt.axhline(thresh, color='r', linestyle='--', label='Threshold')
            plt.legend()
            plt.title("Reconstruction Error")
        figures.append(fig_to_base64(fig1))
        encoder = model.encoder
        with torch.no_grad():
            latent = encoder(train_tensor).numpy()
        clusters = KMeans(4, random_state=42).fit_predict(latent)
        tsne_res = TSNE(2, random_state=42).fit_transform(latent)
        if PLOTLY_AVAILABLE:
            fig2 = px.scatter(x=tsne_res[:,0], y=tsne_res[:,1], color=clusters,
                             title="t-SNE of Latent Space", opacity=0.6)
        else:
            fig2 = plt.figure(figsize=(6,6))
            plt.scatter(tsne_res[:,0], tsne_res[:,1], c=clusters, alpha=0.6)
            plt.title("t-SNE of Latent Space")
        figures.append(fig_to_base64(fig2))
        summary = (f"Machine {machine_serial}: {n_anom}/{len(future)} anomalies "
                   f"(threshold={thresh:.4f})")
        logger.info("Anomaly detection completed successfully")
        logger.info(f"Train shape: {train.shape}, Future shape: {future.shape}")
        return {"summary": summary, "figures": figures}
    except Exception as e:
        logger.error(f"Anomaly detection failed: {str(e)}")
        return {"summary": f"Error: {str(e)}", "figures": []}

def run_forecasting(path: str, steps=30):
    df = load_dataset(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').set_index('timestamp')

    series = df['alarm'].resample('D').count()

    _ = adfuller(series)  # just to show it's called
    decomp = sm.tsa.seasonal_decompose(series, model='additive')
    fig_decomp = decomp.plot()
    fig_decomp.set_size_inches(12,8)

    model = sm.tsa.statespace.SARIMAX(
        series, order=(1,1,1), seasonal_order=(1,1,1,12),
        enforce_stationarity=False, enforce_invertibility=False
    ).fit(disp=False)
    fig_diag = model.plot_diagnostics(figsize=(12,8))

    fc = model.get_forecast(steps=steps)
    mean_fc = fc.predicted_mean
    ci = fc.conf_int()

    figures = []
    # history
    f1 = plt.figure(figsize=(10,5))
    plt.plot(series, label="History")
    plt.title("Historical Counts")
    figures.append(fig_to_base64(f1))

    # forecast + CI
    f2 = plt.figure(figsize=(10,5))
    plt.plot(series, label="History")
    plt.plot(mean_fc, label="Forecast")
    plt.fill_between(mean_fc.index, ci.iloc[:,0], ci.iloc[:,1], alpha=0.3)
    plt.legend()
    plt.title("Forecast with 95% CI")
    figures.append(fig_to_base64(f2))

    figures.append(fig_to_base64(fig_decomp))
    figures.append(fig_to_base64(fig_diag))

    if Prophet:
        pdf = series.reset_index().rename(columns={'timestamp':'ds','alarm':'y'})
        pm = Prophet().fit(pdf)
        fut = pm.make_future_dataframe(periods=steps)
        pr = pm.predict(fut)
        fig_prophet = pm.plot(pr)
        figures.append(fig_to_base64(fig_prophet))

    return {
        "forecast": mean_fc.to_dict(),
        "figures": figures
    }

def generate_synthetic_data(path: str, task: str, anomaly_pct: float = None, series_noise: float = 0.1) -> str:
    df = load_dataset(path)
    if task == 'anomaly':
        if anomaly_pct is None:
            raise ValueError("Need anomaly_pct for anomaly task")
        syn = df.copy().reset_index(drop=True)
        n = len(syn)
        k = int(n * anomaly_pct)
        idx = np.random.choice(n, k, replace=False)
        syn.loc[idx, 'alarm'] = -1
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        daily = df.set_index('timestamp')['alarm'].resample('D').count()
        noise = np.random.normal(0, daily.std()*series_noise, size=len(daily))
        syn = pd.DataFrame({
            'timestamp': daily.index,
            'alarm': np.round(daily + noise).astype(int)
        })

    out_name = f"test.csv"
    syn.to_csv(out_name, index=False)
    return out_name 