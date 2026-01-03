import os
from langfuse.langchain import CallbackHandler
from langfuse import observe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_langfuse_callback():
    """Initializes and returns a Langfuse callback handler if credentials are set."""
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if public_key and secret_key:
        # In Langfuse 3.x, CallbackHandler for Langchain picks up 
        # credentials from environment variables automatically.
        return CallbackHandler()
    return None
