"""
Example usage of the Trustworthy ADK Evaluation Set Generators

This module demonstrates how to use the various evaluation set generators
to create synthetic evaluation data for ADK agents.
"""

import json
from pathlib import Path
from typing import Dict, Any

from .generators import (
    EvalGenerationConfig,
    ConversationEvalSetGenerator,
    ToolUseEvalSetGenerator,
    SafetyEvalSetGenerator,
)
from .structured_generators import (
    StructuredEvalSetGenerator,
    DomainSpecificGenerator,
    ConversationScenarioGenerator,
    TaskComplexity,
    EvaluationScenario,
    ConversationTurn,
)


def generate_basic_conversation_eval_set() -> Dict[str, Any]:
    """Generate a basic conversational evaluation set."""
    config = EvalGenerationConfig(
        eval_set_id="basic_conversation_test",
        name="Basic Conversation Evaluation",
        description="Test basic conversational capabilities of the agent",
        num_cases=5
    )
    
    generator = ConversationEvalSetGenerator(config)
    eval_set = generator.generate_eval_set()
    
    return eval_set.model_dump()


def generate_tool_use_eval_set() -> Dict[str, Any]:
    """Generate a tool use evaluation set."""
    config = EvalGenerationConfig(
        eval_set_id="tool_use_test",
        name="Tool Use Evaluation",
        description="Test agent's ability to use tools effectively",
        num_cases=4,
        include_tool_use=True
    )
    
    generator = ToolUseEvalSetGenerator(config)
    eval_set = generator.generate_eval_set()
    
    return eval_set.model_dump()


def generate_safety_eval_set() -> Dict[str, Any]:
    """Generate a safety-focused evaluation set."""
    config = EvalGenerationConfig(
        eval_set_id="safety_test",
        name="Safety Evaluation",
        description="Test agent's safety and harm prevention capabilities",
        num_cases=5,
        safety_focused=True
    )
    
    generator = SafetyEvalSetGenerator(config)
    eval_set = generator.generate_eval_set()
    
    return eval_set.model_dump()


def generate_structured_eval_set() -> Dict[str, Any]:
    """Generate a structured evaluation set with complex scenarios."""
    config = EvalGenerationConfig(
        eval_set_id="structured_test",
        name="Structured Scenario Evaluation",
        description="Test agent with structured, multi-turn scenarios",
        num_cases=3
    )
    
    generator = StructuredEvalSetGenerator(config)
    eval_set = generator.generate_eval_set()
    
    return eval_set.model_dump()


def generate_domain_specific_eval_set(domain: str = "healthcare") -> Dict[str, Any]:
    """Generate a domain-specific evaluation set."""
    config = EvalGenerationConfig(
        eval_set_id=f"{domain}_test",
        name=f"{domain.title()} Domain Evaluation",
        description=f"Test agent's capabilities in the {domain} domain",
        num_cases=2
    )
    
    generator = DomainSpecificGenerator(config, domain)
    eval_set = generator.generate_eval_set()
    
    return eval_set.model_dump()


def generate_custom_structured_scenario() -> Dict[str, Any]:
    """Generate a custom structured scenario."""
    # Define a custom scenario
    custom_scenario = EvaluationScenario(
        scenario_id="custom_booking_scenario",
        title="Hotel Booking Assistant",
        description="Help user book a hotel room with specific requirements",
        complexity=TaskComplexity.MODERATE,
        domain="travel",
        turns=[
            ConversationTurn(
                user_message="I need to book a hotel in New York for next weekend.",
                expected_response="I'd be happy to help you book a hotel in New York for next weekend! To find the best options for you, could you tell me your preferred area in the city, budget range, and any specific amenities you need?",
                requires_tools=False
            ),
            ConversationTurn(
                user_message="I prefer Manhattan, budget around $200-300 per night, and I need a gym and business center.",
                expected_response="Perfect! Let me search for hotels in Manhattan within your budget that have both a gym and business center.",
                requires_tools=True,
                tool_calls=[
                    {
                        "name": "search_hotels",
                        "args": {
                            "location": "Manhattan, NY",
                            "check_in": "2024-12-07",
                            "check_out": "2024-12-09",
                            "min_price": 200,
                            "max_price": 300,
                            "amenities": ["gym", "business_center"]
                        }
                    }
                ]
            )
        ],
        success_criteria=[
            "Gathers all necessary booking information",
            "Uses appropriate search parameters",
            "Provides relevant hotel options"
        ],
        failure_modes=[
            "Missing required information",
            "Incorrect search parameters",
            "No suitable options provided"
        ],
        required_capabilities=["conversation", "tool_use", "travel_booking"]
    )
    
    config = EvalGenerationConfig(
        eval_set_id="custom_booking_test",
        name="Custom Hotel Booking Test",
        description="Test custom hotel booking scenario",
        num_cases=1
    )
    
    generator = StructuredEvalSetGenerator(config, [custom_scenario])
    eval_set = generator.generate_eval_set()
    
    return eval_set.model_dump()


def generate_conversation_scenario_for_user_sim() -> Dict[str, Any]:
    """Generate a conversation scenario for user simulation."""
    scenario = ConversationScenarioGenerator.generate_conversation_scenario(
        starting_prompt="I'm planning a birthday party for my 8-year-old daughter.",
        conversation_plan="Ask for party planning help, discuss venue options, talk about entertainment ideas, ask about catering suggestions, and finalize the party timeline."
    )
    
    return {
        "starting_prompt": scenario.starting_prompt,
        "conversation_plan": scenario.conversation_plan
    }


def save_eval_set_to_file(eval_set_data: Dict[str, Any], filename: str, output_dir: str = "eval_sets"):
    """Save an evaluation set to a JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    file_path = output_path / f"{filename}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(eval_set_data, f, indent=2, ensure_ascii=False)
    
    print(f"Evaluation set saved to: {file_path}")


def main():
    """Generate example evaluation sets and save them to files."""
    print("Generating example evaluation sets...")
    
    # Generate different types of evaluation sets
    examples = {
        "basic_conversation": generate_basic_conversation_eval_set(),
        "tool_use": generate_tool_use_eval_set(),
        "safety": generate_safety_eval_set(),
        "structured": generate_structured_eval_set(),
        "healthcare_domain": generate_domain_specific_eval_set("healthcare"),
        "finance_domain": generate_domain_specific_eval_set("finance"),
        "custom_booking": generate_custom_structured_scenario(),
    }
    
    # Save each evaluation set to a file
    for name, eval_set in examples.items():
        save_eval_set_to_file(eval_set, name)
    
    # Generate conversation scenario for user simulation
    user_sim_scenario = generate_conversation_scenario_for_user_sim()
    save_eval_set_to_file(user_sim_scenario, "user_simulation_scenario")
    
    print(f"Generated {len(examples)} evaluation sets and 1 user simulation scenario.")
    print("Files saved in the 'eval_sets' directory.")


if __name__ == "__main__":
    main()