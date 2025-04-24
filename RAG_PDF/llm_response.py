from dotenv import load_dotenv
load_dotenv()
import os
import openai
import requests

openai_api_key = os.getenv("OPENAI_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")  # fixed typo from DEEPEEK

def generate_llm_response(prompt, model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, deepseek_api_key=deepseek_api_key):
    if model_name.startswith("gpt"):
        openai.api_key = openai_api_key
        client = openai.OpenAI(api_key=openai_api_key)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains equipment installation steps using retrieved manual content. Include any referenced images when helpful."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

    elif model_name.startswith("deepseek"):
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that explains equipment installation steps using retrieved manual content. Include any referenced images when helpful."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    else:
        raise ValueError(f"Unsupported model: {model_name}")
