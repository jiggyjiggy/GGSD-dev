import boto3
import uuid

# from my_settings import AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME


class MyS3Client:
    def __init__(self, access_key, secret_key, bucket_name):
        boto3_s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.s3_client = boto3_s3
        self.bucket_name = bucket_name

    def upload(self, file):
        try:
            file_id = str(uuid.uuid4())
            extra_args = {'ContentType': file.content_type}

            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                file_id,
                ExtraArgs=extra_args
            )
            uploaded_url = f'https://{self.bucket_name}.s3.ap-northeast-2.amazonaws.com/{file_id}'
            return uploaded_url
        except:
            return None

    def delete(self, file_name):
        return self.s3_client.delete_object(bucket=self.bucket_name, Key=f'{file_name}')


# s3_client = MyS3Client(AWS_S3_ACCESS_KEY_ID, AWS_S3_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME)