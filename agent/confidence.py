from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

CONFIDENCE_PROMPT = """You are evaluating whether an AI support agent gave a good answer to a customer support question for NovaPay, a payments platform.

Customer message: {message}
Agent response: {response}
Context used: {context}

Rate the confidence of this response on a scale of 0.0 to 1.0:
- 1.0 = perfect answer, fully supported by context
- 0.8 = good answer, mostly supported by context
- 0.7 = adequate answer, partially supported
- 0.5 = weak answer, context does not clearly support the response
- 0.3 = poor answer, agent is guessing or context is irrelevant
- 0.2 = question is not a real support question (gibberish, meta questions, chit-chat)
- 0.0 = completely wrong or no relevant context

IMPORTANT:
- If context is empty or irrelevant, score 0.3 or below
- If the question is gibberish or not a real support question, score 0.2
- If the response says it cannot find information, score 0.4 or below
- Only score 0.8 or above if the response directly answers using the context

Reply with only a number between 0.0 and 1.0. Nothing else.

Confidence score:"""

CONFIDENCE_THRESHOLD = 0.65

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