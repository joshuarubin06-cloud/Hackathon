from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_Key")
client = genai.Client(api_key=api_key)

user_input = input("Enter a prompt: ")

prompt = f'{user_input}'

response = client.models.generate_content(model= "gemini-3-flash-preview", contents=prompt)

