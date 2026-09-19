"""
All Gemini API calls live here. Keeping this separate from the Streamlit
UI means the UI person and the LLM person can both work without stepping
on each other's files.
"""

import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas import (
    Email,
    EmailAnalysis,
    DraftReply,
    InboxAnswer,
)


# ---------- Gemini setup ----------

load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

MODEL = "gemini-3.5-flash-lite"


# ---------- Email analysis ----------

def analyze_email(
    email: Email,
    thread_context: str = ""
) -> EmailAnalysis:
    """
    Summarize, prioritize, extract tasks/deadlines, and gauge sentiment
    for a single email (optionally with earlier thread context).
    """

    prompt = f"""You are an AI email assistant. Analyze the following email and return
a structured analysis.

{f"Earlier thread context:\n{thread_context}\n" if thread_context else ""}

Email to analyze:
From: {email.sender_name} <{email.sender_email}>
Subject: {email.subject}
Body:
{email.body}

Instructions:
- summary: 2-3 sentences capturing what this email is about and what
  (if anything) it needs from the recipient.
- priority: Urgent (needs action today), High (needs action this week),
  Normal, or Low.
- priority_reason: one sentence justifying the priority.
- tasks: extract any concrete action items and their deadlines, if mentioned.
  Empty list if none.
- sentiment: the emotional tone of the SENDER.
- suggested_tone: the tone a reply should use, based on sender relationship
  and content.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EmailAnalysis,
        ),
    )

    return EmailAnalysis.model_validate(
        json.loads(response.text)
    )


# ---------- Reply drafting ----------

def draft_reply(
    email: Email,
    analysis: EmailAnalysis,
    thread_context: str = ""
) -> DraftReply:
    """
    Draft a reply to an email, using the prior analysis
    (tone, tasks) as guidance, and flag whether it is safe
    to send with minimal review.
    """

    prompt = f"""You are drafting an email reply on behalf of the recipient.

{f"Earlier thread context:\n{thread_context}\n" if thread_context else ""}

Original email:
From: {email.sender_name} <{email.sender_email}>
Subject: {email.subject}
Body:
{email.body}

Context from analysis:
- Priority: {analysis.priority}
- Suggested tone: {analysis.suggested_tone}
- Open tasks: {[t.description for t in analysis.tasks]}

Instructions:
- Write a complete, ready-to-send reply in the suggested tone.
  Keep it concise and natural.
- Do NOT invent specific facts, prices, or commitments the original
  email didn't provide enough info for.
- confidence: how safe is this draft to send with little/no editing?
  - "High": routine acknowledgment, no commitments made.
  - "Medium": reasonable draft but involves scheduling, dates, or mild
    commitments worth a glance.
  - "Low": involves pricing, contractual language, sensitive/emotional
    content, or firm commitments — a human MUST review.
- needs_human_review: true unless confidence is "High".
- confidence_reason: one sentence explaining why.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DraftReply,
        ),
    )

    return DraftReply.model_validate(
        json.loads(response.text)
    )


# ---------- Ask My Inbox ----------

def answer_inbox_question(
    question: str,
    emails: list[Email]
) -> InboxAnswer:
    """
    Answer a user's question using the provided emails.

    The model is instructed to use ONLY the supplied email context
    and return supporting source emails.
    """

    context = "\n\n".join(
        f"""
EMAIL ID: {email.id}
FROM: {email.sender_name} <{email.sender_email}>
DATE: {email.timestamp}
SUBJECT: {email.subject}
BODY:
{email.body}
"""
        for email in emails
    )

    prompt = f"""
You are an AI assistant answering questions about a user's email inbox.

Answer the user's question using ONLY the email context provided below.

IMPORTANT RULES:
- Do not use outside knowledge.
- Do not invent facts, dates, names, or commitments.
- If the answer cannot be found in the provided emails, say:
  "I couldn't find that information in your inbox."
- Only include source emails that actually support your answer.
- Use the EMAIL ID provided in the context when identifying sources.
- Keep the answer concise but useful.

User question:
{question}

Email context:
{context}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InboxAnswer,
        ),
    )

    return InboxAnswer.model_validate(
        json.loads(response.text)
    )