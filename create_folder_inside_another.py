from __future__ import print_function

import os.path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/drive.file']
folder_names = [
    'name1',
    'name2',
    'name3'
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
        for folder_name in folder_names:
          file_metadata = {
              'name': folder_name,
              'mimeType': 'application/vnd.google-apps.folder',
              'parents': ['1I97pGPORbIjFwojA9Oddv5fvyLbW8jKr']
          }

          # pylint: disable=maybe-no-member
          file = service.files().create(body=file_metadata, fields='id'
                                        ).execute()
          print(F'Folder ID: "{file.get("id")}".')
          folder_ids.append(file.get('id'))

        return folder_ids

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


if __name__ == '__main__':
    create_folder()
