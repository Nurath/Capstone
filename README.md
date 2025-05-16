#  AI-Powered Predictive Maintenance and RAG Troubleshooting

## Overview
This project combines advanced AI techniques for anomaly detection, fault classification, and predictive maintenance with a Retrieval-Augmented Generation (RAG) chatbot for real-time equipment troubleshooting. Designed for industrial packaging machines, the system empowers proactive maintenance aligned with Industry 4.0 standards.


## Dataset Description
The dataset, titled **Alarm Logs of Industrial Packaging Machines** (https://ieee-dataport.org/open-access/alarm-logs-packaging-industry-alpi), includes:
- **Raw Data**: A CSV file (`alarms.csv`) containing timestamped alarm codes and machine serial numbers from 20 machines worldwide (Feb 21, 2019 – Jun 17, 2020).
- **Processed Data**: Preprocessed formats (JSON, Pickle, NPZ) that provide training and testing sequences for tasks such as anomaly detection, next alarm forecasting, and fault classification.

## 🎯 Project Objectives
- **Anomaly Detection:** Spot deviations in alarm behavior
- **Time-Series Forecasting:** Predict future alarms/events
- **Fault Classification:** Categorize equipment issues using ML
- **RAG Chatbot:** Guide technicians with image- and text-based instructions from manuals
- **LLM Integration:** Leverage language models for real-time fault detection and resolution

---

# Agent Assist Project

This project consists of a Flask backend and a React frontend that work together to provide an AI-powered agent assistance system.

## Core Project Structure

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
AgentAssistProject/
├── AgentAssistBackEnd/
│   ├── agent/           # Backend agent implementation
│   ├── app.py          # Main Flask application
│   └── requirements.txt # Python dependencies
│
└── AgentAssistFrontEnd/
    ├── src/            # React source code
    ├── public/         # Static assets
    ├── package.json    # Node.js dependencies
    └── various config files (vite, typescript, etc.)
```

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn package manager

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd AgentAssistBackEnd
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with the following environment variables:
   ```
   OPENAI_API_KEY=your_api_key_here
   FLASK_APP=app.py
   FLASK_ENV=development
   ```

5. Run the backend server:
   ```bash
   python app.py
   ```
   The backend server will start on `http://localhost:5000`

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd AgentAssistFrontEnd
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   The frontend will be available at `http://localhost:5173`

## Running the Project

1. Start the backend server first (follow Backend Setup steps 4-5)
2. In a separate terminal, start the frontend development server (follow Frontend Setup steps 2-3)
3. Open your browser and navigate to `http://localhost:5173`

## Development

- Backend API endpoints are available at `http://localhost:5000`
- Frontend development server supports hot reloading
- Backend uses Flask for the API server
- Frontend uses React with TypeScript, Vite, and Tailwind CSS

## Building for Production

### Backend
The backend is ready for production deployment. Make sure to set appropriate environment variables in production.

### Frontend
To build the frontend for production:
```bash
cd AgentAssistFrontEnd
npm run build
# or
yarn build
```
The built files will be in the `dist` directory.

## Additional Notes

- Make sure both backend and frontend servers are running simultaneously
- The backend requires various Python packages for AI/ML functionality
- The frontend uses modern React features and TypeScript for type safety
- Tailwind CSS is used for styling
- The project uses Vite as the build tool for the frontend 

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

## Other Usage
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
- **RAG CHATBOT DEPLOYMENT**:
  
  ***Local Deployment***
  - Uses local FAISS, openAI Enbedding, Deepseek or OpenAI, and Manual PDF.
  - Images and chunks stored in local files.
 
  ```bash
  cd RAG_PDF/
  streamlit run app.py
  ```

  ***Cloud Deployment***
  - Uses MongoDB for Text chunks and embeddings and AWS S3 for images.
 
    ```bash
    cd RAG_PDF_1/
    streamlit run app.py
    ```
Make sure .env is configured with OpenAIor DeepSeek, MongoDB URI and AWS keys.

## Contributing
Contributions are welcome! Please submit issues or pull requests. Follow the established milestones and GitHub issue plan for structured development.

## License
This project is licensed under the MIT License.

## Acknowledgments
- **Dataset Authors**: Diego Tosato, Davide Dalle Pezze, Chiara Masiero, Gian Antonio Susto, Alessandro Beghi.
- Thanks to the industrial partners and research teams supporting the development of advanced AI solutions for smart manufacturing.
