import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# https://github.com/googleapis/google-api-python-client/blob/main/docs/oauth.md#flows

def get_credentials_installed():
  SCOPES = ['https://www.googleapis.com/auth/sdm.service']

  credentials = None

  pickle_file = './secrets/token.pickle'

  if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            credentials = pickle.load(token)

  if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('./secrets/client_secret.json', SCOPES)
            credentials = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(credentials, token)

  return credentials