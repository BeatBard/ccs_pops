import os
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Get the directory where this script is located
script_dir = Path(__file__).parent
parent_dir = script_dir.parent

# Load environment variables from parent directory
load_dotenv(dotenv_path=parent_dir / ".env")

# Set Google credentials from environment
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path:
    # If path is relative, make it absolute relative to parent directory
    if not os.path.isabs(credentials_path):
        credentials_path = str(parent_dir / credentials_path)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Initialize client
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_PROJECT_ID"),
    location="global"
)

model = "gemini-3-flash-preview"

def chat(user_message: str) -> str:
    """Send a message and get response from Gemini"""
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_message)],
        ),
    ]

    try:
        response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents
        ):
            response += chunk.text
        return response
    except Exception as e:
        return f"Error: {e}"


def main():
    """Interactive chatbot loop"""
    print("=" * 50)
    print("🤖 Gemini Chatbot - Type 'quit' to exit")
    print("=" * 50)

    while True:
        # Get user input
        user_input = input("\nYou: ").strip()

        # Exit condition
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nGoodbye! 👋")
            break

        # Skip empty input
        if not user_input:
            continue

        # Get and print response
        print("\nBot: ", end="", flush=True)
        response = chat(user_input)
        print(response)


if __name__ == "__main__":
    main()
