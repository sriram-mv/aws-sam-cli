import botocore
import time
import math


def patch_client(client_to_be_patched):
    def patch_boto_session_client_s3(*args, **kwargs):
        cl = client_to_be_patched(*args, **kwargs)
        if getattr(cl, "put_object"):
            BACKOFF = 1
            RETRIES = 3
            old_put_object = getattr(cl, "put_object")

            def put_object_wrapper(*args, **kwargs):
                old_put_object(*args, **kwargs)
                retry_attempts = 0
                while retry_attempts <= RETRIES:
                    try:
                        cl.get_object(Bucket=kwargs["Bucket"], Key=kwargs["Key"])
                        break
                    except botocore.exceptions.ClientError as ex:
                        retry_attempts += 1
                        time.sleep(math.pow(BACKOFF, retry_attempts))

            setattr(cl, "put_object", put_object_wrapper)
        return cl

    return patch_boto_session_client_s3
