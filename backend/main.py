from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import os
from dotenv import load_dotenv

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain_openai import ChatOpenAI

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

# === Vectorstore Cache ===
VECTOR_CACHE = {}
embedding_model = OpenAIEmbeddings()

def load_dynamic_knowledge_base(raw_data):
    docs = []
    for item in raw_data:
        question = item.get("question", "")
        answer = item.get("answer", "")
        if question and answer:
            combined = f"{question} {answer}"
            docs.append(Document(page_content=combined))
    return docs

# === Prompt template ===
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

# === Models ===
class Message(BaseModel):
    message: str

# 🆕 ADDED: Model for issue reports
class IssueReport(BaseModel):
    user_message: str = Field(..., description="The original user message")
    bot_reply: str = Field(..., description="The chatbot's response")
    comment: str = Field("", description="User-added context or note")


# 🆕 ADDED: Report endpoint to log bad bot replies
@app.post("/report")
async def report_issue(report: IssueReport):
    timestamp = datetime.utcnow().isoformat()
    report_entry = {
        "timestamp": timestamp,
        "user_message": report.user_message,
        "bot_reply": report.bot_reply,
        "comment": report.comment
    }

    report_path = "../clients/poway/data/reports.json"
    try:
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = []

        existing.append(report_entry)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

        print(f"✅ Issue logged at {timestamp}")
        return {"status": "success", "message": "Report saved."}
    except Exception as e:
        print(f"❌ Report failed: {e}")
        return {"status": "error", "message": str(e)}


# ✅ Chat endpoint
@app.post("/chat/{client_id}")
async def chat(client_id: str, msg: Message):
    user_msg = msg.message

    try:
        # === Dynamic paths ===
        client_dir = f"../clients/{client_id}"
        config_path = os.path.join(client_dir, "config.json")
        kb_path = os.path.join(client_dir, "data", f"{client_id}_knowledge_base_structured.json")

        with open(config_path, "r") as f:
            client_config = json.load(f)

        with open(kb_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # === Vectorstore cache ===
        if client_id not in VECTOR_CACHE:
            print(f"🔧 Building vectorstore for '{client_id}'")
            documents = load_dynamic_knowledge_base(raw_data)
            VECTOR_CACHE[client_id] = FAISS.from_documents(documents, OpenAIEmbeddings())
        vectorstore = VECTOR_CACHE[client_id]

        # === QA chain setup ===
        qa_chain = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.4,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            ),
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={
                "prompt": prompt_template.partial(
                    client_name=client_config["client_name"],
                    fallback_message=client_config["fallback_message"]
                )
            }
        )

        # Optional preview
        docs = vectorstore.similarity_search(user_msg)
        print(f"\n🔍 Retrieved Docs for '{client_id}':")
        for i, doc in enumerate(docs):
            print(f"--- Chunk {i+1} ---\n{doc.page_content[:300]}\n")

        response = qa_chain.run(user_msg)
        return {"reply": response}

    except Exception as e:
        return {
            "reply": f"{client_config.get('fallback_message', 'Something went wrong.')}\n(Error: {str(e)})"
        }
