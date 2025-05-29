import boto3
import os
import mimetypes
import io
import magic
import uuid
import time
import logging
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_fixed
from pydantic import BaseModel
from typing import Optional
from botocore.config import Config
from PIL import Image
from .logging import logger


class UploaderOptions(BaseModel):
    endpoint_url: Optional[str] = None
    region_name: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    bucket_name: Optional[str] = None


class Uploader():
    logger = logger.getChild("uploader")
    client = None

    def __init__(self, options: Optional[UploaderOptions] = None):
        if options is None:
            options = UploaderOptions.model_validate({
                "endpoint_url": os.environ.get("S3_ENDPOINT", None),
                "region_name": os.environ.get("S3_REGION", None),
                "aws_access_key_id": os.environ.get("S3_KEY", None),
                "aws_secret_access_key": os.environ.get("S3_SECRET", None),
                "bucket_name": os.environ.get("S3_BUCKET", None),
            })

        self.options = options

        # Create a copy of options without 'bucket_name'
        boto3_options = {key: value for key,
                         value in options.model_dump().items() if key != "bucket_name"}

        # The configuration has not been set.
        if options.endpoint_url is None:
            self.logger.warning(
                "S3_ENDPOINT is not set. The files will be saved locally in the folder 'simulated_uploaded'")
            return

        try:
            config = Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required"
            )

            self.client = boto3.client(
                "s3",
                **boto3_options,
                config=config,
            )

            self.logger.info(
                f"Uploader initialized for: {options.endpoint_url}")
        except Exception as e:
            self.logger.warning(f"Failed to initialize uploader: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.2),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def upload_file(
        self,
        input: str | bytes | Image.Image,
        target_path: str,
        file_name: Optional[str] = None,
        file_mimetype: Optional[str] = None,
        bucket_name: Optional[str] = None,
        presigned_url_return=True,
        presigned_url_expires=3600,
    ):
        if bucket_name is None:
            bucket_name = self.options.bucket_name

        output: Optional[bytes] = None
        file_size: Optional[int] = None

        if isinstance(input, str) and os.path.isfile(input):
            if file_name is None:
                file_name = os.path.basename(input)
                self.logger.debug(f"Filename Detected: {file_name}")

            if file_mimetype is None:
                file_mimetype, _ = mimetypes.guess_type(input)
                self.logger.debug(f"Mimetype Detected: {file_mimetype}")

            file_size = os.path.getsize(input)

            with open(input, "rb") as file_input:
                output = file_input.read()
        elif isinstance(input, Image.Image):
            if file_mimetype is None and file_name is not None:
                file_mimetype, _ = mimetypes.guess_type(file_name)
                self.logger.debug(f"Mimetype Detected: {file_mimetype}")

            if file_mimetype is not None:
                file_extension = mimetypes.guess_extension(file_mimetype)

                if file_extension is None:
                    raise Exception(
                        f"Invalid extension for mimetype: {file_mimetype}")

                format = file_extension[1:]

                if format == "jpg":
                    format = "jpeg"

                self.logger.debug(f"PIL Image Format Detected: {format}")
            else:
                file_mimetype = "image/jpeg"
                format = "jpeg"

            byte_data = io.BytesIO()
            input.save(byte_data, format=format)

            input = byte_data.getvalue()

        if isinstance(input, bytes):
            output = input
            file_size = len(output)

            if file_mimetype is None:
                file_mimetype = magic.from_buffer(output[:2048], mime=True)
                self.logger.debug(f"Mimetype Detected: {file_mimetype}")

            if file_name is None:
                random_name = uuid.uuid4()
                file_extension = mimetypes.guess_extension(file_mimetype)
                file_name = f"{random_name}{file_extension}"
                self.logger.debug(f"Filename Generated: {file_name}")

        assert output is not None
        assert file_name is not None

        file_target_path = f"{target_path}/{file_name}"

        if self.client is None:
            file_target_path = f"./simulated_uploaded/{file_target_path}"
            os.makedirs(os.path.dirname(file_target_path), exist_ok=True)

            with open(file_target_path, "wb") as file_output:
                file_output.write(output)

            return file_target_path

        start_time = time.perf_counter()
        self.logger.info(f"Uploading to: {file_target_path}")

        self.client.put_object(
            Bucket=bucket_name,
            Key=file_target_path,
            Body=output,
            ContentType=file_mimetype,
            ContentLength=file_size,
        )

        self.logger.info(
            f"Upload completed in: {time.perf_counter() - start_time:.2f}s")

        if presigned_url_return:
            presigned_url = self.client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": file_target_path,
                },
                ExpiresIn=presigned_url_expires,
            )
            assert isinstance(presigned_url, str)

            return presigned_url

        return file_target_path


uploader = Uploader()
