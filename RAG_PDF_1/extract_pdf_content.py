# # import fitz  # PyMuPDF
# # import os
# # from PIL import Image
# # import io

# # def extract_pdf_content(pdf_path, output_image_dir="output/images"):
# #     os.makedirs(output_image_dir, exist_ok=True)
# #     doc = fitz.open(pdf_path)
# #     content_blocks = []

# #     for page_number, page in enumerate(doc, start=1):
# #         # Render full page as image
# #         pix = page.get_pixmap(dpi=200)
# #         image_filename = f"page_{page_number}.png"
# #         image_path = os.path.join(output_image_dir, image_filename)
# #         pix.save(image_path)

# #         # Extract text
# #         text = page.get_text("text")  # or "blocks" if you want layout

        
        
# #         # text_blocks = page.get_text("blocks")
# #         # images = page.get_images(full=True)
# #         # image_paths = []

# #         # for img_index, img in enumerate(images):
# #         #     xref = img[0]
# #         #     base_image = doc.extract_image(xref)
# #         #     image_bytes = base_image["image"]
# #         #     image_ext = base_image["ext"]
# #         #     image = Image.open(io.BytesIO(image_bytes))

# #         #     image_filename = f"page_{page_number}_img_{img_index}.{image_ext}"
# #         #     image_path = os.path.join(output_image_dir, image_filename)
# #         #     image.save(image_path)
# #         #     image_paths.append(image_path)

# #         # text = "\\n".join(block[4] for block in text_blocks if block[4].strip())

# #         content_blocks.append({
# #             "page": page_number,
# #             "text": text.strip(),  # simple text only
# #             "images": [image_path]
# #         })

# #     return content_blocks


# import fitz  # PyMuPDF
# import os
# from PIL import Image
# import io
# import base64
# from io import BytesIO
# from pdf2image import convert_from_path
# import pytesseract

# def extract_pdf_content(pdf_path, output_image_dir="output/images"):
#     os.makedirs(output_image_dir, exist_ok=True)
#     doc = fitz.open(pdf_path)
#     content_blocks = []

#     for page_number, page in enumerate(doc, start=1):
#         text = page.get_text("text")
#         image_paths = []

#         images = page.get_images(full=True)
#         seen = set()  # Avoid duplicates (sliced tiles often share xrefs)

#         for img_index, img in enumerate(images):
#             xref = img[0]
#             if xref in seen:
#                 continue  # Skip duplicates or slices
#             seen.add(xref)

#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
#             image_ext = base_image["ext"]
#             image = Image.open(io.BytesIO(image_bytes))

#             image_filename = f"page_{page_number}_img_{img_index}.{image_ext}"
#             image_path = os.path.join(output_image_dir, image_filename)
#             image.save(image_path)
#             image_paths.append(image_path)
            
#         if not text.strip():
#             pix = page.get_pixmap(dpi=300)
#             image = Image.open(BytesIO(pix.tobytes("png")))
#             text = pytesseract.image_to_string(image)

#         content_blocks.append({
#             "page": page_number,
#             "text": text.strip(),
#             "images": image_paths
#         })

#     return content_blocks



# def encode_image_to_base64(image_path):
#     with Image.open(image_path) as img:
#         buffered = BytesIO()
#         img.save(buffered, format="JPEG")
#         return base64.b64encode(buffered.getvalue()).decode("utf-8")
    


# import fitz  # PyMuPDF
# from PIL import Image
# from io import BytesIO
# import pytesseract


# def extract_pdf_content(pdf_path):
#     doc = fitz.open(pdf_path)
#     content_blocks = []

#     for page_number, page in enumerate(doc, start=1):
#         text = page.get_text("text")
#         image_data_list = []

#         images = page.get_images(full=True)
#         seen = set()  # Avoid duplicates

#         for img_index, img in enumerate(images):
#             xref = img[0]
#             if xref in seen:
#                 continue
#             seen.add(xref)

#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
#             image_ext = base_image["ext"]
#             image_filename = f"page_{page_number}_img_{img_index}.{image_ext}"
#             image_data_list.append({
#                 "filename": image_filename,
#                 "bytes": image_bytes,
#                 "content_type": f"image/{image_ext.lower()}"
#             })

#         # OCR fallback if no text found
#         if not text.strip():
#             pix = page.get_pixmap(dpi=300)
#             image = Image.open(BytesIO(pix.tobytes("png")))
#             text = pytesseract.image_to_string(image)

#         content_blocks.append({
#             "page": page_number,
#             "text": text.strip(),
#             "images": image_data_list  # List of dicts with filename, bytes, content_type
#         })

#     return content_blocks


def extract_pdf_content(pdf_path):
    import fitz  # PyMuPDF
    import io
    from PIL import Image

    doc = fitz.open(pdf_path)
    content_blocks = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        images = page.get_images(full=True)
        image_objs = []

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image["ext"]
            img_name = f"page_{page_number}_img_{img_index}.{img_ext}"

            image_objs.append({
                "filename": img_name,
                "bytes": img_bytes
            })

        content_blocks.append({
            "page": page_number,
            "text": text.strip(),
            "images": image_objs
        })

    return content_blocks

