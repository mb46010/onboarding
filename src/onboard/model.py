from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter
from dotenv import load_dotenv

load_dotenv()

rate_limiter = InMemoryRateLimiter(
    requests_per_second=4,  # <-- Can only make 4 requests per second
    check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=10,  # Controls the maximum burst size.
)
def get_default_llm():
    from onboard.tracing import get_langfuse_callback
    langfuse_handler = get_langfuse_callback()
    callbacks = [langfuse_handler] if langfuse_handler else []
    
    llm = init_chat_model(
        model="gpt-4o", 
        temperature=0.0,
        max_tokens=1000,
        max_retries=3,
        rate_limiter=rate_limiter,
        callbacks=callbacks
    )
    return llm