import dotenv
import fastapi
import os

from anthropic import Anthropic


dotenv.load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

app = fastapi.FastAPI()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ask")
def ask(question: str):
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        model=ANTHROPIC_MODEL,
    )
    return {"response": message.content}
