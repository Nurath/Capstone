import boto3
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

def upload_image_to_s3(image_bytes, filename, content_type, manual_folder="default-manual"):
    """
    Upload image to S3 bucket and return public URL
    """
    session = boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    s3 = session.client('s3')

    # Unique S3 key to prevent overwrite
    unique_key = f"manual-images/{manual_folder}/{uuid.uuid4()}_{filename}"

    try:
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=unique_key,
            Body=image_bytes,
            ContentType=content_type,
            ACL='public-read'  # Make the object publicly readable
        )
        return f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_key}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
