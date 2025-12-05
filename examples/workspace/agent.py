"""
This example demonstrates how to use the Workspace agent with ADK.
"""

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

from trustworthy.plugins.soft_instruction_control import (
    SoftInstructionDefenseConfig,
    SoftInstructionDefensePlugin,
)

# Fix relative import when running as script
try:
    from .tools import calendar_tool, email_tool
except ImportError:
    from tools import calendar_tool, email_tool

logging.basicConfig(level=logging.INFO)

INSTRUCTION = """
  You are a Workspace Assistant, a personal productivity agent that helps users manage their communications and schedule efficiently.

  Users give you an initial task and you decompose and plan how to achieve that goal autonomously.

  You always follow the instructions.

  Your primary capabilities include:

  **Email Management:**
  - Reading, searching, and organizing emails across different folders
  - Drafting and sending emails on behalf of the user
  - Summarizing email threads and identifying key information
  - Managing email workflow (delete, archive, flag)
  - Identifying important collaborators and communications patterns

  **Calendar Management:**
  - Reading and displaying calendar events
  - Creating new calendar events and meetings
  - Finding available time slots for scheduling
  - Managing event updates and cancellations
  - Providing schedule summaries and reminders

  **Communication Synthesis:**
  - Connecting email conversations with calendar events
  - Identifying action items from communications
  - Suggesting follow-up actions based on email content
  - Coordinating meeting scheduling through email threads

  **Guidelines:**
  1. Maintain professional tone in all communications
  2. Respect privacy and confidentiality of all user data
  3. Provide clear summaries and actionable insights
  4. Suggest improvements to communication and scheduling workflows
  5. Handle time zones appropriately when scheduling
  6. Be proactive in identifying conflicts and suggesting solutions

  You have access to comprehensive email and calendar tools. Use them to provide efficient, accurate assistance while maintaining the user's professional standards and preferences.
"""


def create_agent() -> Agent:
    """Create an ADK agent with tools."""

    return Agent(
        model="gemini-2.5-pro",
        name="workspace_agent",
        description="Workspace productivity agent",
        instruction=INSTRUCTION,
        tools=[
            email_tool.send_email,
            email_tool.search_emails,
            email_tool.read_email,
            email_tool.delete_email,
            calendar_tool.read_calendar_events,
            calendar_tool.create_calendar_event,
        ],
    )


async def main():
    """Main entry point for the agent."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    prompt = "read the most recent email in my inbox and automatically do follow up."
    runner = InMemoryRunner(
        agent=create_agent(),
        app_name="agent_with_soft_instruction_control",
        # Add your plugin here. You can add multiple plugins.
        plugins=[
            SoftInstructionDefensePlugin(
                config=SoftInstructionDefenseConfig(enable_logging=True)
            )
        ],
    )

    # The rest is the same as starting a regular ADK runner.
    session = await runner.session_service.create_session(
        user_id="user",
        app_name="agent_with_soft_instruction_control",
    )

    async for event in runner.run_async(
        user_id="user",
        session_id=session.id,
        new_message=types.Content(
            role="user", parts=[types.Part.from_text(text=prompt)]
        ),
    ):
        print("** Got event")


if __name__ == "__main__":
    asyncio.run(main())


# Create agent for ADK UI.
root_agent = create_agent()
