from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from rag.retriever import get_retriever

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

BILLING_PROMPT = """You are a billing support specialist for NovaPay, a payments platform.

Use the following context from our billing documentation to answer the customer's question.
Be concise, helpful, and professional. If you cannot find a clear answer in the context, say so honestly.

Context:
{context}

Customer message: {message}

Your response:"""

def billing_agent(message: str) -> dict:
    retriever = get_retriever(category="billing")
    docs = retriever.invoke(message)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = ChatPromptTemplate.from_template(BILLING_PROMPT)
    chain = prompt | llm

    result = chain.invoke({
        "context": context,
        "message": message
    })

    return {
        "response": result.content,
        "context_used": context,
        "agent": "billing"
    }