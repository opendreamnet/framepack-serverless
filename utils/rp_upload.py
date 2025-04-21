import os
import uuid
import time
import boto3
import multiprocessing
from typing import Optional, Tuple
from boto3.s3.transfer import TransferConfig
from botocore.config import Config
from runpod.serverless.utils.rp_upload import extract_region_from_url
from utils.crypto import encrypt

def get_boto_client(
    bucket_creds: Optional[dict] = None,
) -> Tuple[
    boto3.client, TransferConfig
]:  # pragma: no cover # pylint: disable=line-too-long
    """
    Returns a boto3 client and transfer config for the bucket.
    """
    bucket_session = boto3.session.Session()

    boto_config = Config(
        signature_version="s3v4", 
        retries={"max_attempts": 3, "mode": "standard"},
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required"
    )

    transfer_config = TransferConfig(
        multipart_threshold=1024 * 25,
        max_concurrency=multiprocessing.cpu_count(),
        multipart_chunksize=1024 * 25,
        use_threads=True,
    )

    if bucket_creds:
        endpoint_url = bucket_creds["endpointUrl"]
        access_key_id = bucket_creds["accessId"]
        secret_access_key = bucket_creds["accessSecret"]
        region = bucket_creds["region"]
    else:
        endpoint_url = os.environ.get("BUCKET_ENDPOINT_URL", None)
        access_key_id = os.environ.get("BUCKET_ACCESS_KEY_ID", None)
        secret_access_key = os.environ.get("BUCKET_SECRET_ACCESS_KEY", None)
        region = os.environ.get("BUCKET_REGION", extract_region_from_url(endpoint_url) if endpoint_url != None else None)

    if endpoint_url and access_key_id and secret_access_key:
        boto_client = bucket_session.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            config=boto_config,
            region_name=region,
        )
    else:
        boto_client = None

    return boto_client, transfer_config

def upload_test_file():
    bucket_name = os.environ.get("BUCKET_NAME", None)
    file_name = "test_file.txt"
    boto_client, _ = get_boto_client()
    content_type = "text/plain"
    output = "This is a test file.".encode("utf-8")
    
    if boto_client is None:
        # Save the output to a file
        print("No bucket endpoint set, saving to disk folder 'simulated_uploaded'")

        os.makedirs("simulated_uploaded", exist_ok=True)
        sim_upload_location = f"simulated_uploaded/{file_name}"

        with open(sim_upload_location, "wb") as file_output:
            file_output.write(output)

        return sim_upload_location
    
    boto_client.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=output,
        ContentType=content_type,
    )
    
    presigned_url: str = boto_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": f"{bucket_name}", "Key": f"{file_name}"},
        ExpiresIn=604800,
    )

    return presigned_url

def upload_video(
    job_id,
    file_location,
    encrypt_file=False,
):  # pylint: disable=line-too-long # pragma: no cover
    """
    Upload a single file to bucket storage.
    """
    bucket_name = os.environ.get("BUCKET_NAME", None)
    file_name = os.path.splitext(os.path.basename(file_location))[0]
    boto_client, _ = get_boto_client()
    file_extension = os.path.splitext(file_location)[1]
    content_type = "video/" + file_extension.lstrip(".")
    
    with open(file_location, "rb") as input_file:
        output = input_file.read()
    
    if encrypt_file:
        content_type = "application/x-encrypted"
        file_extension = f"{file_extension}.enc"
        output = encrypt(output)

    if boto_client is None:
        # Save the output to a file
        print("No bucket endpoint set, saving to disk folder 'simulated_uploaded'")

        os.makedirs("simulated_uploaded", exist_ok=True)
        sim_upload_location = f"simulated_uploaded/{file_name}{file_extension}"

        with open(sim_upload_location, "wb") as file_output:
            file_output.write(output)

        return sim_upload_location

    bucket = bucket_name if bucket_name else time.strftime("%m-%y")
    boto_client.put_object(
        Bucket=f"{bucket}",
        Key=f"{job_id}/{file_name}{file_extension}",
        Body=output,
        ContentType=content_type,
    )

    presigned_url: str = boto_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": f"{bucket}", "Key": f"{job_id}/{file_name}{file_extension}"},
        ExpiresIn=604800,
    )

    return presigned_url