import re
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from memory.corrections import get_relevant_corrections

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

CLASSIFIER_PROMPT = """You are a support ticket classifier for NovaPay, a payments platform.

Classify the following customer message into exactly one of these categories:

BILLING — anything related to:
payments, charges, double charges, refunds, invoices, subscriptions, cancellations,
payment methods, credit cards, bank accounts, VAT, billing history, pricing

TECHNICAL — anything related to:
API errors, 502 errors, 429 errors, webhooks, authentication, API keys, tokens,
rate limits, file uploads, file formats, SDKs, integrations, HTTP errors, code

GENERAL — anything related to:
account settings, password reset, two-factor authentication, 2FA, data export,
support hours, account deletion, contact information, data privacy, general enquiries

{corrections}

Rules:
- Reply with only one word: billing, technical, or general
- No punctuation, no explanation
- If unsure between billing and general, pick billing
- If unsure between technical and general, pick general

Customer message: {message}

Category:"""

def classify_ticket(message: str) -> dict:
    corrections = get_relevant_corrections(message)

    corrections_text = ""
    if corrections:
        corrections_text = "Learn from these past corrections:\n"
        for c in corrections:
            try:
                corrections_text += f"- Message like '{c['message']}' should be classified as: {c['correct_category']}\n"
            except KeyError:
                continue

    prompt = ChatPromptTemplate.from_template(CLASSIFIER_PROMPT)
    chain = prompt | llm

    result = chain.invoke({
        "message": message,
        "corrections": corrections_text
    })

    category = result.content.strip().lower()
    if category not in ["billing", "technical", "general"]:
        category = "general"

    return {
        "category": category,
        "message": message
    }