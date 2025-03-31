Orryx is a modular, white-labeled AI assistant designed for Chambers of Commerce, local organizations, and community-based institutions. It enables these groups to provide real-time, branded, and intelligent assistance to site visitors, members, and prospective clients—all with minimal setup.

---

## 🧠 Core Features

- 🔁 **Modular Deployment** – Each client has a unique config and data set
- 🧩 **GPT-4 Turbo Powered** – High-quality, conversational responses
- 📄 **Document Ingestion** – Load PDFs and scraped site content into memory
- 🎨 **Custom Branding** – Light-mode chat widget themed per client
- 📦 **One-Line Embed** – Easily deploy the assistant to any website
- 🧭 **Fallback to Human** – Redirect users to real staff if needed
- 🌐 **API-Driven Backend** – Built using FastAPI and Supabase for vector search

---

## 📂 Project Structure

```
orryx/
├── frontend/              # React chat UI (light mode, embedded)
│   ├── components/
│   ├── config/            # Loads client theme and settings
│   ├── public/
│   └── App.jsx
│
├── backend/               # FastAPI backend for chat + search
│   ├── routes/
│   ├── utils/
│   ├── orryx_config.py    # Loads client-specific config
│   └── main.py
│
├── clients/
│   ├── poway/
│   │   ├── data/          # PDFs and scraped site content
│   │   └── config.json    # Brand, greeting, fallback, contact
│   └── [client-name]/     # Duplicate this for other orgs
│
├── scripts/               # Setup scripts
│   ├── ingest_pdf.py      # Vectorizes PDF content
│   ├── crawl_site.py      # Scrapes + cleans HTML
│   └── build_client.py    # Automates client onboarding
│
├── supabase/              # Vector DB utils
├── .env                   # API keys (OpenAI, Supabase)
└── README.md              # Setup guide
```

---

## 🚀 Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/devaSas1/orryx.git
cd orryx
```

### 2. Set Up Virtual Environment (Python Backend)
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Add Your API Keys
Create a `.env` file at the root:
```bash
OPENAI_API_KEY=your-key-here
```

### 4. Run the Backend
```bash
cd backend
uvicorn main:app --reload
```

Test it at: `http://127.0.0.1:8000/docs`

### 5. Add Client Data
- Place PDFs in `clients/clientname/data/`
- Edit `config.json` with brand colors, greeting, fallback, contact info

---

## 💼 License
MIT License — free to use, modify, and deploy. For commercial licensing or support, contact [devaSas1](https://github.com/devaSas1).

---

## Made by Deva :D
