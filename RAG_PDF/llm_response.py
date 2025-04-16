from dotenv import load_dotenv
load_dotenv()
import os
import openai

openai_api_key = os.getenv("OPENAI_API_KEY")

def generate_llm_response(prompt, openai_api_key= openai_api_key, model_name="gpt-3.5-turbo"):
    if openai_api_key:
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

if __name__ == "__main__":
    prompt = "What is the purpose of the equipment manual?"
    print(generate_llm_response(prompt, openai_api_key=openai_api_key))