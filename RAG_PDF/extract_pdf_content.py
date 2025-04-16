# import fitz  # PyMuPDF
# import os
# from PIL import Image
# import io

# def extract_pdf_content(pdf_path, output_image_dir="output/images"):
#     os.makedirs(output_image_dir, exist_ok=True)
#     doc = fitz.open(pdf_path)
#     content_blocks = []

#     for page_number, page in enumerate(doc, start=1):
#         # Render full page as image
#         pix = page.get_pixmap(dpi=200)
#         image_filename = f"page_{page_number}.png"
#         image_path = os.path.join(output_image_dir, image_filename)
#         pix.save(image_path)

#         # Extract text
#         text = page.get_text("text")  # or "blocks" if you want layout

        
        
#         # text_blocks = page.get_text("blocks")
#         # images = page.get_images(full=True)
#         # image_paths = []

#         # for img_index, img in enumerate(images):
#         #     xref = img[0]
#         #     base_image = doc.extract_image(xref)
#         #     image_bytes = base_image["image"]
#         #     image_ext = base_image["ext"]
#         #     image = Image.open(io.BytesIO(image_bytes))

#         #     image_filename = f"page_{page_number}_img_{img_index}.{image_ext}"
#         #     image_path = os.path.join(output_image_dir, image_filename)
#         #     image.save(image_path)
#         #     image_paths.append(image_path)

#         # text = "\\n".join(block[4] for block in text_blocks if block[4].strip())

#         content_blocks.append({
#             "page": page_number,
#             "text": text.strip(),  # simple text only
#             "images": [image_path]
#         })

#     return content_blocks


import fitz  # PyMuPDF
import os
from PIL import Image
import io
import base64
from io import BytesIO

def extract_pdf_content(pdf_path, output_image_dir="output/images"):
    os.makedirs(output_image_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    content_blocks = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        image_paths = []

        images = page.get_images(full=True)
        seen = set()  # Avoid duplicates (sliced tiles often share xrefs)

        for img_index, img in enumerate(images):
            xref = img[0]
            if xref in seen:
                continue  # Skip duplicates or slices
            seen.add(xref)

            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image = Image.open(io.BytesIO(image_bytes))

            image_filename = f"page_{page_number}_img_{img_index}.{image_ext}"
            image_path = os.path.join(output_image_dir, image_filename)
            image.save(image_path)
            image_paths.append(image_path)

        content_blocks.append({
            "page": page_number,
            "text": text.strip(),
            "images": image_paths
        })

    return content_blocks



def encode_image_to_base64(image_path):
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

