from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
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

"""
# === Load Poway config ===
with open("../clients/poway/config.json") as f:
    CLIENT_CONFIG = json.load(f)
"""

# openai.api_key = os.getenv("OPENAI_API_KEY")  # ❌ OLD: Raw OpenAI SDK

# === Load FAISS vectorstore ===
VECTOR_DIR = "../clients/poway/data"
embedding_model = OpenAIEmbeddings()
#vectorstore = FAISS.load_local(
#    VECTOR_DIR,
#    embedding_model,
#    allow_dangerous_deserialization=True
#)


import json
from langchain.schema import Document
from langchain.vectorstores import FAISS  # ✅ still using FAISS for retrieval

# 🔁 Caches vectorstores per client
VECTOR_CACHE = {}

def load_dynamic_knowledge_base(raw_data):
    docs = []
    for item in raw_data:
        question = item.get("question", "")
        answer = item.get("answer", "")
        if question and answer:
            combined = f"{question} {answer}"
            docs.append(Document(page_content=combined))
    return docs
"""

# OLD DYNAMIC KNOWLEDGE BASE FUNCTION
def load_dynamic_knowledge_base(path):
    with open(path, "r", encoding="utf-8") as f:
        print("🔍 Raw JSON content:", f.read())  # NEW
        f.seek(0)  # Reset file pointer for json.load()
        data = json.load(f)

    docs = []
    for item in data:
        question = item.get("question", "")
        answer = item.get("answer", "")
        if question and answer:
            combined = f"{question} {answer}"
            docs.append(Document(page_content=combined))
    return docs

    
"""



"""
# OLD. IGNORE THIS
documents = load_dynamic_knowledge_base("../clients/poway/data/poway_knowledge_base_structured.json")

for i, doc in enumerate(documents):
    print(f"Doc {i+1} content:", doc.page_content[:200])  # Preview first 200 chars

vectorstore = FAISS.from_documents(documents, embedding_model)

"""


# === Initialize LangChain-compatible LLM ===
# llm = openai.ChatCompletion  # ❌ OLD: Not compatible with LangChain
llm = ChatOpenAI(  # ✅ NEW: LangChain-native LLM wrapper
    model_name="gpt-3.5-turbo",
    temperature=0.4, #More fluid and natural responses :D
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


class Message(BaseModel):
    message: str

@app.post("/chat/{client_id}")
async def chat(client_id: str, msg: Message):
    user_msg = msg.message

    # Optional system prompt for branding/personality (currently unused in RetrievalQA chain)
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
            print(f"🔧 Generating new vectorstore for '{client_id}'")
            documents = load_dynamic_knowledge_base(raw_data)
            VECTOR_CACHE[client_id] = FAISS.from_documents(documents, OpenAIEmbeddings())
        vectorstore = VECTOR_CACHE[client_id]

        # === QA Chain setup ===
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

        # 🔍 Optional debug
        docs = vectorstore.similarity_search(user_msg)
        print(f"\n🔍 Retrieved Docs for '{client_id}':")
        for i, doc in enumerate(docs):
            print(f"--- Chunk {i+1} ---\n{doc.page_content[:300]}\n")

        response = qa_chain.run(user_msg)
        return {"reply": response}

    except Exception as e:
        return {"reply": f"{client_config.get('fallback_message', 'Something went wrong.')} (Error: {str(e)})"}