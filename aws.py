import sys
import requests
import boto3
import os

# AWS setup (ensure your credentials and bucket region are configured)
os.environ['AWS_ACCESS_KEY_ID'] ='your key id'
os.environ['AWS_SECRET_ACCESS_KEY'] ='your secret access key'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

s3_client = boto3.client('s3')

bucket_name = "teakook-aws-jkk"
file_name = "index.html"

def create_s3_bucket(bucket_name):
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            ObjectOwnership='BucketOwnerPreferred'
        )
        print(f"Bucket '{bucket_name}' created successfully.\n")
        s3_client.delete_public_access_block(Bucket=bucket_name)
        print("Public access block removed.\n")
    except Exception as e:
        print(f"Error creating bucket: {e}")
        return False
    return True

def save_webpage_content(file_name, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"Webpage content saved to {file_name}\n")
        return True
    except requests.RequestException as e:
        print(f"Failed to retrieve the webpage:\n\t{e}")
        return False

def upload_file_to_s3(bucket_name, file_name):
    try:
        s3_client.upload_file(
            file_name, bucket_name, file_name,
            ExtraArgs={'ACL': 'public-read', 'ContentType': 'text/html'}
        )
        print(f"File '{file_name}' uploaded to bucket '{bucket_name}'.\n")
        print(f"URL: https://{bucket_name}.s3.amazonaws.com/{file_name}\n")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python aws.py <URL>")
        sys.exit(1)

    url = sys.argv[1]

    if create_s3_bucket(bucket_name):
        if save_webpage_content(file_name, url):
            upload_file_to_s3(bucket_name, file_name)
