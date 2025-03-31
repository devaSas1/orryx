from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# === Allow frontend to talk to this ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Load Poway config ===
with open("../clients/poway/config.json") as f:
    CLIENT_CONFIG = json.load(f)

openai.api_key = os.getenv("OPENAI_API_KEY")

class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(msg: Message):
    user_msg = msg.message

    system_prompt = f"""
    You are an AI assistant named Orryx, built for the {CLIENT_CONFIG['client_name']}.
    Your job is to answer user questions in a helpful, friendly, and accurate tone.
    Brand colors are {CLIENT_CONFIG['primary_color']} and {CLIENT_CONFIG['accent_color']}.
    If you don’t know the answer, use this fallback message:
    '{CLIENT_CONFIG['fallback_message']}'
    """

    try:
        res = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]
        )
        return {"reply": res['choices'][0]['message']['content']}
    except Exception as e:
        return {"reply": f"{CLIENT_CONFIG['fallback_message']} (Error: {str(e)})"}
