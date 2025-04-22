#  AI-Powered Predictive Maintenance and RAG Troubleshooting

## Overview
his project combines advanced AI techniques for anomaly detection, fault classification, and predictive maintenance with a Retrieval-Augmented Generation (RAG) chatbot for real-time equipment troubleshooting. Designed for industrial packaging machines, the system empowers proactive maintenance aligned with Industry 4.0 standards.


## Dataset Description
The dataset, titled **Alarm Logs of Industrial Packaging Machines** (https://ieee-dataport.org/open-access/alarm-logs-packaging-industry-alpi), includes:
- **Raw Data**: A CSV file (`alarms.csv`) containing timestamped alarm codes and machine serial numbers from 20 machines worldwide (Feb 21, 2019 – Jun 17, 2020).
- **Processed Data**: Preprocessed formats (JSON, Pickle, NPZ) that provide training and testing sequences for tasks such as anomaly detection, next alarm forecasting, and fault classification.

## Project Objectives
- **Anomaly Detection**: Identify unusual patterns in alarm logs to preempt equipment failures.
- **Forecasting**: Predict future alarms using time-series forecasting models.
- **Fault Classification**: Categorize faults to streamline maintenance processes.
- **Real-Time Monitoring & Optimization**: Integrate LLM-based agents for fault identification and continuous system improvement.
- **Chatbot for Troubleshooting**: Develop a Retrieval-Augmented Generation (RAG) chatbot to assist operators with real-time diagnostics.

## Project Structure
```
.
Capstone/
├── Dataset/
│   ├── alarms_log_data.zip
│   │   ├── raw/
│   │   │   └── alarms.csv
│   │   └── processed/
│   │       ├── all_alarms.json
│   │       ├── all_alarms.npz
│   │       └── all_alarms.pickle
│   ├── dataset.py            # Data preprocessing and dataset creation scripts
│   └── README.md             # Instructions and overview for the dataset
├── EDA And Preprocessing/
│   ├── EDA_and_Preprocessing.ipynb  # Notebook for exploratory data analysis and preprocessing
│   └── README.md                    # Instructions and context for the EDA work
├── models/                     # Machine learning model implementations
├── chatbot/                    # RAG-based chatbot components for troubleshooting
├── docs/                       # Additional documentation and presentation slides
├── requirements.txt            # Python dependency list
└── README.md                   # Top-level project overview and instructions

```

## Milestones & GitHub Issues
The project is organized into four key milestones:

1. **Data Preprocessing and Model Training**
   - Data ingestion, cleaning, and feature extraction.
   - Building baseline anomaly detection, forecasting, and fault classification models.

2. **Utilizing LLMs for Fault Identification and System Optimization**
   - Integrating language models for advanced fault identification.
   - Developing real-time monitoring and continuous improvement modules.

3. **Building a RAG-Based Chatbot for Troubleshooting**
   - Designing and implementing a chatbot to assist with system diagnostics.
   - Integrating data retrieval from historical logs and real-time information.

4. **Model Improvement and Evaluation**
   - Generating synthetic data for model augmentation.
   - Setting up comprehensive evaluation and hyperparameter tuning pipelines.
   - Conducting robustness testing and further system refinements.

## Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/Nurath/Capstone.git
   cd Capstone
   ```
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **(Optional) Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage
- **Data Processing**:  
  Use `dataset.py` to convert raw alarm logs into processed formats.
  ```bash
  python dataset.py --input raw/alarms.csv --output processed/
  ```
- **Model Training**:  
  Navigate to the `models/` directory and run the training scripts for anomaly detection, forecasting, or fault classification.
  ```bash
  python models/train_anomaly.py
  ```
- **Chatbot Interface**:  
  Launch the RAG-based chatbot from the `chatbot/` directory.
  ```bash
  python chatbot/run_chatbot.py
  ```

## Contributing
Contributions are welcome! Please submit issues or pull requests. Follow the established milestones and GitHub issue plan for structured development.

## License
This project is licensed under the MIT License.

## Acknowledgments
- **Dataset Authors**: Diego Tosato, Davide Dalle Pezze, Chiara Masiero, Gian Antonio Susto, Alessandro Beghi.
- Thanks to the industrial partners and research teams supporting the development of advanced AI solutions for smart manufacturing.
