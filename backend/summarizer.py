# backend/summarizer.py
import os
from dotenv import load_dotenv

# modern langchain imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()  # expects GROQ_API_KEY in your .env

def summarize_endpoints_groq(endpoints):
    """
    Summarize a list of endpoints using Groq via LangChain LCEL.
    endpoints: list[dict(method, path, summary)]
    returns: markdown string
    """
    # build the prompt with system+human messages (recommended style)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an assistant for backend developers. "
         "Given API endpoints (method + path + brief summary), produce concise, "
         "developer-friendly documentation:\n"
         "• Purpose\n• Key params (if obvious)\n• Example request body (if applicable)\n"
         "Return clean Markdown with headings per endpoint."),
        ("human",
         "Endpoints:\n{endpoints}\n\nIf info is missing, keep output minimal without guessing.")
    ])

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    parser = StrOutputParser()

    # LCEL chain (prompt → llm → text)
    chain = prompt | llm | parser

    joined = "\n".join(
        f"{e['method']} {e['path']} - {e.get('summary','')}".strip()
        for e in endpoints
    )

    return chain.invoke({"endpoints": joined})