import hashlib
import os
from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.client import Config


@dataclass
class StorageConfig:
    bucket: str
    endpoint_url: Optional[str]
    access_key: str
    secret_key: str
    region: Optional[str]
    public_base_url: Optional[str]
    use_path_style: bool = True


def get_storage_config() -> StorageConfig:
    return StorageConfig(
        bucket=os.environ["STORAGE_BUCKET"],
        endpoint_url=os.getenv("STORAGE_ENDPOINT_URL"),
        access_key=os.environ["STORAGE_ACCESS_KEY"],
        secret_key=os.environ["STORAGE_SECRET_KEY"],
        region=os.getenv("STORAGE_REGION"),
        public_base_url=os.getenv("STORAGE_PUBLIC_BASE_URL"),
        use_path_style=os.getenv("STORAGE_PATH_STYLE", "true").lower() == "true",
    )


def create_s3_client(cfg: StorageConfig):
    return boto3.client(
        "s3",
        endpoint_url=cfg.endpoint_url,
        region_name=cfg.region,
        aws_access_key_id=cfg.access_key,
        aws_secret_access_key=cfg.secret_key,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path" if cfg.use_path_style else "virtual"},
        ),
    )


def generate_object_key(user_id: str, suffix: str = "original.jpg") -> str:
    hashed = hashlib.sha256(user_id.encode()).hexdigest()
    return f"users/{hashed}/{suffix}"


def upload_image(image_bytes: bytes, user_id: str, content_type: str = "image/jpeg") -> str:
    cfg = get_storage_config()
    client = create_s3_client(cfg)
    object_key = generate_object_key(user_id)

    client.put_object(
        Bucket=cfg.bucket,
        Key=object_key,
        Body=image_bytes,
        ContentType=content_type,
        ACL="private",
    )

    if cfg.public_base_url:
        return f"{cfg.public_base_url.rstrip('/')}/{object_key}"

    return client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": cfg.bucket, "Key": object_key},
        ExpiresIn=60 * 5,
    )

