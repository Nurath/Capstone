from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from RAG.retriever import retrieve_data
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))


# def create_rag_chain(retriever):
#     """Creates a RAG pipeline with a retriever, prompt, and LLM."""
    
#     prompt_template = """You are an assistant for question-answering tasks. 
#     Use the following retrieved context to answer the question. If you don't know the answer, say you don't know.
    
#     Question: {question}
#     Context: {context}
#     Answer:"""

#     prompt = ChatPromptTemplate.from_template(prompt_template)
#     llm = ChatGroq(model="deepseek-r1-distill-llama-70b", verbose=True, temperature=0)

#     rag_chain = (
#         {"context": retriever, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
#     )

#     return rag_chain

llm = ChatGroq(model="deepseek-r1-distill-llama-70b", verbose=True, temperature=0)

def create_rag_chain(query):
    retrieved_docs = retrieve_data(query)
    context = "\n".join([doc["content"] for doc in retrieved_docs if doc["type"] == "text"])

    prompt = f"Use the following retrieved data to answer the query:\n{context}\n\nQuery: {query}\nAnswer:"
    response = llm.predict(prompt)
    
    return response, retrieved_docs