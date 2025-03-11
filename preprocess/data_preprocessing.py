import pandas as pd


def prune_alarm_logs(df):
    # Sort the data by timestamp for each machine
    df_sorted = df.sort_values(["serial", "timestamp"])
    # Group by machine serial and remove consecutive duplicate alarms
    pruned_groups = []
    for serial, group in df_sorted.groupby("serial"):
        pruned_group = group.copy()
        # Create a flag to identify where the current alarm differs from the previous one
        pruned_group['prune_flag'] = pruned_group['alarm'] != pruned_group['alarm'].shift()
        pruned_group = pruned_group[pruned_group['prune_flag']]
        pruned_groups.append(pruned_group.drop(columns='prune_flag'))

    pruned_groups = pd.concat(pruned_groups)
    print("Original number of rows:", pruned_groups.shape[0])
    print("After pruning consecutive duplicates:", pruned_groups.shape[0])
    return pruned_groups

def create_sequences(alarms, window_size=10, forecast_horizon=1):
    """
    Generates overlapping sequences from a list of alarms.

    For forecasting:
      - Input: the first (window_size - forecast_horizon) alarms in the window.
      - Target: the last forecast_horizon alarms.

    For anomaly detection:
      - Uses the full sliding window as the observation.

    Parameters:
      alarms (list): A list of alarm codes.
      window_size (int): Total length of the sliding window.
      forecast_horizon (int): Number of alarms at the end of the window to be used as forecast target.

    Returns:
      forecasting_sequences (list of tuples): Each tuple is (input_sequence, target_sequence)
      anomaly_sequences (list): Each element is the full window sequence.
    """
    forecasting_sequences = []
    anomaly_sequences = []
    total_length = len(alarms)
    # Ensure that we have enough alarms to create at least one sequence.
    if total_length < window_size:
        return forecasting_sequences, anomaly_sequences
    for i in range(total_length - window_size + 1):
        window = alarms[i:i+window_size]
        # Split the window: first part for input, last part for forecast target
        input_seq = window[:-forecast_horizon]
        target_seq = window[-forecast_horizon:]
        forecasting_sequences.append((input_seq, target_seq))
        anomaly_sequences.append(window)
    return forecasting_sequences, anomaly_sequences

def start_preprocessing(df,window_size=10,forecast_horizon=1,requirement='forecasting'):
    df_pruned = prune_alarm_logs(df)
    results = {
    'forecasting': {},        # For supervised forecasting: (input, target) pairs
    'anomaly_detection': {}   # For unsupervised anomaly detection: full sequences
    }

    for serial, group in df_pruned.groupby("serial"):
        # Sort the data by timestamp to maintain temporal order
        group_sorted = group.sort_values("timestamp")
        alarm_list = group_sorted["alarm"].tolist()

        # Generate both forecasting and anomaly detection sequences
        fc_sequences, ad_sequences = create_sequences(alarm_list, window_size=window_size, forecast_horizon=forecast_horizon)

        results['forecasting'][serial] = fc_sequences
        results['anomaly_detection'][serial] = ad_sequences
        print(f"Machine {serial}: Generated {len(fc_sequences)} forecasting sequences and {len(ad_sequences)} anomaly detection sequences.")
    
    if requirement == 'forecasting':
        return results['forcasting']
    
    else:
        return results['anomaly_detection']