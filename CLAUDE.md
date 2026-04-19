# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
streamlit run app.py
```

Requires `ANTHROPIC_API_KEY` set as an environment variable (or in a `.env` file loaded before running).

## Installing dependencies

```bash
pip install -r requirements.txt
```

## Architecture

The app has two layers:

**[librarian.py](librarian.py)** — all backend logic, no UI:
- `process_url(url, domain, user_note)` — full pipeline: detect source → extract content → summarize via Claude → append to `knowledge_index.json`
- `search_index(query, domain, source_type)` — keyword scoring search across title, summary, tags, key_concepts, user_note (tags/key_concepts score 3×, title 2×, anywhere 1×)
- Three extractors: `extract_youtube` (scrapes og:description + JSON blob), `extract_kaggle` (scrapes meta + paragraph text), `extract_generic` (trafilatura main content)
- `summarize_with_claude` calls `claude-sonnet-4-6`, expects JSON back with title/summary/tags/domain/key_concepts
- SSL certs are set via `certifi` at module load time (required for Windows corporate environments)

**[app.py](app.py)** — Streamlit UI only, imports from `librarian.py`:
- Left column: add URL form → calls `process_url`
- Right column: search form → calls `search_index`
- Bottom: full library browser sorted by `date_saved` descending

**[knowledge_index.json](knowledge_index.json)** — flat JSON array, auto-created on first save. Each entry has: `id` (MD5 of URL, 10 chars), `url`, `title`, `summary`, `tags`, `key_concepts`, `domain`, `source_type`, `user_note`, `date_saved`.

`main.py` is a stub and is not used by the app.

## Domain taxonomy

The Claude prompt and UI dropdowns share a fixed domain list: `Power BI`, `Microsoft Fabric`, `Machine Learning`, `Survival Analysis`, `Causal Inference`, `Time Series`, `Deep Learning`, `Interpretable ML`, `A/B Testing`, `Statistics`, `R`, `General`. Keep these in sync between [librarian.py:246](librarian.py#L246) and [app.py:215-222](app.py#L215-L222) when adding new domains.
