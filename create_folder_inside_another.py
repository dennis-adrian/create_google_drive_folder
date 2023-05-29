from __future__ import print_function

import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/drive.file']

names_and_emails = [
    ('folder name', 'user@email.com')
]


def get_creds():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def create_folder():
    creds = get_creds()

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        folder_ids = []
        for name_and_email in names_and_emails:
          folder_name = name_and_email[0]
          user_email = name_and_email[1]

          file_metadata = {
              'name': folder_name,
              'mimeType': 'application/vnd.google-apps.folder',
              'parents': ['1I97pGPORbIjFwojA9Oddv5fvyLbW8jKr']
          }

          # pylint: disable=maybe-no-member
          file = service.files().create(body=file_metadata, fields='id').execute()
          print(F'Folder ID: "{file.get("id")}".')
          folder_ids.append(file.get('id'))

          share_file(file.get('id'), user_email)

        return folder_ids

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def share_file(real_file_id, real_user):
    """Batch permission modification.
    Args:
        real_file_id: file Id
        real_user: User ID
        real_domain: Domain of the user ID
    Prints modified permissions
    """

    creds = get_creds()

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)
        ids = []
        file_id = real_file_id

        def callback(request_id, response, exception):
            if exception:
                # Handle error
                print(exception)
            else:
                print(f'Request_Id: {request_id}')
                print(F'Permission Id: {response.get("id")}')
                ids.append(response.get('id'))

        # pylint: disable=maybe-no-member
        batch = service.new_batch_http_request(callback=callback)
        user_permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': real_user
        }
        batch.add(service.permissions().create(fileId=file_id, body=user_permission, fields='id',))
        batch.execute()

    except HttpError as error:
        print(F'An error occurred: {error}')
        ids = None

    return ids

if __name__ == '__main__':
    create_folder()
