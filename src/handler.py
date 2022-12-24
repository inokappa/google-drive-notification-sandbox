from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import base64
import json
import boto3


SCOPES = [
    'https://www.googleapis.com/auth/drive'
]


ssm = boto3.client('ssm', region_name='ap-northeast-1')


def get_page_token():
    response = ssm.get_parameters(
        Names=[
            'google-drive-watch-page-token',
        ],
        WithDecryption=False
    )
    return response['Parameters'][0]['Value']


def set_page_token(value):
    ssm.put_parameter(
        Name='google-drive-watch-page-token',
        Value=value,
        Type='String',
        Overwrite=True
    )


def lambda_handler(event, context):
    sa_json = base64.b64decode(os.environ['GOOGLE_SERVICE_ACCOUNT']).decode()
    service_account_info = json.loads(sa_json)
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES)
    
    service = build('drive', 'v3', credentials=credentials, cache_discovery=False)

    page_token = get_page_token()
    response = service.changes().list(pageToken=page_token).execute()
    
    for change in response.get('changes'):
        print('Change found for file: %s' % change.get('fileId'))
        if 'newStartPageToken' in response:
            update_page_token = response.get('newStartPageToken')
            set_page_token(update_page_token)
