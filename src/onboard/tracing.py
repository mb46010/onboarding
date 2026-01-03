import os
from langfuse.callback import CallbackHandler
from langfuse.decorators import observe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_langfuse_callback():
    """Initializes and returns a Langfuse callback handler if credentials are set."""
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if public_key and secret_key:
        return CallbackHandler(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
    return None
