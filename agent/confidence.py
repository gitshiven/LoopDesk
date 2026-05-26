from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

CONFIDENCE_PROMPT = """You are evaluating whether an AI support agent gave a good answer.

Customer message: {message}
Agent response: {response}
Context used: {context}

Rate the confidence of this response on a scale of 0.0 to 1.0:
- 1.0 = perfect answer, fully supported by context
- 0.7 = good answer, mostly supported
- 0.5 = partial answer, some gaps
- 0.3 = weak answer, mostly guessing
- 0.0 = wrong or no answer

Reply with only a number between 0.0 and 1.0. Nothing else.

Confidence score:"""

CONFIDENCE_THRESHOLD = 0.75

def score_confidence(message: str, response: str, context: str) -> float:
    prompt = ChatPromptTemplate.from_template(CONFIDENCE_PROMPT)
    chain = prompt | llm

    result = chain.invoke({
        "message": message,
        "response": response,
        "context": context
    })

    try:
        score = float(result.content.strip())
        score = max(0.0, min(1.0, score))
    except ValueError:
        score = 0.5

    return score

def should_escalate(confidence: float) -> bool:
    return confidence < CONFIDENCE_THRESHOLD