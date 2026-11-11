# FoodBot

Ask for a restaurant the way you’d ask a friend — and get ranked places back.

> “Quiet Italian for a date in Toronto, vegetarian options welcome.”

FoodBot is a local AI restaurant search app.


---

## What you get

- **Natural-language search** — cuisine, mood, diet, occasion; not just keywords
- **In-app chatbot** — same engine, conversational replies with pick lists
- **Filters that matter** — location (Canadian cities), price, vibe, and how results are ranked
- **Scores like people use them** — match quality shown as ★ on a 0–5 scale
- **A short walk-in intro** — entrance → dining → kitchen (skip anytime; respects reduced motion)

Sample data covers places across **Toronto, Vancouver, Montreal, Calgary, Ottawa, Edmonton, Quebec City, Winnipeg, Halifax, and Victoria**. Swap in the real Yelp Open Dataset when you want a bigger catalog.

---

## How it works (plain English)

1. **Understand the ask** — optional LLM, otherwise a solid rule-based parser (cuisine, quiet, vegetarian, city, price…)
2. **Find candidates two ways** — meaning-based search (embeddings + FAISS) and word-based search (BM25)
3. **Nudge with filters** — city, price, quiet / date night / vegetarian (soft filters so good places don’t vanish)
4. **Blend & re-rank** — hybrid scores, then LightGBM LambdaRank for the final order
5. **Measure** — Recall@10 and NDCG@10 so you can compare methods

Under the hood: Python, Sentence-Transformers, FAISS, BM25, LightGBM, FastAPI, and a Motion-powered web UI.

---

## Quick start

```bash
cd "AI-Powered Restaurant Search & Recommendation Engine"

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Sample data → search indexes → ranking model → metrics
python scripts/prepare_data.py
python scripts/build_indexes.py
python scripts/train_ltr.py
python scripts/evaluate.py

# Start the app
./scripts/run_web.sh
# or: uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

Then open **http://127.0.0.1:8000**.

If you’re on macOS and imports hang, keep thread limits low (the run script already does this):

```bash
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
```

Or with Make:

```bash
make setup && make all && make web
```

---

## Try it

In the search box:

- Quiet Italian for a date with vegetarian options  
- Best sushi for a romantic dinner in Vancouver  
- Cheap spicy vegetarian Indian food  

Or tap **Chat** and ask the same way you’d text someone.

Use **Location**, **Price**, **Vibe**, and **Rank by** to narrow or reorder results without rewriting the whole query.

---

## Optional: real Yelp data

1. Download the [Yelp Open Dataset](https://business.yelp.com/data/resources/open-dataset/).
2. Drop these into `data/raw/`:
   - `yelp_academic_dataset_business.json`
   - `yelp_academic_dataset_review.json`
3. Rebuild:

```bash
python scripts/prepare_data.py
python scripts/build_indexes.py
python scripts/train_ltr.py
```

Until then, a **30-restaurant Canadian sample** (Yelp-like schema) is generated for you.

---

## Optional: smarter query parsing

Copy `.env.example` → `.env` and set `OPENAI_API_KEY`.

No key? FoodBot still works — it falls back to deterministic rules. With a key, chat replies and query understanding can get a bit warmer and more flexible.

---

## Project layout

```
web/                  FoodBot UI (search, filters, chat, walk intro)
src/
  api/                FastAPI + /search + /chat
  data/               Load & clean restaurant docs
  llm/                Query parser
  retrieval/          Embeddings, FAISS, BM25, hybrid, filters
  ranking/            LightGBM features + model
  evaluation/         Recall@K, NDCG@K, judgments
scripts/              prepare → index → train → evaluate → run_web
notebooks/            Step-by-step Jupyter walkthrough
data/                 sample · processed · indexes
models/               trained LTR model
```

---

## API

| Endpoint | What it does |
|----------|----------------|
| `GET /` | FoodBot web app |
| `GET /health` | Is the engine loaded? |
| `POST /search` | Ranked restaurants for a query (+ city / price / vibe / sort) |
| `POST /chat` | Conversational reply + picks |
| `GET /docs` | Interactive Swagger docs |

Example search body:

```json
{
  "query": "quiet Italian for a date",
  "city": "Toronto",
  "price_max": 3,
  "vibe": "romantic",
  "sort_by": "match",
  "top_k": 10
}
```

---

## Built for learning (and for dinner plans)

This project is meant to be readable end-to-end: data prep, retrieval, ranking, eval, and a real UI. Use the notebooks to walk the pipeline, poke the API at `/docs`, or just open the app and find somewhere good to eat.
