import boto3
from app.core.config import settings
from botocore.exceptions import ClientError

s3 = boto3.client(
    "s3",
    endpoint_url=settings.r2_endpoint,
    aws_access_key_id=settings.r2_access_key_id,
    aws_secret_access_key=settings.r2_secret_access_key,
    region_name="auto",
)


def create_presigned_put(key: str, content_type: str) -> str:
    return s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.r2_bucket,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=600,
    )


def get_object_info(key: str):
    return s3.head_object(
        Bucket=settings.r2_bucket,
        Key=key,
    )


def delete_object(key: str):
    s3.delete_object(
        Bucket=settings.r2_bucket,
        Key=key,
    )


def object_exists(key: str) -> bool:
    try:
        s3.head_object(
            Bucket=settings.r2_bucket,
            Key=key,
        )
        return True

    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise
