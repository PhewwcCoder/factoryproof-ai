import os
from pathlib import Path

import boto3


def client():
    return boto3.client('s3', endpoint_url=os.environ['S3_ENDPOINT'])


def put(key: str, content: bytes):
    if os.getenv('S3_BUCKET'):
        client().put_object(Bucket=os.environ['S3_BUCKET'], Key=key, Body=content)
    else:
        path = Path(os.getenv('STORAGE_DIR', './runtime/private')) / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def get(key: str) -> bytes:
    if os.getenv('S3_BUCKET'):
        return client().get_object(Bucket=os.environ['S3_BUCKET'], Key=key)['Body'].read()
    return (Path(os.getenv('STORAGE_DIR', './runtime/private')) / key).read_bytes()
