from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# import openai  # ❌ OLD: No longer using raw openai
import json
import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI  # ✅ NEW: Correct LangChain-compatible LLM

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

# openai.api_key = os.getenv("OPENAI_API_KEY")  # ❌ OLD: Raw OpenAI SDK

# === Load FAISS vectorstore ===
VECTOR_DIR = "../clients/poway/data"
embedding_model = OpenAIEmbeddings()
vectorstore = FAISS.load_local(
    VECTOR_DIR,
    embedding_model,
    allow_dangerous_deserialization=True
)

# === Initialize LangChain-compatible LLM ===
# llm = openai.ChatCompletion  # ❌ OLD: Not compatible with LangChain
llm = ChatOpenAI(  # ✅ NEW: LangChain-native LLM wrapper
    model_name="gpt-3.5-turbo",
    temperature=0.7, #More fluid and natural responses :D
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# === RAG Prompt Customization with Personality ===
prompt_template = PromptTemplate(
    input_variables=["context", "question", "client_name", "fallback_message"],
    template="""
You're Orryx — the AI assistant for the {client_name}.
You're helpful, clear, and just conversational enough to keep things human. Think: smart intern who actually likes their job.
You're smart, helpful, and a little witty (but not annoying about it). 
Think of yourself as the intern who always gets stuff done — but still roasts people in the group chat. UNDER NO CIRCUMSTANCES SHOULD YOU GO OVERBOARD
Always keep your tone warm, approachable, and human. Avoid sounding like a robot.\n\n
Use the info below to answer. Don’t make anything up. If you don't know, just say: "{fallback_message}".

Context:
{context}

Question:
{question}

Answer like you're explaining it to a sharp middle schooler. Straightforward, a bit casual, and easy to read.
Tone guide:
- Keep it real. Conversational, clear, and a little clever.
- A sprinkle of humor is cool — like you're in a good mood and had a solid iced coffee this morning.
- Don’t try too hard. No cringe. No dad jokes. Just be likable and useful.
- If its not necessary, don't try to be too funny. Only when it makes sense. Simple questions call for simpler answers, but still stay warm
"""
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    chain_type_kwargs={
        "prompt": prompt_template.partial(
            client_name=CLIENT_CONFIG["client_name"],
            fallback_message=CLIENT_CONFIG["fallback_message"]
        )
    }
)

class Message(BaseModel):
    message: str

@app.post("/chat")
async def chat(msg: Message):
    user_msg = msg.message

    # Optional system prompt for branding/personality (currently unused in RetrievalQA chain)
    system_prompt = f"""
    You are an AI assistant named Orryx, built for the {CLIENT_CONFIG['client_name']}.
    Your job is to answer user questions in a helpful, friendly, and accurate tone.
    Brand colors are {CLIENT_CONFIG['primary_color']} and {CLIENT_CONFIG['accent_color']}.
    If you don’t know the answer, use this fallback message:
    '{CLIENT_CONFIG['fallback_message']}'
    """

    try:
        # ❌ OLD: Raw GPT call
        # res = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": user_msg}
        #     ]
        # )
        # return {"reply": res['choices'][0]['message']['content']}

        # ✅ NEW: LangChain QA chain
        # 🔍 Debug: Test vectorstore retrieval
        docs = vectorstore.similarity_search(user_msg)
        print("\n🔍 Retrieved Docs:")
        for i, doc in enumerate(docs):
            print(f"--- Chunk {i+1} ---")
            print(doc.page_content[:300])
            print()

        response = qa_chain.run(user_msg)
        return {"reply": response}
    except Exception as e:
        return {"reply": f"{CLIENT_CONFIG['fallback_message']} (Error: {str(e)})"}
