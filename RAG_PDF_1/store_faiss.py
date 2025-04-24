import faiss

def store_faiss_index(embeddings, dim, path=None):
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    if path:
        faiss.write_index(index, path)

    return index

def load_faiss_index(path):
    import faiss
    return faiss.read_index(path)
