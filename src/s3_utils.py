import boto3
import json
import os
import sys
from dotenv import load_dotenv, find_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.insert(1, "/home/")

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")


def connect_to_s3(aws_access_key_id, aws_secret_access_key):
    session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    try:
        s3 = session.client('s3')
    except Exception as e:
        print(f"failed to connect to s3 error: {e}")
        return None
    else:
        print("connected to s3")
        return s3
    

def create_s3_bucket(BUCKET_NAME: str):

    s3 = connect_to_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    list_buckets = [l["Name"] for l in s3.list_buckets()["Buckets"]]

    if BUCKET_NAME in list_buckets:
        print(f"bucket {BUCKET_NAME} already exists")
    else:
        try:
            s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "ap-southeast-1"})
        except Exception as e:
            print(f"failed to create bucket {BUCKET_NAME} error: {e}")
        else:
            print(f"bucket {BUCKET_NAME} created")

def write_json_to_s3(results_dict: dict, bucket: str, zone: str, file_name: str):

    s3 = connect_to_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    create_s3_bucket(bucket)

    # Convert the dictionary to a JSON string
    json_result = json.dumps(results_dict, indent=4)

    # upload the JSON string to S3
    try:
        response = s3.put_object(Bucket=bucket, 
                                 Key=f"{zone}/{file_name}", 
                                 Body=bytes(json_result.encode('UTF-8')))
    except Exception as e:
        return f"Error uploading {file_name} to s3 error: {e}"
    else:
        return f"{file_name} is uploaded to s3"
    
def read_json_from_s3(bucket: str, zone: str, file_name: str):
    s3 = connect_to_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    try:
        response = s3.get_object(Bucket=bucket, Key=f"{zone}/{file_name}")
        json_data = response['Body'].read().decode('utf-8')
        data = json.loads(json_data)
    except Exception as e:
        return f"Error reading {file_name} from s3 error: {e}"
    else:
        return data