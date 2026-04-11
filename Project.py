from google import genai
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()


file_path = '/Users/fatahibrahim/Library/Mobile Documents/com~apple~CloudDocs/Hackathon/healthcare_real_time_dataset.csv'
df = pd.read_csv(file_path)

dataset_context = df.head(15).to_string()


def make_client():
  api_key = os.getenv("API_Key")
  if not api_key:
    print("Warning: API_Key not set; API client will be unavailable.")
    return None
  return genai.Client(api_key=api_key)


def run_interactive(client):
  """Run a simple interactive loop. Type 'quit' to exit."""
  while True:
    user_input = input("Enter a prompt (or type quit to quit): ").strip()
    if user_input.lower() == "quit":
      print("Exiting.")
      break
    if user_input == "":
      # ignore empty input and continue
      continue

    prompt = (
      f"Use this dataset as context:{dataset_context}\n\nUser Question:{user_input}\n"
      "Response should be concise and straight to the point"
    )

    if client is None:
      # In environments without the API key, print the prompt instead of calling the API
      print("API client unavailable. Prompt to send:\n", prompt)
      continue

    response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
    # response shape may vary; prefer .text if available
    print(response.text)


client = make_client()
run_interactive(client)






