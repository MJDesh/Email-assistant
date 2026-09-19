# AI Email Inbox Assistant — Hackathon Starter

## Setup (do this first, everyone)

```bash
cd inbox-assistant
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# then edit .env and paste your Gemini API key (get one free at aistudio.google.com)
```

Run the app:
```bash
streamlit run main.py
```

## What's already built

- `schemas.py` — Pydantic models for emails and LLM output (analysis + draft reply)
- `llm_logic.py` — Gemini API calls, structured JSON output, two functions:
  `analyze_email()` and `draft_reply()`
- `data/emails.json` — 8 realistic mock emails (urgent outage, contract pricing,
  frustrated client, newsletter, scheduling confirmation, budget request) covering
  a good spread for demoing
- `main.py` — working Streamlit app: inbox list, email detail view, analysis panel,
  draft reply with confidence scoring, and an **Inbox Health Score** in the sidebar

## Already-included differentiator features

1. **Inbox Health Score** (sidebar) — aggregates urgency/frustration/open tasks
   across analyzed emails into one score. Click "Analyze all emails" to populate it.
2. **Reply confidence + human-review flag** — every draft reply comes with a
   confidence level (High/Medium/Low) and a reason, so the tool knows when
   NOT to auto-send (e.g. pricing, commitments, emotionally charged replies).

## Where to go next (suggested split)

- **Person 1 (LLM):** tune prompts in `llm_logic.py`, test edge cases (very short
  emails, multi-language, sarcasm), maybe add thread-context stitching using
  `thread_id` in emails.json
- **Person 2 (LLM/data):** expand `data/emails.json` with more variety, and/or
  build the thread-summary feature (combine e1 + e8, which share `thread_id`)
- **Person 3 (UI):** polish `main.py` — better priority color styling, maybe a
  card layout instead of buttons for the inbox list
- **Person 4 (UI):** add the deadline timeline view (new tab/section — collect
  all `Task.deadline` values across analyzed emails and show on a simple chart
  or sorted list)
- **Person 5 (data + demo):** stress-test the flow end-to-end, prepare the pitch,
  make sure the demo emails tell a clear "before/after" story

## Notes

- Analysis and drafts are cached in `st.session_state` so you don't burn API
  calls re-analyzing the same email on every rerun.
- If you hit Gemini free-tier rate limits during dev, stagger testing across
  teammates or add a short `time.sleep()` between calls in a loop.
- The `thread_id` field in emails.json lets you group e1 (initial outage report)
  and e8 (follow-up) — useful if you build thread-level context/summaries.
