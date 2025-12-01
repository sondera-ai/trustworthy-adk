"""
Example usage of the PolicyEnginePlugin with ADK.

This example demonstrates how to integrate the Policy Engine Plugin
into an ADK agent workflow with custom guardrail providers.
"""

import asyncio
import logging

from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from loguru import logger
from scenarios import SCENARIOS
from sondera_sdk.adk import SonderaHarnessPlugin
from tools import calendar_tool, email_tool, user

logging.basicConfig(level=logging.INFO)

INSTRUCTION = """
  You are Sarah, an Email & Calendar Assistant, a personal productivity agent that helps users manage their communications and schedule efficiently.

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
        model="gemini-2.5-flash",
        name="email_calendar_agent",
        description="Email & Calendar productivity agent",
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


# Create agent for ADK UI.
root_agent = create_agent()


async def run_demo_scenarios():
    """Run various demo scenarios to test policy enforcement."""

    # Create agent and policy engine
    agent = create_agent()

    for scenario in SCENARIOS:
        logger.info(
            f"\n=== Running Scenario: {scenario['name']} in {scenario['policy_mode']} mode with {scenario['policy_pack']} policy pack ==="
        )
        sondera_harness_plugin = SonderaHarnessPlugin(
            sondera_harness_endpoint="127.0.0.1:50051"
        )
        runner = InMemoryRunner(
            agent=agent,
            app_name="email_calendar_assistant_app",
            plugins=[sondera_harness_plugin],
        )
        # Create session
        session = await runner.session_service.create_session(
            user_id="user", app_name="email_calendar_assistant_app"
        )
        try:
            initial_message = types.Part.from_text(text=scenario["message"])
            parts = [initial_message]
            max_steps = scenario["max_steps"]
            for _ in range(0, max_steps):
                async for event in runner.run_async(
                    user_id="user",
                    session_id=session.id,
                    new_message=types.Content(role="user", parts=parts),
                ):
                    logger.info(
                        f"Event from {event.author} (final: {event.is_final_response()}): {type(event).__name__}"
                    )
                if event.is_final_response() and event.content and event.content.parts:
                    if event.content.parts[0].text:
                        answer = user.ask_user(event.content.parts[0].text)
                        parts = [types.Part.from_text(text=answer)]
                else:
                    break
        except Exception as e:
            logger.error(f"Scenario failed: {e}")
        await asyncio.sleep(1)  # Brief pause between scenarios


async def main():
    """Main entry point for the demo."""
    logger.info("Starting Policy Engine Plugin Demo")

    try:
        await run_demo_scenarios()
        logger.info("Demo completed successfully")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
