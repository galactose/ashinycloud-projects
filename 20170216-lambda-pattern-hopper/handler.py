import boto3
import json

S3 = boto3.client('s3')
lambda_client = boto3.client('lambda')

def handler(event, context):
    print 'Event:', event
    if 'config_bucket' not in event:
        raise Exception('Missing config_bucket')
    if 'lambda_function' not in event:
        raise Exception('Missing lambda_function')

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(event['config_bucket'])
    result = bucket.meta.client.list_objects(
        Bucket=bucket.name, Prefix='/', Delimiter='/'
    )
    for dataset_prefixes in result.get('CommonPrefixes'):
        event['dataset_prefix'] = dataset_prefixes
        response = lambda_client.invoke(
            FunctionName=event['lambda_function'],
            InvocationType='Event',
            Payload=json.dumps(event)
        )
        print response

