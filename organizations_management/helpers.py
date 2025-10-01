from django.conf import settings


def create_bucket(bucket_name: str):
    settings.S3_CLIENT.create_bucket(Bucket=bucket_name)

def generate_upload_presigned_url(bucket_name, location, content_type, expiration=3600):
    try:
        url = settings.S3_CLIENT.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': location, 'ContentType': content_type},
            ExpiresIn=expiration
        )
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None
    return url

def generate_download_presigned_url(bucket_name, location, expiration=3600):
    try:
        url = settings.S3_CLIENT.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': location},
            ExpiresIn=expiration
        )
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None
    return url