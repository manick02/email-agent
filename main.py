import os
import time
import argparse  # <-- Add this import
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_mistralai import ChatMistralAI   
import schedule
from email_classifier import EmailClassifier
import base64
# Expanded scopes to allow read + modify actions
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify"  # Allows marking as read, archiving, etc.
]

CLIENT_SECRET="credentials.json"
TOKEN = "token.json"




class GmailPoller:
    def __init__(self,email_classifier):
        self.service = self._authenticate()
        self.email_classifier = email_classifier

    def _authenticate(self):
        """Handles OAuth 2.0 authentication with modify permissions."""
        creds = None

        # Load existing token if available
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)

        # If no valid token, run the OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                   CLIENT_SECRET, SCOPES
                )
                creds = flow.run_local_server(port=0)  # Auto-handles OAuth flow

            # Save the token for next time
            with open(TOKEN, "w") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)
    
    def get_email_body(self, payload):
        """Extracts the email body from the payload."""
        return ""
    
     # def get_email_body(self,payload):
        # if "parts" in payload:
        #     # Multi-part email (plain text + HTML)
        #     for part in payload["parts"]:
        #         if part["mimeType"] == "text/plain":
        #             data = part["body"]["data"]
        #             return base64.urlsafe_b64decode(data).decode("utf-8")
        # else:
        #     # Single-part email
        #     data = payload["body"]["data"]
        #     return base64.urlsafe_b64decode(data).decode("utf-8")
        #   return ""

    def poll_new_emails(self):
        """Fetches new emails and can modify them (mark as read, etc.)."""
        try:
            print(f"\nChecking emails at {time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Fetch unread messages
            result = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=5)
                .execute()
            )
            messages = result.get("messages", [])

            if not messages:
                print("No new emails found.")
                return

            print(f"Found {len(messages)} new email(s):")

            for msg in messages:
                # Get email metadata
                email = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg["id"], format="metadata")
                    .execute()
                )

                headers = email["payload"]["headers"]
                subject = next(
                    (h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)"
                )
                sender = next(
                    (h["value"] for h in headers if h["name"] == "From"), "Unknown Sender"
                )
               
                msg_body = self.get_email_body(email["payload"])
                classified = self.email_classifier.classify_email(msg_body,sender,subject)

                print(f"\n📩 From: {sender}")
                print(f"📌 Subject: {subject[:80]}...")
                print(f"🔗 ID: {msg['id']}")
                print(f"🔖 Classified Label: {classified}"  )

                # Example: Mark as read by removing UNREAD label
                self.service.users().messages().modify(
                    userId="me",
                    id=msg["id"],
                    body={"removeLabelIds": ["UNREAD"]}
                ).execute()
                print("✅ Marked as read")

        except Exception as e:
            print(f"⚠️ Error: {e}")

    def start_polling(self, interval_minutes=5):
        """Starts periodic email polling with modify capabilities."""
        print(f"🚀 Gmail Poller Started (checking every {interval_minutes} minutes)...")
        print("🛑 Press Ctrl+C to stop\n")

        # Initial check
        self.poll_new_emails()

        # Schedule periodic checks
        schedule.every(interval_minutes).minutes.do(self.poll_new_emails)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Polling stopped by user")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gmail Poller")
    llm=ChatMistralAI(model="mistral:7b-instruct", temperature=0.0, endpoint="http://localhost:11434/v1")
    email_classifier = EmailClassifier(llm) 
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Polling interval in minutes (default: 5)"
    )
    args = parser.parse_args()

    poller = GmailPoller(email_classifier=email_classifier)
    poller.start_polling(interval_minutes=args.interval)