from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from memory.corrections import get_relevant_corrections

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

CLASSIFIER_PROMPT = """You are a support ticket classifier for NovaPay, a payments platform.

Classify the following customer message into exactly one of these categories:
- billing
- technical
- general

{corrections}

Rules:
- Reply with only one word: billing, technical, or general
- No punctuation, no explanation

Customer message: {message}

Category:"""

def classify_ticket(message: str) -> dict:
    corrections = get_relevant_corrections(message)

    corrections_text = ""
    if corrections:
        corrections_text = "Learn from these past corrections:\n"
        for c in corrections:
            corrections_text += f"- Message like '{c['message']}' should be classified as: {c['correct_category']}\n"

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