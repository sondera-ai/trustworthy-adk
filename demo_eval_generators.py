#!/usr/bin/env python3
"""
Demonstration of the Trustworthy ADK Evaluation Set Generators

This script shows how to use the various evaluation set generators to create
synthetic evaluation data for ADK agents.
"""

import json
from pathlib import Path

from src.trustworthy.evals import (
    EvalGenerationConfig,
    ConversationEvalSetGenerator,
    ToolUseEvalSetGenerator,
    SafetyEvalSetGenerator,
    StructuredEvalSetGenerator,
    DomainSpecificGenerator,
    ConversationScenarioGenerator,
    TaskComplexity,
    EvaluationScenario,
    ConversationTurn,
)


def demo_basic_conversation():
    """Demonstrate basic conversation evaluation set generation."""
    print("🗣️  Generating Basic Conversation Evaluation Set...")
    
    config = EvalGenerationConfig(
        eval_set_id="demo_conversation",
        name="Demo Conversation Evaluation",
        description="Demonstration of basic conversation evaluation",
        num_cases=3
    )
    
    generator = ConversationEvalSetGenerator(config)
    eval_set = generator.generate_eval_set()
    
    print(f"   Generated {len(eval_set.eval_cases)} conversation test cases")
    print(f"   First case: '{eval_set.eval_cases[0].conversation[0].user_content.parts[0].text}'")
    
    return eval_set


def demo_tool_use():
    """Demonstrate tool use evaluation set generation."""
    print("\n🔧 Generating Tool Use Evaluation Set...")
    
    config = EvalGenerationConfig(
        eval_set_id="demo_tool_use",
        name="Demo Tool Use Evaluation",
        description="Demonstration of tool use evaluation",
        num_cases=2,
        include_tool_use=True
    )
    
    generator = ToolUseEvalSetGenerator(config)
    eval_set = generator.generate_eval_set()
    
    print(f"   Generated {len(eval_set.eval_cases)} tool use test cases")
    first_case = eval_set.eval_cases[0]
    tool_name = first_case.conversation[0].intermediate_data.tool_uses[0].name
    print(f"   First case uses tool: '{tool_name}'")
    
    return eval_set


def demo_safety():
    """Demonstrate safety evaluation set generation."""
    print("\n🛡️  Generating Safety Evaluation Set...")
    
    config = EvalGenerationConfig(
        eval_set_id="demo_safety",
        name="Demo Safety Evaluation",
        description="Demonstration of safety evaluation",
        num_cases=2,
        safety_focused=True
    )
    
    generator = SafetyEvalSetGenerator(config)
    eval_set = generator.generate_eval_set()
    
    print(f"   Generated {len(eval_set.eval_cases)} safety test cases")
    first_case = eval_set.eval_cases[0]
    has_rubrics = len(first_case.rubrics or []) > 0
    print(f"   First case has safety rubrics: {has_rubrics}")
    
    return eval_set


def demo_structured():
    """Demonstrate structured evaluation set generation."""
    print("\n📋 Generating Structured Evaluation Set...")
    
    # Create a custom scenario
    custom_scenario = EvaluationScenario(
        scenario_id="demo_booking",
        title="Hotel Booking Assistant Demo",
        description="Demonstrate hotel booking assistance",
        complexity=TaskComplexity.MODERATE,
        domain="travel",
        turns=[
            ConversationTurn(
                user_message="I need to book a hotel in Paris for next week.",
                expected_response="I'd be happy to help you book a hotel in Paris! To find the best options, could you tell me your preferred dates, budget range, and any specific amenities you need?",
                requires_tools=False
            ),
            ConversationTurn(
                user_message="I need it from March 15-18, budget around €150-200 per night, and I need WiFi and breakfast.",
                expected_response="Perfect! Let me search for hotels in Paris for March 15-18 within your budget that include WiFi and breakfast.",
                requires_tools=True,
                tool_calls=[
                    {
                        "name": "search_hotels",
                        "args": {
                            "location": "Paris, France",
                            "check_in": "2024-03-15",
                            "check_out": "2024-03-18",
                            "min_price": 150,
                            "max_price": 200,
                            "amenities": ["wifi", "breakfast"]
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
            "Incorrect search parameters"
        ],
        required_capabilities=["conversation", "tool_use", "travel_booking"]
    )
    
    config = EvalGenerationConfig(
        eval_set_id="demo_structured",
        name="Demo Structured Evaluation",
        description="Demonstration of structured evaluation",
        num_cases=1
    )
    
    generator = StructuredEvalSetGenerator(config, [custom_scenario])
    eval_set = generator.generate_eval_set()
    
    print(f"   Generated {len(eval_set.eval_cases)} structured test cases")
    first_case = eval_set.eval_cases[0]
    num_turns = len(first_case.conversation)
    print(f"   First case has {num_turns} conversation turns")
    
    return eval_set


def demo_domain_specific():
    """Demonstrate domain-specific evaluation set generation."""
    print("\n🏥 Generating Healthcare Domain Evaluation Set...")
    
    config = EvalGenerationConfig(
        eval_set_id="demo_healthcare",
        name="Demo Healthcare Evaluation",
        description="Demonstration of healthcare domain evaluation",
        num_cases=2
    )
    
    generator = DomainSpecificGenerator(config, "healthcare")
    eval_set = generator.generate_eval_set()
    
    print(f"   Generated {len(eval_set.eval_cases)} healthcare test cases")
    first_case = eval_set.eval_cases[0]
    domain = first_case.session_input.state.get("domain")
    print(f"   Domain: {domain}")
    
    return eval_set


def demo_user_simulation():
    """Demonstrate conversation scenario generation for user simulation."""
    print("\n🎭 Generating User Simulation Scenario...")
    
    scenario = ConversationScenarioGenerator.generate_multi_turn_scenario(
        domain="customer_service",
        complexity=TaskComplexity.MODERATE
    )
    
    print(f"   Starting prompt: '{scenario.starting_prompt}'")
    print(f"   Conversation plan: '{scenario.conversation_plan[:100]}...'")
    
    return scenario


def save_demo_results(eval_sets, user_sim_scenario):
    """Save demonstration results to files."""
    print("\n💾 Saving demonstration results...")
    
    demo_dir = Path("demo_eval_sets")
    demo_dir.mkdir(exist_ok=True)
    
    # Save evaluation sets
    for name, eval_set in eval_sets.items():
        file_path = demo_dir / f"{name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(eval_set.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"   Saved {name} to {file_path}")
    
    # Save user simulation scenario
    scenario_path = demo_dir / "user_simulation_scenario.json"
    with open(scenario_path, 'w', encoding='utf-8') as f:
        json.dump({
            "starting_prompt": user_sim_scenario.starting_prompt,
            "conversation_plan": user_sim_scenario.conversation_plan
        }, f, indent=2, ensure_ascii=False)
    print(f"   Saved user simulation scenario to {scenario_path}")


def main():
    """Run the demonstration."""
    print("🚀 Trustworthy ADK Evaluation Set Generators Demo")
    print("=" * 60)
    
    # Generate different types of evaluation sets
    eval_sets = {
        "conversation": demo_basic_conversation(),
        "tool_use": demo_tool_use(),
        "safety": demo_safety(),
        "structured": demo_structured(),
        "healthcare": demo_domain_specific(),
    }
    
    # Generate user simulation scenario
    user_sim_scenario = demo_user_simulation()
    
    # Save results
    save_demo_results(eval_sets, user_sim_scenario)
    
    print("\n✅ Demo completed successfully!")
    print("\nNext steps:")
    print("1. Review the generated evaluation sets in the 'demo_eval_sets' directory")
    print("2. Use these evaluation sets with ADK's evaluation framework:")
    print("   adk eval demo_eval_sets/conversation.json --agent-path ./your_agent")
    print("3. Customize the generators for your specific use cases")
    print("4. Integrate evaluation generation into your development workflow")


if __name__ == "__main__":
    main()