from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
import uuid
import sys


SCOPES = ['https://www.googleapis.com/auth/drive']
ADDRESS = 'https://example.com'


def get_service_credential():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('./client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))

    return service


def create_channel():
    service = get_service_credential()
    res_token = service.changes().getStartPageToken().execute()
    page_token = res_token['startPageToken']

    body = {
        'id': str(uuid.uuid1()),
        'type': 'web_hook',
        'address': ADDRESS
    }
    try:
        watch_info = service.changes().watch(
            pageToken=page_token, body=body).execute()
        print('ID: %s' % watch_info.get('id'))
        print('Resource ID: %s' % watch_info.get('resourceId'))
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def stop_channel(channel_id, resource_id):
    service = get_service_credential()
    body = {
        'id': channel_id,
        'resourceId': resource_id
    }
    try:
        service.channels().stop(body=body).execute()
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def main():
    arg = sys.argv
    if len(arg) == 1:
        sys.exit(0)
    elif len(arg) == 2 and arg[1] == 'create':
        create_channel()
    elif len(arg) > 2 and arg[1] == 'stop':
        stop_channel(arg[2], arg[3])
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
