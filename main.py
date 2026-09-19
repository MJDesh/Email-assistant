"""
AI Email Inbox Assistant — Streamlit app.
Run with: streamlit run main.py
"""

import json
import streamlit as st
from schemas import Email
from llm_logic import analyze_email, draft_reply, answer_inbox_question

st.set_page_config(page_title="AI Inbox Assistant", layout="wide")


# ---------- Data loading ----------

@st.cache_data
def load_emails():
    with open("data/emails.json") as f:
        raw = json.load(f)
    return [Email.model_validate(e) for e in raw]


emails = load_emails()

# session cache so we don't re-call the LLM every rerun
if "analysis_cache" not in st.session_state:
    st.session_state.analysis_cache = {}
if "draft_cache" not in st.session_state:
    st.session_state.draft_cache = {}


def get_analysis(email: Email):
    if email.id not in st.session_state.analysis_cache:
        with st.spinner("Analyzing email..."):
            st.session_state.analysis_cache[email.id] = analyze_email(email)
    return st.session_state.analysis_cache[email.id]


def get_draft(email: Email, analysis):
    if email.id not in st.session_state.draft_cache:
        with st.spinner("Drafting reply..."):
            st.session_state.draft_cache[email.id] = draft_reply(email, analysis)
    return st.session_state.draft_cache[email.id]


PRIORITY_COLOR = {
    "Urgent": "🔴",
    "High": "🟠",
    "Normal": "🟢",
    "Low": "⚪",
}

CONFIDENCE_COLOR = {
    "High": "🟢",
    "Medium": "🟡",
    "Low": "🔴",
}


# ---------- Sidebar: Inbox Health Score ----------

st.sidebar.title("📊 Inbox Health")

if st.sidebar.button("Analyze all emails", use_container_width=True):
    for e in emails:
        get_analysis(e)

analyzed = [st.session_state.analysis_cache[e.id] for e in emails if e.id in st.session_state.analysis_cache]

if analyzed:
    urgent_count = sum(1 for a in analyzed if a.priority == "Urgent")
    high_count = sum(1 for a in analyzed if a.priority == "High")
    total_tasks = sum(len(a.tasks) for a in analyzed)
    frustrated_count = sum(1 for a in analyzed if a.sentiment in ("Frustrated", "Urgent/Stressed"))

    # simple health score: starts at 100, deducted for each stressor
    score = 100 - (urgent_count * 20) - (high_count * 10) - (frustrated_count * 10)
    score = max(score, 0)

    st.sidebar.metric("Inbox Health Score", f"{score}/100")
    st.sidebar.write(f"🔴 Urgent: {urgent_count}")
    st.sidebar.write(f"🟠 High priority: {high_count}")
    st.sidebar.write(f"😤 Frustrated senders: {frustrated_count}")
    st.sidebar.write(f"📋 Open tasks: {total_tasks}")
else:
    st.sidebar.caption("Click 'Analyze all emails' to see your inbox health score.")

st.sidebar.divider()
st.sidebar.caption(f"{len(emails)} emails in inbox • analyzed {len(analyzed)}")


# ---------- Main layout ----------

st.title("📬 AI Email Inbox Assistant")

# ---------- Ask My Inbox ----------

st.subheader("🔎 Ask My Inbox")
st.caption("Ask a question about anything in your inbox.")

question = st.text_input(
    "What would you like to know?",
    placeholder="e.g. What are my upcoming deadlines?"
)

if st.button("Ask", key="ask_inbox_btn", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching your inbox..."):
            result = answer_inbox_question(question, emails)

        st.markdown("### 💬 Answer")
        st.write(result.answer)

        if result.sources:
            st.markdown("### 📧 Sources")

            for source in result.sources:
                st.markdown(
                    f"**{source.subject}**  \n"
                    f"{source.sender} · `{source.email_id}`"
                )
        else:
            st.caption("No supporting emails found.")

st.divider()

col_list, col_detail = st.columns([1, 2])

with col_list:
    st.subheader("Inbox")
    selected_id = st.session_state.get("selected_id", emails[0].id)

    for e in emails:
        cached = st.session_state.analysis_cache.get(e.id)
        badge = PRIORITY_COLOR.get(cached.priority, "⬜") if cached else "⬜"
        label = f"{badge} **{e.subject}**\n\n{e.sender_name} · {e.timestamp[:10]}"
        if st.button(label, key=f"select_{e.id}", use_container_width=True):
            st.session_state.selected_id = e.id
            selected_id = e.id

selected_email = next(e for e in emails if e.id == selected_id)

with col_detail:
    st.subheader(selected_email.subject)
    st.caption(f"From: {selected_email.sender_name} <{selected_email.sender_email}> · {selected_email.timestamp}")
    st.write(selected_email.body)

    st.divider()

    if st.button("🔍 Analyze this email", key="analyze_btn"):
        st.session_state.analysis_cache.pop(selected_email.id, None)  # force refresh
        get_analysis(selected_email)

    analysis = st.session_state.analysis_cache.get(selected_email.id)

    if analysis:
        p1, p2, p3 = st.columns(3)
        p1.metric("Priority", f"{PRIORITY_COLOR[analysis.priority]} {analysis.priority}")
        p2.metric("Sentiment", analysis.sentiment)
        p3.metric("Suggested tone", analysis.suggested_tone)

        st.markdown(f"**Summary:** {analysis.summary}")
        st.caption(f"Why this priority: {analysis.priority_reason}")

        if analysis.tasks:
            st.markdown("**📋 Extracted tasks:**")
            for t in analysis.tasks:
                deadline_str = f" — *due {t.deadline}*" if t.deadline else ""
                st.write(f"- {t.description}{deadline_str}")
        else:
            st.caption("No action items detected.")

        st.divider()

        if st.button("✍️ Draft a reply", key="draft_btn"):
            st.session_state.draft_cache.pop(selected_email.id, None)
            get_draft(selected_email, analysis)

        draft = st.session_state.draft_cache.get(selected_email.id)
        if draft:
            st.markdown("**Suggested reply:**")
            st.text_area("Draft", draft.reply_text, height=180, key=f"draft_text_{selected_email.id}")

            conf_badge = CONFIDENCE_COLOR[draft.confidence]
            st.write(f"{conf_badge} **Confidence: {draft.confidence}** — {draft.confidence_reason}")
            if draft.needs_human_review:
                st.warning("⚠️ This draft needs your review before sending.")
            else:
                st.success("✅ Safe to send with minimal edits.")
    else:
        st.info("Click 'Analyze this email' to generate a summary, priority, tasks, and sentiment.")
