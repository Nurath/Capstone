from query_engine import load_chunks_and_index, retrieve_relevant_chunks
from llm_response import generate_llm_response  # Uncomment this if using OpenAI API

def main():
    chunks, index, model = load_chunks_and_index()

    query = input("Enter your question about the equipment manual: ")
    retrieved_chunks = retrieve_relevant_chunks(query, chunks, index, model, top_k = 1)

    context = "\\n\\n".join([chunk["text"] for chunk in retrieved_chunks])

    print("\\n--- Retrieved Chunks ---")
    for i, chunk in enumerate(retrieved_chunks, 1):
        print(f"Chunk {i}:")
        print(chunk["text"])
        print()

    # Optionally send to LLM
    prompt = f"Answer the following question using the provided context:\\n\\n{context}\\n\\nQuestion: {query}"
    response = generate_llm_response(prompt)
    print("\\n--- LLM Response ---")
    print(response)

if __name__ == "__main__":
    main()