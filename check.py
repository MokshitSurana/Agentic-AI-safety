from groq import Groq
import os

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)
for m in client.models.list().data:
    print(m.id)
