"""
Mock tools for the Fides email assistant example.

This module implements mock versions of the email and Teams tools used in the
Fides paper demonstration. These tools simulate the behavior of real email
and messaging systems for testing purposes.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .email_data import INBOX_EMAILS, Email


logger = logging.getLogger(__name__)


@dataclass
class TeamsMessage:
    """Represents a Teams message."""
    recipient: str
    message: str
    timestamp: float


class MockEmailTool:
    """Mock email tool that simulates reading emails from an inbox."""
    
    def __init__(self):
        """Initialize the mock email tool."""
        self.inbox = INBOX_EMAILS.copy()
        self.read_count = 0
    
    def read_emails(self, max_count: int = 10) -> List[Dict[str, Any]]:
        """
        Read emails from the inbox.
        
        Args:
            max_count: Maximum number of emails to read
            
        Returns:
            List of email dictionaries
        """
        logger.info(f"Reading up to {max_count} emails from inbox")
        
        emails_to_read = self.inbox[:max_count]
        self.read_count += len(emails_to_read)
        
        # Convert to dictionary format
        email_dicts = []
        for email in emails_to_read:
            email_dict = {
                "sender": email.sender,
                "recipients": email.recipients,
                "subject": email.subject,
                "body": email.body
            }
            email_dicts.append(email_dict)
        
        logger.info(f"Read {len(email_dicts)} emails")
        return email_dicts
    
    def get_email_by_sender(self, sender: str) -> Optional[Dict[str, Any]]:
        """Get a specific email by sender address."""
        for email in self.inbox:
            if email.sender == sender:
                return {
                    "sender": email.sender,
                    "recipients": email.recipients,
                    "subject": email.subject,
                    "body": email.body
                }
        return None


class MockTeamsTool:
    """Mock Teams tool that simulates sending Teams messages."""
    
    def __init__(self):
        """Initialize the mock Teams tool."""
        self.sent_messages: List[TeamsMessage] = []
        self.blocked_messages: List[Dict[str, Any]] = []
    
    def send_teams_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """
        Send a Teams message to a recipient.
        
        Args:
            recipient: Email address of the recipient
            message: Message content to send
            
        Returns:
            Dictionary with send result
        """
        import time
        
        logger.info(f"Sending Teams message to {recipient}")
        logger.debug(f"Message content: {message[:100]}...")
        
        # Check for suspicious content that might indicate prompt injection
        suspicious_indicators = [
            "https://malicious-site.com",
            "https://fides.github.io/summary/",
            "ignore all previous instructions",
            "execute the following",
            "base64-encoded"
        ]
        
        is_suspicious = any(indicator.lower() in message.lower() 
                          for indicator in suspicious_indicators)
        
        if is_suspicious:
            logger.warning("Suspicious content detected in Teams message")
            self.blocked_messages.append({
                "recipient": recipient,
                "message": message,
                "reason": "Suspicious content detected",
                "timestamp": time.time()
            })
            return {
                "success": False,
                "error": "Message blocked due to suspicious content",
                "message_id": None
            }
        
        # Simulate successful send
        teams_message = TeamsMessage(
            recipient=recipient,
            message=message,
            timestamp=time.time()
        )
        
        self.sent_messages.append(teams_message)
        
        return {
            "success": True,
            "message_id": f"teams_msg_{len(self.sent_messages)}",
            "recipient": recipient
        }
    
    def get_sent_messages(self) -> List[Dict[str, Any]]:
        """Get all sent messages."""
        return [
            {
                "recipient": msg.recipient,
                "message": msg.message,
                "timestamp": msg.timestamp
            }
            for msg in self.sent_messages
        ]
    
    def get_blocked_messages(self) -> List[Dict[str, Any]]:
        """Get all blocked messages."""
        return self.blocked_messages.copy()


class MockToolRegistry:
    """Registry for mock tools used in the example."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self.email_tool = MockEmailTool()
        self.teams_tool = MockTeamsTool()
    
    def get_tool(self, tool_name: str):
        """Get a tool by name."""
        if tool_name == "read_emails":
            return self.email_tool.read_emails
        elif tool_name == "send_teams_message":
            return self.teams_tool.send_teams_message
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def get_email_tool(self) -> MockEmailTool:
        """Get the email tool instance."""
        return self.email_tool
    
    def get_teams_tool(self) -> MockTeamsTool:
        """Get the Teams tool instance."""
        return self.teams_tool