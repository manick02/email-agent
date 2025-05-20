# email_tools.py
import base64
import binascii
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.tools import tool
from googleapiclient.discovery import build
from google.auth.exceptions import GoogleAuthError
from credential_manager import get_gmail_service  # Add this import

# Configure logging
logger = logging.getLogger(__name__)

# ---------- Pydantic Models ---------- #
class EmailContent(BaseModel):
    """Structured email content with metadata"""
    message_id: str = Field(..., description="Unique Gmail message identifier")
    sender: str = Field(..., description="From address in format 'Name <email@domain>'")
    subject: str = Field("(No Subject)", description="Email subject line")
    body: str = Field(..., description="Decoded email body content")
    snippet: str = Field(..., description="Short preview from Gmail")

class EmailContentRequest(BaseModel):
    message_id: str
    purpose: str = Field("classification", description="Reason for retrieving content")

# ---------- Core Tools ---------- #
class EmailTools:
    def __init__(self):
        self.service = self._initialize_service()
        
    def _initialize_service(self):
        """Initialize Gmail service using credential_manager."""
        try:
            return get_gmail_service()  # Use your credential manager's function
        except Exception as e:
            logger.error(f"Gmail service initialization failed: {str(e)}")
            raise

    # @tool(
    #     args_schema=EmailContentRequest,
    #     handle_tool_error=True,
    #     return_direct=False
    # )
    def get_email_content(self, request: EmailContentRequest) -> EmailContent:
        """
        Retrieves structured email content with enhanced error handling.
        Use for agentic email processing workflows.
        """
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=request.message_id,
                format='full'
            ).execute()

            payload = msg['payload']
            headers = {h['name']: h['value'] for h in payload['headers']}
            
            return EmailContent(
                message_id=request.message_id,
                sender=headers.get('From', 'Unknown Sender'),
                subject=headers.get('Subject', '(No Subject)'),
                body=self._decode_email_body(payload),
                snippet=msg.get('snippet', '')
            )
            
        except (KeyError, binascii.Error) as e:
            logger.error(f"Decoding failed for {request.message_id}: {str(e)}")
            return EmailContent(
                message_id=request.message_id,
                sender="Decoding Error",
                subject="Content Unavailable",
                body=f"Error: {str(e)}",
                snippet=""
            )
        except Exception as e:
            logger.error(f"Failed to retrieve {request.message_id}: {str(e)}")
            raise

    def _decode_email_body(self, payload: dict) -> str:
        """Hierarchical email body decoding with fallbacks"""
        try:
            # Prioritize plain text parts
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        return self._safe_b64_decode(part['body']['data'])
            return self._safe_b64_decode(payload['body']['data'])
        except KeyError:
            return "Email body content unavailable"

    def _safe_b64_decode(self, data: str) -> str:
        """Safe Base64 decoding with error handling"""
        try:
            return base64.urlsafe_b64decode(data).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError) as e:
            logger.warning(f"Partial decode error: {str(e)}")
            return base64.urlsafe_b64decode(data + '==').decode('utf-8', 'replace')

   # @tool
    def check_unread_emails(self, reason: str) -> List[str]:
        """
        Check for unread emails with agentic context awareness.
        Returns list of message IDs requiring processing.
        """
        try:
            result = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=10
            ).execute()
            
            logger.info(f"Email check ({reason}) found {len(result.get('messages', []))} messages")
            return [msg['id'] for msg in result.get('messages', [])]
            
        except Exception as e:
            logger.error(f"Email check failed: {str(e)}")
            return []