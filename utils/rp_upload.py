import os
import uuid
import time
from typing import Optional
from runpod.serverless.utils.rp_upload import get_boto_client

def upload_video(
    job_id,
    file_location,
    result_index=0,
    results_list=None,
    bucket_name: Optional[str] = None,
):  # pylint: disable=line-too-long # pragma: no cover
    """
    Upload a single file to bucket storage.
    """
    file_name = str(uuid.uuid4())[:8]
    boto_client, _ = get_boto_client()
    file_extension = os.path.splitext(file_location)[1]
    content_type = "video/" + file_extension.lstrip(".")

    with open(file_location, "rb") as input_file:
        output = input_file.read()

    if boto_client is None:
        # Save the output to a file
        print("No bucket endpoint set, saving to disk folder 'simulated_uploaded'")
        print("If this is a live endpoint, please reference the following:")
        print(
            "https://github.com/runpod/runpod-python/blob/main/docs/serverless/utils/rp_upload.md"
        )  # pylint: disable=line-too-long

        os.makedirs("simulated_uploaded", exist_ok=True)
        sim_upload_location = f"simulated_uploaded/{file_name}{file_extension}"

        with open(sim_upload_location, "wb") as file_output:
            file_output.write(output)

        if results_list is not None:
            results_list[result_index] = sim_upload_location

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

    if results_list is not None:
        results_list[result_index] = presigned_url

    return presigned_url