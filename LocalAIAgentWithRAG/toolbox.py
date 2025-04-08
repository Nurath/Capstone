"""
toolbox.py
----------
This module implements a toolkit for predictive maintenance based on industrial alarm logs.
It supports:
  • Data loading (from CSV and ZIP files)
  • Data preprocessing (pruning duplicate alarms, building overlapping sequences)
  • Anomaly detection (with autoencoder training and clustering visualization)
  • Forecasting (time-series forecasting with SARIMAX and optional Prophet)
  
Before running, make sure to install the required packages:
    pip install pandas numpy matplotlib seaborn tensorflow scikit-learn statsmodels fbprophet
"""

import os
import sys
import zipfile
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- For Autoencoder ---
from tensorflow.keras import layers, models, callbacks

# --- For Clustering & Visualization ---
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score

# --- For Forecasting ---
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error

# (Optional) Prophet – ensure it is installed. Otherwise, this part can be skipped.
try:
    from prophet import Prophet
except ImportError:
    Prophet = None


###########################
# Data Loading Utilities
###########################

def read_csv_from_zip(zip_path, file_name):
    """
    Reads a CSV file directly from a ZIP archive without extracting.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            if file_name not in zip_ref.namelist():
                print(f"Error: '{file_name}' not found in the ZIP archive.")
                return None
            with zip_ref.open(file_name) as file:
                df = pd.read_csv(file)
                return df
    except FileNotFoundError:
        print(f"Error: Zip file '{zip_path}' not found.")
    except zipfile.BadZipFile:
        print(f"Error: '{zip_path}' is not a valid zip file.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def load_dataset(path):
    """
    Loads a dataset from a CSV or ZIP file.
    If a ZIP file is given, prompts the user for the internal CSV filename.
    """
    if path.endswith('.zip'):
        csv_inside = input("Enter the CSV filename inside the ZIP (with path if needed): ").strip()
        df = read_csv_from_zip(path, csv_inside)
    elif path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        print("Unsupported file type. Please provide a '.csv' or '.zip' file.")
        return None
    if df is not None:
        print(f"Loaded dataset with shape {df.shape}")
    return df


###########################
# Preprocessing Functions
###########################

def prune_alarm_logs(df):
    """
    Remove consecutive duplicate alarms for each machine.
    Assumes the DataFrame has columns: 'serial', 'timestamp', and 'alarm'.
    """
    df_sorted = df.sort_values(["serial", "timestamp"])
    pruned_groups = []
    for serial, group in df_sorted.groupby("serial"):
        pruned_group = group.copy()
        pruned_group['prune_flag'] = pruned_group['alarm'] != pruned_group['alarm'].shift()
        pruned_group = pruned_group[pruned_group['prune_flag']]
        pruned_groups.append(pruned_group.drop(columns='prune_flag'))
    pruned_df = pd.concat(pruned_groups)
    print("After pruning, dataset shape:", pruned_df.shape)
    return pruned_df

def create_sequences(alarms, window_size=10, forecast_horizon=1):
    """
    Generates overlapping sequences from a list of alarm values.
    Returns two lists:
      - forecasting_sequences: List of (input_sequence, target_sequence) tuples.
      - anomaly_sequences: List of full window sequences for unsupervised anomaly detection.
    """
    forecasting_sequences = []
    anomaly_sequences = []
    total_length = len(alarms)
    if total_length < window_size:
        return forecasting_sequences, anomaly_sequences
    for i in range(total_length - window_size + 1):
        window = alarms[i:i+window_size]
        input_seq = window[:-forecast_horizon]
        target_seq = window[-forecast_horizon:]
        forecasting_sequences.append((input_seq, target_seq))
        anomaly_sequences.append(window)
    return forecasting_sequences, anomaly_sequences

def start_preprocessing(df, window_size=10, forecast_horizon=1, requirement='forecasting'):
    """
    Preprocess the alarm logs:
      - Prunes consecutive duplicate alarms.
      - Splits into sequences per machine (grouped by 'serial').
    Returns a dictionary mapping machine serial numbers to the generated sequences.
    """
    df_pruned = prune_alarm_logs(df)
    results = {'forecasting': {}, 'anomaly_detection': {}}
    for serial, group in df_pruned.groupby("serial"):
        group_sorted = group.sort_values("timestamp")
        alarm_list = group_sorted["alarm"].tolist()
        fc_sequences, ad_sequences = create_sequences(alarm_list, window_size, forecast_horizon)
        results['forecasting'][serial] = fc_sequences
        results['anomaly_detection'][serial] = ad_sequences
        print(f"Machine {serial}: {len(fc_sequences)} forecasting sequences, {len(ad_sequences)} anomaly sequences generated.")
    
    return results['forecasting'] if requirement == 'forecasting' else results['anomaly_detection']


###########################
# Anomaly Detection Pipeline
###########################

def run_anomaly_detection(df, window_size=10, forecast_horizon=1, machine_serial=None):
    """
    Executes the anomaly detection pipeline:
      1. Preprocess data to build sequences.
      2. Split the sequences into training and future simulation.
      3. Build and train an autoencoder.
      4. Evaluate reconstruction errors to flag anomalies.
      5. Optionally, perform clustering and t-SNE visualization.
    """
    print("Running anomaly detection pipeline...")
    # Ensure timestamps are parsed correctly
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    sequences_dict = start_preprocessing(df, window_size, forecast_horizon, requirement='anomaly_detection')
    available_machines = list(sequences_dict.keys())
    if machine_serial is None:
        machine_serial = available_machines[0]
        print(f"No machine serial provided. Defaulting to machine {machine_serial}")
    elif machine_serial not in available_machines:
        print(f"Machine serial {machine_serial} not found. Available machines: {available_machines}")
        return

    anomaly_sequences = sequences_dict[machine_serial]
    data_array = np.array(anomaly_sequences)
    print(f"Total sequences for machine {machine_serial}: {data_array.shape[0]}")
    
    # Split data: 70% for training, 30% for simulated future
    split_index = int(0.7 * len(data_array))
    train_data = data_array[:split_index]
    future_data = data_array[split_index:]
    print(f"Training data shape: {train_data.shape}, Future data shape: {future_data.shape}")
    
    # Build the autoencoder model
    input_dim = train_data.shape[1]
    encoding_dim = 32
    input_seq = layers.Input(shape=(input_dim,))
    encoded = layers.Dense(encoding_dim, activation='relu', name='encoder_layer')(input_seq)
    decoded = layers.Dense(input_dim, activation='linear', name='decoder_layer')(encoded)
    autoencoder = models.Model(input_seq, decoded)
    autoencoder.compile(optimizer='adam', loss='mse')
    autoencoder.summary()
    
    early_stop = callbacks.EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)
    autoencoder.fit(train_data, train_data, epochs=50, batch_size=32, shuffle=True, validation_split=0.2, callbacks=[early_stop])
    
    # Build a separate encoder to extract latent features
    encoder = models.Model(input_seq, encoded)
    reconstructions = autoencoder.predict(future_data)
    reconstruction_errors = np.mean(np.abs(future_data - reconstructions), axis=1)
    
    plt.figure(figsize=(10, 4))
    plt.plot(reconstruction_errors, label="Reconstruction Error")
    plt.title("Anomaly Scores on Future Data")
    plt.xlabel("Sequence Index")
    plt.ylabel("Mean Absolute Error")
    plt.legend()
    plt.show()
    
    # Set anomaly threshold (95th percentile of training errors)
    train_reconstructions = autoencoder.predict(train_data)
    train_errors = np.mean(np.abs(train_data - train_reconstructions), axis=1)
    threshold = np.quantile(train_errors, 0.95)
    print(f"Anomaly detection threshold: {threshold:.4f}")
    
    anomalies = future_data[reconstruction_errors > threshold]
    print(f"Detected {len(anomalies)} anomalous sequences out of {len(future_data)}")

    # --- Optional Clustering & Visualization ---
    train_latent = encoder.predict(train_data)
    future_latent = encoder.predict(future_data)
    num_clusters = 4
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    train_clusters = kmeans.fit_predict(train_latent)
    
    tsne = TSNE(n_components=2, random_state=42)
    tsne_results = tsne.fit_transform(train_latent)
    unique_clusters = np.unique(train_clusters)
    centroids_tsne = np.array([tsne_results[train_clusters == cluster].mean(axis=0)
                               for cluster in unique_clusters])
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(tsne_results[:, 0], tsne_results[:, 1],
                          c=train_clusters, cmap='viridis', alpha=0.6, s=10)
    plt.scatter(centroids_tsne[:, 0], centroids_tsne[:, 1],
                marker='*', s=300, c='red', label='Centroids')
    plt.colorbar(scatter, label='Cluster Label')
    plt.title('t-SNE Projection of Training Latent Features')
    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.legend()
    plt.show()
    
    sil_score = silhouette_score(train_latent, train_clusters)
    print("Silhouette Score (Training latent space):", sil_score)
    
    return {
        'autoencoder': autoencoder,
        'encoder': encoder,
        'threshold': threshold,
        'anomalies': anomalies,
        'train_data': train_data,
        'future_data': future_data
    }


###########################
# Forecasting Pipeline
###########################

def run_forecasting(df):
    """
    Executes the forecasting pipeline:
      1. Preprocess and aggregate the alarm logs into a time series.
      2. Checks stationarity and decomposes the series.
      3. Fits a SARIMAX model and produces forecast plots.
      4. Calculates in-sample metrics.
    Optionally, it runs a Prophet forecast if available.
    """
    print("Running forecasting pipeline...")
    # Ensure proper datetime parsing and sort
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values("timestamp")
    df.set_index('timestamp', inplace=True)
    
    # Aggregate alarm counts (daily)
    df_aggregated = df['alarm'].resample('D').sum()
    plt.figure(figsize=(12, 6))
    plt.plot(df_aggregated, label="Daily Alarm Count")
    plt.title("Historical Daily Alarm Counts")
    plt.xlabel("Date")
    plt.ylabel("Number of Alarms")
    plt.legend()
    plt.show()
    
    # Check for stationarity and decompose
    adf_test = adfuller(df_aggregated)
    print(f"ADF Statistic: {adf_test[0]}, p-value: {adf_test[1]}")
    decomposition = sm.tsa.seasonal_decompose(df_aggregated, model='additive')
    fig = decomposition.plot()
    fig.set_size_inches(12, 8)
    plt.show()
    
    # Fit SARIMAX model
    model = sm.tsa.statespace.SARIMAX(df_aggregated, order=(1, 1, 1),
                                      seasonal_order=(1, 1, 1, 12),
                                      enforce_stationarity=False,
                                      enforce_invertibility=False).fit()
    print(model.summary())
    model.plot_diagnostics(figsize=(12, 8))
    plt.show()
    
    # Forecast future alarm counts (e.g., next 30 days)
    steps = 30
    forecast = model.get_forecast(steps=steps)
    forecast_values = forecast.predicted_mean
    forecast_index = pd.date_range(df_aggregated.index[-1], periods=steps+1, freq='D')[1:]
    forecast_series = pd.Series(forecast_values, index=forecast_index)
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_aggregated, label="Historical Alarm Counts")
    plt.plot(forecast_series, label="Forecasted Alarm Counts", color='red')
    plt.title("Alarm Counts Forecast using SARIMAX")
    plt.xlabel("Date")
    plt.ylabel("Number of Alarms")
    plt.legend()
    plt.show()
    
    forecast_ci = forecast.conf_int()
    plt.figure(figsize=(12, 6))
    plt.plot(df_aggregated, label="Historical Alarm Counts")
    plt.plot(forecast_series, label="Forecasted Alarm Counts", color='red')
    plt.fill_between(forecast_index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color='pink', alpha=0.3)
    plt.title("Forecast with Confidence Intervals")
    plt.xlabel("Date")
    plt.ylabel("Number of Alarms")
    plt.legend()
    plt.show()
    
    in_sample_preds = model.predict(start=df_aggregated.index[0], end=df_aggregated.index[-1])
    mse = mean_squared_error(df_aggregated, in_sample_preds)
    print(f"In-sample Mean Squared Error (MSE): {mse}")
    
    # (Optional) Run Prophet forecast if available
    if Prophet is not None:
        print("Running Prophet forecast...")
        prophet_df = df_aggregated.reset_index().rename(columns={'timestamp':'ds', 'alarm':'y'})
        prophet_model = Prophet()
        prophet_model.fit(prophet_df)
        future = prophet_model.make_future_dataframe(periods=steps)
        forecast_prophet = prophet_model.predict(future)
        prophet_model.plot(forecast_prophet)
        plt.title("Prophet Forecast")
        plt.show()
    
    return model

# End of toolbox.py
