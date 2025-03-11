# Implement Fault Identification via Alarm Clustering and Visualization

## Overview

This module implements fault identification using unsupervised clustering on industrial alarm logs. By leveraging an autoencoder to learn latent representations of alarm sequences and applying KMeans clustering, the module groups similar sequences into clusters—each representing a potential fault type (e.g., mechanical, electrical). Advanced visualizations (t‑SNE projections, distance metrics, silhouette scores) and sample outputs help verify and interpret the clustering results.

This README and code focus exclusively on the issue:
**"Implement Fault Identification via Alarm Clustering and Visualization"**

## Data Description

The module uses preprocessed alarm sequence data from the file:
- **`alarm_sequences_for_models.pkl`**

This pickle file contains two primary components:
- **Forecasting Data:** Sliding-window sequences for supervised forecasting.
- **Anomaly Detection Data:** Full sliding-window sequences used here to simulate live data and for clustering.

For fault analysis, we select one machine’s anomaly detection data, split it into training (past) and simulated future (live) segments, and then work with these sequences.

## Requirements

- Python 3.x
- TensorFlow (with Keras)
- NumPy
- Pandas
- scikit-learn
- Matplotlib

Install the required packages using:
```bash
pip install numpy pandas matplotlib scikit-learn tensorflow
```

## Pipeline

The module’s pipeline consists of the following steps:

1. **Data Loading & Splitting:**  
   - Load the preprocessed data (`alarm_sequences_for_models.pkl`).
   - Select alarm sequences for a specific machine (e.g., serial 3).
   - Split the data into training (past) and future (simulated live) sets.

2. **Autoencoder Training:**  
   - Train a simple autoencoder on the training data to learn latent representations of alarm sequences.
   - Use the encoder portion to extract latent features for clustering.

3. **Clustering:**  
   - Apply KMeans clustering on the latent representations to group sequences into clusters (fault types).
   - Determine cluster centroids and assign predicted cluster labels to each sequence.

4. **Visualization & Metrics:**  
   - Use t‑SNE to project high-dimensional latent features into 2D for visualization.
   - Overlay cluster centroids on the t‑SNE plot.
   - Compute Euclidean distances from each sample’s latent vector to its cluster centroid.
   - Calculate average cluster compactness (distance metrics) and the silhouette score to assess clustering quality.

5. **Sample Results Display:**  
   - Randomly select sample future sequences.
   - Display each sequence’s alarm codes, predicted fault cluster, and distance to the corresponding centroid.

## Usage

1. **Download and Prepare Data:**  
   Ensure that the `alarm_sequences_for_models.pkl` file is available. The code downloads it automatically if it is missing.

2. **Run the Notebook/Script:**  
   Execute the module in your local Jupyter environment, Google Colab, or any Python IDE.

3. **Review Outputs:**  
   - Console outputs include training statistics, silhouette scores, and sample sequence details.
   - Visual outputs include:
     - t‑SNE projections with cluster centroids.
     - Bar charts of average distances to centroids per cluster.
     - Plots of reconstruction errors used for anomaly detection.

### Example Output

```
Sequence 1239:
Alarms: [26, 139, 11, 19, 139, 11, 139, 11, 31, 139]
Predicted Cluster (Fault Type): 2
Distance to Centroid: 3.2500
--------------------------------------------------
```

Additionally, the module produces informative visualizations to help interpret clustering performance.

## Notes

- **Simulation:** The module simulates live data by splitting the dataset into past (training) and future segments.
- **Customization:** Autoencoder architecture, latent space dimensions, and the number of clusters can be adjusted to suit different datasets.
- **Deployment:** Although designed for local testing (Windows/Colab), the code is modular and can be integrated into production pipelines (e.g., on AWS) for batch processing of alarm logs.

## License

Open Source

## Contact

For questions or further improvements, please open an issue in the repository.

---

Happy Fault Hunting!
