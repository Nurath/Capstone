def create_chunks_with_references(content_blocks):
    chunks = []
    for block in content_blocks:
        if block["text"].strip():
            chunk_text = block["text"]
            for image_path in block["images"]:
                chunk_text += f"\\n[Image: {image_path}]"
            chunks.append({
                "text": chunk_text,
                "metadata": {"page": block["page"], "images": block["images"]}
            })
    return chunks