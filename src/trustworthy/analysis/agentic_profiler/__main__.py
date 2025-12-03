from pathlib import Path

import click
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.sdk.tool import register_tool
from openhands.tools.preset.default import get_default_tools

from trustworthy.analysis.agentic_profiler.radar_chart_tool import RadarChartTool
from trustworthy.analysis.agentic_profiler.rubric import JUDGE_SYSTEM_INSTRUCTION

# Register the RadarChartTool
register_tool("RadarChartTool", RadarChartTool)

TOOLS = get_default_tools() + [Tool(name="RadarChartTool")]


@click.command()
@click.option("--dir", type=Path, required=True)
def main(dir: Path):
    """Analyze an AI system and assign a structured risk profile based on the established framework for characterizing AI agents."""
    llm = LLM(model="vertex_ai/gemini-2.5-pro")
    agent = Agent(llm=llm, tools=TOOLS)
    conversation = Conversation(agent=agent, workspace=dir.absolute())
    conversation.send_message(JUDGE_SYSTEM_INSTRUCTION)
    conversation.send_message(
        """
        1. Classify agent profile in the current working directory.
        2. Write a markdown report of the agent profile and save it to $prefix_agent_profile.md where prefix is the name of agent. 
        2. Write JSON results to $prefix_agent_profile.json.
        3. Create a radar chart of the agent profile and save it to $prefix_agent_profile.svg."""
    )
    conversation.run()
    print("All done!")


if __name__ == "__main__":
    main()
