from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from rag.retriever import get_retriever

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)

TECHNICAL_PROMPT = """You are a technical support specialist for NovaPay, a payments platform.

Use the following context from our technical documentation to answer the customer's question.
Be concise, helpful, and technical where needed. If you cannot find a clear answer in the context, say so honestly.

Context:
{context}

Customer message: {message}

Your response:"""

def technical_agent(message: str) -> dict:
    retriever = get_retriever(category="technical")
    docs = retriever.invoke(message)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = ChatPromptTemplate.from_template(TECHNICAL_PROMPT)
    chain = prompt | llm

    result = chain.invoke({
        "context": context,
        "message": message
    })

    response = result.content
    response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
    response = re.sub(r'\*(.*?)\*', r'\1', response)
    response = re.sub(r'^[-•]\s+', '', response, flags=re.MULTILINE)

    return {
        "response": result.content,
        "context_used": context,
        "agent": "technical"
    }