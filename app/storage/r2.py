import asyncio

import boto3

from app.core.config import settings

s3 = boto3.client(
    "s3",
    endpoint_url=settings.r2_endpoint,
    aws_access_key_id=settings.r2_access_key_id,
    aws_secret_access_key=settings.r2_secret_access_key,
    region_name="auto",
)


async def create_presigned_put(key: str, content_type: str) -> str:
    return await asyncio.to_thread(
        s3.generate_presigned_url,
        "put_object",
        Params={
            "Bucket": settings.r2_bucket,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=600,
    )


async def get_object_info(key: str):
    return await asyncio.to_thread(
        s3.head_object,
        Bucket=settings.r2_bucket,
        Key=key,
    )


async def delete_object(key: str):
    await asyncio.to_thread(
        s3.delete_object,
        Bucket=settings.r2_bucket,
        Key=key,
    )


async def copy_object(source_key: str, key: str):
    await asyncio.to_thread(
        s3.copy_object,
        Bucket=settings.r2_bucket,
        CopySource={
            "Bucket": settings.r2_bucket,
            "Key": source_key,
        },
        Key=key,
    )
