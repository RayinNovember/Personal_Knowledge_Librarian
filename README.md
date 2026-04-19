# Knowledge Librarian

A personal knowledge librarian that reads any URL you give it, summarises the content using Claude, and helps you retrieve what you know when you need it.

## What it does

- Paste a URL (YouTube, Kaggle, or any website) → the app reads and summarises it
- Ask a question → it searches your saved sources and returns the most relevant ones
- Browse your full library filtered by domain

## Supported sources

| Source | How it's handled |
|--------|-----------------|
| YouTube | Scrapes video description |
| Kaggle | Scrapes notebook/competition/discussion content |
| Everything else | `trafilatura` extracts main article content |

## Setup

### 1. Clone / download the project

```bash
git clone <your-repo> knowledge-librarian
cd knowledge-librarian
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or create a `.env` file and load it before running.

### 4. Run locally

```bash
streamlit run app.py
```

Open http://localhost:8501

---

## Deploy to Streamlit Community Cloud (free, any device)

1. Push this folder to a GitHub repo
2. Go to https://share.streamlit.io
3. Connect your GitHub repo
4. Set `ANTHROPIC_API_KEY` in the Secrets section (Settings → Secrets):
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Deploy — you'll get a public URL accessible from any device

---

## Project structure

```
knowledge-librarian/
├── app.py                  # Streamlit UI
├── librarian.py            # Extractors, Claude summarization, search
├── requirements.txt        # Python dependencies
├── knowledge_index.json    # Your saved sources (auto-created)
└── README.md
```

## knowledge_index.json format

Each saved entry looks like this:

```json
{
  "id": "a1b2c3d4e5",
  "url": "https://...",
  "title": "Class Imbalance in ML – Towards Data Science",
  "summary": "Covers SMOTE, cost-sensitive learning, and threshold tuning for handling imbalanced datasets in binary classification.",
  "tags": ["SMOTE", "class imbalance", "oversampling", "precision-recall"],
  "key_concepts": ["resampling", "threshold tuning", "cost-sensitive learning"],
  "domain": "Machine Learning",
  "source_type": "web",
  "user_note": "good practical walkthrough",
  "date_saved": "2026-04-18T10:30:00"
}
```

## Notes

- The knowledge index is stored as a local JSON file. Back it up or commit it to your repo.
- For Streamlit Cloud deployment, the index resets on each redeploy. For persistent storage across devices, swap `knowledge_index.json` for a Supabase table (next phase).
- YouTube extraction relies on scraping the description from the page — quality depends on what the creator wrote.
