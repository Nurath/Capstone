# Industrial Alarm Logs Data Processing & EDA Overview

## Overview
This project focuses on analyzing alarm logs generated by industrial packaging machines. The goal is to use these logs to develop machine learning models for tasks such as next-alarm forecasting, multi-label classification, sequence prediction, and anomaly detection. The dataset comes originally as a raw CSV file (`alarms.csv`), which is then processed into various formats for direct use in modeling.

## Data Files

### Raw Data
- **alarms.csv**:  
  The original dataset containing raw alarm logs. Each row in the CSV provides:
  - **timestamp**: When the alarm occurred.
  - **alarm**: The alarm code (154 distinct codes).
  - **serial**: Identifier for the machine generating the alarm.

### Processed Data
These files are produced by the data processing pipeline implemented in `dataset.py` and are the outputs of several transformation steps applied to the raw data.

- **all_alarms.pickle**
- **all_alarms.json**
- **all_alarms.npz**

They have undergone the following processing steps:
- **Segmentation and Windowing**:  
  The raw alarm logs are divided into fixed-length input/output sequences based on sliding windows (e.g., an input window of 1720 minutes and an output window of 480 minutes).
- **Pruning and Padding**:  
  Consecutive duplicate alarms are removed (pruning) to reduce noise, and the sequences are padded to ensure all samples have uniform length.
- **Dataset Splitting**:  
  The processed data is split into training and test sets with additional stratification based on machine serial numbers, making the data ready for various machine learning tasks.

## EDA and Data Verification

### Raw Data EDA
Extensive exploratory data analysis (EDA) has been performed on the raw `alarms.csv` file to understand:
- The distribution of alarm codes and the imbalance present in the data.
- Temporal patterns, such as daily or weekly trends in alarm occurrences.
- Machine-specific behavior by analyzing alarms per machine.

### Processed Data EDA
While the processed files are designed to be “ready-to-use” for modeling, it is still advisable to perform some basic checks, such as:
- **Verifying Shapes and Splits**:  
  Confirm that the training and test splits have the expected number of samples and that sequence lengths match the intended design.
- **Distribution Checks**:  
  Validate that the alarm code distributions within the sequences remain consistent with the raw data insights.
- **Sanity Checks**:  
  Ensure that the processing steps (e.g., pruning and padding) have been applied correctly.

**Note:**  
Since the processed files (`all_alarms.json`, `all_alarms.npz`, and `all_alarms.pickle`) are derived directly from the already-analyzed raw data, extensive EDA on these files is optional. Our primary focus for modeling is to work with the raw data directly, knowing that the processing pipeline has been verified to produce data in a format suitable for machine learning tasks.

---

## New Data Structure for Forecasting and Anomaly Detection

In addition to the standard processed datasets, our updated preprocessing pipeline now produces a versatile data structure that supports both forecasting models and anomaly detection tasks. This new structure is stored in a pickle file (e.g., `alarm_sequences_for_models.pkl`) and is organized as follows:

- **`forecasting`**:  
  For each machine, this key contains a list of tuples. Each tuple represents a sliding-window sample where:
  - The **input sequence** is the first part of the window (e.g., the first *n – h* alarms).
  - The **target sequence** is the subsequent alarms (the next *h* alarms) that are to be forecast.
  
  This format is directly suitable for supervised forecasting models, such as sequence-to-sequence predictors, RNNs, or LSTM networks.

- **`anomaly_detection`**:  
  For each machine, this key holds a list of full sliding-window sequences. These sequences contain the entire window of alarms and are ideal for unsupervised anomaly detection methods, such as autoencoders, clustering techniques, or isolation forests, which can learn the normal patterns of alarms and flag deviations.

### How to Use the Preprocessed Data Structure

1. **Loading the Data:**

   Use Python's pickle module to load the data structure:
   ```python
   import pickle

   with open("alarm_sequences_for_models.pkl", "rb") as f:
       results = pickle.load(f)
   ```

2. **For Forecasting:**

   The forecasting data is accessed via the `results['forecasting']` key, which maps each machine serial to a list of `(input_sequence, target_sequence)` tuples.
   ```python
   forecasting_data = results['forecasting']
   # Example: Use data for machine with serial '3'
   machine3_forecasting = forecasting_data[3]  # List of (input, target) tuples
   # You can now use machine3_forecasting as training data for a forecasting model.
   ```

3. **For Anomaly Detection:**

   The anomaly detection data is accessed via the `results['anomaly_detection']` key. Each machine serial maps to a list of full sliding-window sequences.
   ```python
   anomaly_data = results['anomaly_detection']
   # Example: Use data for machine with serial '3'
   machine3_anomaly_sequences = anomaly_data[3]  # List of full sliding-window sequences
   # These sequences can be used as inputs to train an autoencoder or other anomaly detection model.
   ```

4. **Integration in Your Programs:**

   - **Forecasting Models:**  
     Pass the `(input_sequence, target_sequence)` pairs from the `forecasting` key to your training pipeline. Preprocess the sequences as needed (e.g., applying one-hot encoding or embeddings) before feeding them to a neural network or traditional forecasting algorithm.

   - **Anomaly Detection Models:**  
     Use the full sliding-window sequences from the `anomaly_detection` key to establish normal behavior profiles. Techniques like reconstruction error from an autoencoder or density estimation can be applied to detect abnormal patterns in new sequences.

This enhanced data structure streamlines the process of experimenting with different machine learning tasks using the same underlying sliding-window approach, ensuring both forecasting and anomaly detection pipelines can leverage the processed alarm log data effectively.
