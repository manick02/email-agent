import os
import time
import argparse
from langchain_mistralai import ChatMistralAI   
import schedule
from email_classifier import EmailClassifier
from email_tools import EmailTools, EmailContentRequest  # <-- Use email_tools

class GmailPoller:
    def __init__(self, email_classifier):
        self.email_classifier = email_classifier
        self.email_tools = EmailTools()  # Use EmailTools for all Gmail operations

    def poll_new_emails(self):
        """Fetches new emails and can modify them (mark as read, etc.)."""
        try:
            print(f"\nChecking emails at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            msg_ids = self.email_tools.check_unread_emails("polling")

            if not msg_ids:
                print("No new emails found.")
                return

            print(f"Found {len(msg_ids)} new email(s):")

            for msg_id in msg_ids:
                content = self.email_tools.get_email_content(
                    EmailContentRequest(message_id=msg_id)
                )
                classified = self.email_classifier.classify_email(
                    content.body, content.sender, content.subject
                )

                print(f"\n📩 From: {content.sender}")
                print(f"📌 Subject: {content.subject[:80]}...")
                print(f"🔗 ID: {content.message_id}")
                print(f"🔖 Classified Label: {classified}")

                # Optionally, implement mark_as_read in EmailTools if needed

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
    llm = ChatMistralAI(model="mistral:7b-instruct", temperature=0.0, endpoint="http://localhost:11434/v1")
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