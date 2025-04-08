"""
agent.py
---------
This script implements an LLM-based interactive agent for predictive maintenance tasks.
The agent uses LangChain to process user commands and then calls the appropriate function
from toolbox.py (for anomaly detection or forecasting).

To switch between local Ollama and GPT API:
  - Set LLM_PROVIDER = "ollama" for local usage
  - Set LLM_PROVIDER = "gpt" to use the OpenAI GPT API (ensure you have set your API key)

Requirements:
    pip install langchain langchain-ollama
    (or pip install openai if using GPT API)
"""

from langchain_ollama.llms import OllamaLLM
# Uncomment the following if you want to use the OpenAI GPT API:
# from langchain.llms import OpenAI
from langchain_core.prompts import ChatPromptTemplate

# Import toolbox functions
from toolbox import load_dataset, run_anomaly_detection, run_forecasting

# Set your LLM provider: either "ollama" or "gpt"
LLM_PROVIDER = "ollama"  # Change to "gpt" if you want to use GPT API

if LLM_PROVIDER == "gpt":
    # Replace with your actual OpenAI GPT API key
    model = OpenAI(openai_api_key="YOUR_API_KEY")
else:
    model = OllamaLLM(model="llama3.2")

# Define a prompt template that instructs the LLM to interpret user commands
template = """
You are an expert assistant in predictive maintenance analytics.
User command: {user_input}

Based on the command, identify if the user wants to run anomaly detection or forecasting.
Return an analysis message containing one of the keywords: "anomaly" or "forecast".
If additional details (like dataset path or machine serial) are mentioned, include them in your analysis.
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

def main():
    print("Welcome to the Predictive Maintenance Agent!")
    print("This agent accepts commands to run anomaly detection or forecasting workflows.")
    print("You can switch between local Ollama or GPT API by changing the LLM_PROVIDER flag in agent.py\n")
    
    while True:
        print("\n---------------------")
        user_input = input("Enter your command (or 'q' to quit): ").strip()
        if user_input.lower() == 'q':
            break
        
        # Process user input with LLM to extract task instructions.
        llm_analysis = chain.invoke({"user_input": user_input})
        print("LLM analysis output:", llm_analysis)
        
        # A simple example to decide which task to run based on the LLM output.
        # In a robust system you might parse JSON or use stricter NLP.
        if "anomaly" in llm_analysis.lower():
            dataset_path = input("Enter the dataset path for anomaly detection (.csv or .zip): ").strip()
            machine_input = input("Enter the machine serial (or press Enter for default): ").strip()
            machine_serial = int(machine_input) if machine_input else None
            df = load_dataset(dataset_path)
            if df is not None:
                run_anomaly_detection(df, machine_serial=machine_serial)
            else:
                print("Failed to load the dataset.")
        elif "forecast" in llm_analysis.lower():
            dataset_path = input("Enter the dataset path for forecasting (.csv or .zip): ").strip()
            df = load_dataset(dataset_path)
            if df is not None:
                run_forecasting(df)
            else:
                print("Failed to load the dataset.")
        else:
            print("LLM did not clearly specify the task. Please include 'anomaly' or 'forecast' in your command.")
    
    print("Exiting agent. Goodbye!")

if __name__ == "__main__":
    main()
