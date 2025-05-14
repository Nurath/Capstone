# def create_chunks_with_references(content_blocks):
#     chunks = []
#     for block in content_blocks:
#         if block["text"].strip():
#             chunk_text = block["text"]
#             image_entries = block.get("images", [])

#             for image in image_entries:
#                 if "filename" in image:
#                     chunk_text += f"\n[Image: {image['filename']}]"

#             # S3 upload placeholder - S3 upload happens later in app.py
#             chunks.append({
#                 "text": chunk_text,
#                 "metadata": {
#                     "page": block["page"],
#                     "images": image_entries  # This still includes raw bytes, used in app.py for S3 upload
#                 }
#             })
#     return chunks


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