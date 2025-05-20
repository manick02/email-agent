import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"
]

CLIENT_SECRET = "credentials.json"
TOKEN = "token.json"

def get_gmail_service():
    """Handles OAuth 2.0 authentication and returns a Gmail API service."""
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)

    # If no valid token, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the token for next time
        with open(TOKEN, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)