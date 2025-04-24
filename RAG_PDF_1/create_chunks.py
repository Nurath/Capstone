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


# def create_chunks_with_references(content_blocks):
#     chunks = []
#     for block in content_blocks:
#         if block["text"].strip():
#             chunk_text = block["text"]
#             for image_path in block["images"]:
#                 chunk_text += f"\\n[Image: {image_path}]"
#             chunks.append({
#                 "text": chunk_text,
#                 "metadata": {"page": block["page"], "images": block["images"]}
#             })
#     return chunks

import os
import json
import boto3
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


import os

import os
import json
import boto3
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def create_chunks_with_references(content_blocks, pdf_filename):
    s3_prefix = f"manuals/{pdf_filename}/images/"
    chunks = []

    for block in content_blocks:
        image_entries = block.get("images", [])

        # ⛳ Collect both filenames and URLs here
        image_filenames = [img["filename"] for img in image_entries]
        image_urls = [img["s3_url"] for img in image_entries if img.get("s3_url")]
        
        # ✍️ Append [Image: ...] references to text
        chunk_text = block["text"]
        for img_name in image_filenames:
            chunk_text += f"\n[Image: {img_name}]"

        chunks.append({
            "text": chunk_text.strip(),
            "metadata": {
                "page": block["page"],
                "image_urls": image_urls
            }
        })

    return chunks