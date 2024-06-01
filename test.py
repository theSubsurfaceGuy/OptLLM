from openai import OpenAI
import json
import os

def load_config():
    with open('config.json', 'r') as file:
        return json.load(file)

def test_openai_connection(api_key):
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[{"role": "user", "content": "Hello, how are you what version of GPT you are, do you know linear programming? what is the general form of an LP"}]
        )
        print("Response from OpenAI:", response.choices[0].message.content)
    
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    config = load_config()
    test_openai_connection(config["openai_api_key"])
