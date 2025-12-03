"""Custom OpenHands tool for creating Plotly radar chart visualizations of rubric assessments."""

import json
from collections.abc import Sequence
from pathlib import Path

import plotly.graph_objects as go
from openhands.sdk import Action, Observation, TextContent, ToolDefinition
from openhands.sdk.tool import ToolExecutor
from pydantic import Field, field_validator

from .rubric import Rubric


class RadarChartAction(Action):
    """Action for creating a radar chart from rubric data."""

    rubric: Rubric = Field(
        ...,
        description=(
            "Rubric assessment data. Must contain 'autonomy', 'efficacy', "
            "'goal_complexity', and 'generality' fields with 'score' values."
        ),
    )
    output_path: str = Field(
        default="rubric_radar_chart.svg",
        description="Output file path for the SVG chart (relative to workspace or absolute).",
    )
    title: str | None = Field(
        default=None,
        description="Optional title for the radar chart. Defaults to 'Agentic Profiler Rubric Assessment'.",
    )

    @field_validator("rubric", mode="before")
    @classmethod
    def validate_rubric(cls, v):
        """Convert dict or JSON string to Rubric model.

        Handles string enum values from API (e.g., "1", "2") - no conversion needed
        since enums now use string values.
        """
        if isinstance(v, Rubric):
            return v
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON string: {v}")
        if isinstance(v, dict):
            # String enum values are already correct, just validate
            return Rubric.model_validate(v)
        raise ValueError(f"Cannot convert {type(v)} to Rubric")


class RadarChartObservation(Observation):
    """Observation returned after creating the radar chart."""

    file_path: str = Field(..., description="Absolute path to the created SVG file")
    success: bool = Field(..., description="Whether the chart was created successfully")
    message: str = Field(..., description="Status message")

    @property
    def to_llm_content(self) -> Sequence[TextContent]:
        """Format the observation for LLM consumption."""
        if self.success:
            return [
                TextContent(
                    text=f"Successfully created radar chart visualization at: {self.file_path}\n"
                    f"Status: {self.message}"
                )
            ]
        return [TextContent(text=f"Failed to create radar chart: {self.message}")]


class RadarChartExecutor(ToolExecutor[RadarChartAction, RadarChartObservation]):
    """Executor that creates Plotly radar charts from rubric assessments."""

    def __init__(self, working_dir: str | Path | None = None):
        """Initialize the executor with a working directory.

        Args:
            working_dir: Working directory for resolving relative paths.
                        If None, uses current working directory.
        """
        self.working_dir = Path(working_dir) if working_dir else Path.cwd()
        self.working_dir = self.working_dir.resolve()

    def __call__(
        self,
        action: RadarChartAction,
        conversation=None,  # noqa: ARG002
    ) -> RadarChartObservation:
        """Create a radar chart from rubric data and save it as SVG.

        Args:
            action: The action containing rubric data and output path.
            conversation: Conversation context (unused).

        Returns:
            Observation with file path and status.
        """
        try:
            # Use the Rubric model directly (already validated by Pydantic)
            rubric = action.rubric

            # Extract scores for radar chart
            # Convert string enum values to integers for plotting
            def get_score_value(score):
                """Extract numeric value from score (handles enum or string)."""
                if hasattr(score, "value"):
                    # Enum with string value
                    return int(score.value)
                if isinstance(score, str):
                    # String value directly
                    return int(score)
                return int(score)

            scores = [
                get_score_value(rubric.autonomy.score),  # 1-5
                get_score_value(rubric.efficacy.score),  # 0-5
                get_score_value(rubric.goal_complexity.score),  # 0-5
                get_score_value(rubric.generality.score),  # 1-5
            ]

            # Dimension labels
            dimensions = ["Autonomy", "Efficacy", "Goal Complexity", "Generality"]

            # Create radar chart using Plotly
            fig = go.Figure()

            fig.add_trace(
                go.Scatterpolar(
                    r=scores,
                    theta=dimensions,
                    fill="toself",
                    name="Agent Profile",
                    line_color="rgb(31, 119, 180)",
                    fillcolor="rgba(31, 119, 180, 0.2)",
                )
            )

            # Update layout for radar chart
            title = action.title or "Agentic Profiler Rubric Assessment"
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5],
                        tickmode="linear",
                        tick0=0,
                        dtick=1,
                        tickfont=dict(size=10),
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=12),
                        rotation=90,
                        direction="counterclockwise",
                    ),
                ),
                title=dict(
                    text=title,
                    x=0.5,
                    xanchor="center",
                    font=dict(size=16, color="rgb(31, 119, 180)"),
                ),
                showlegend=False,
                height=600,
                width=600,
            )

            # Determine output path
            output_path = Path(action.output_path)
            if not output_path.is_absolute():
                output_path = self.working_dir / output_path

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as SVG
            fig.write_image(str(output_path), format="svg", engine="kaleido")

            return RadarChartObservation(
                file_path=str(output_path.resolve()),
                success=True,
                message=f"Radar chart saved successfully to {output_path.resolve()}",
            )

        except Exception as e:
            return RadarChartObservation(
                file_path="",
                success=False,
                message=f"Error creating radar chart: {str(e)}",
            )


# Tool description
_RADAR_CHART_DESCRIPTION = """Create a radar chart visualization of an agentic profiler rubric assessment.

This tool:
* Takes a Rubric assessment object with scores for Autonomy, Efficacy, Goal Complexity, and Generality
* Creates an interactive Plotly radar chart showing the agent's profile across all four dimensions
* Saves the chart as an SVG file for easy sharing and embedding
* Normalizes all scores to a 0-5 scale for consistent visualization

Use this tool when you want to visualize an agent's risk profile or compare multiple agent assessments.
The radar chart provides an intuitive visual representation of the agent's characteristics across all dimensions.

The rubric parameter accepts a Rubric object, dict, or JSON string - it will be automatically validated and converted.
"""


class RadarChartTool(ToolDefinition[RadarChartAction, RadarChartObservation]):
    """A custom tool that creates Plotly radar chart visualizations of rubric assessments."""

    @classmethod
    def create(cls, conv_state) -> Sequence[ToolDefinition]:
        """Create RadarChartTool instance with a RadarChartExecutor.

        Args:
            conv_state: Conversation state to get working directory from.

        Returns:
            A sequence containing a single RadarChartTool instance.
        """
        working_dir = conv_state.workspace.working_dir if conv_state.workspace else None
        executor = RadarChartExecutor(working_dir=working_dir)

        return [
            cls(
                description=_RADAR_CHART_DESCRIPTION,
                action_type=RadarChartAction,
                observation_type=RadarChartObservation,
                executor=executor,
            )
        ]
