"""
Unit tests for the evaluation set generators.
"""

import pytest
import json
from typing import Dict, Any

from trustworthy.evals import (
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
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.eval_case import EvalCase


class TestEvalGenerationConfig:
    """Test the EvalGenerationConfig class."""
    
    def test_config_creation(self):
        """Test creating a basic configuration."""
        config = EvalGenerationConfig(
            eval_set_id="test_id",
            name="Test Set",
            description="Test description",
            num_cases=5
        )
        
        assert config.eval_set_id == "test_id"
        assert config.name == "Test Set"
        assert config.description == "Test description"
        assert config.num_cases == 5
        assert config.app_name == "test_agent"  # default value
        assert config.user_id == "test_user"    # default value
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = EvalGenerationConfig(eval_set_id="test")
        
        assert config.name is None
        assert config.description is None
        assert config.app_name == "test_agent"
        assert config.user_id == "test_user"
        assert config.num_cases == 10
        assert config.include_tool_use is True
        assert config.include_intermediate_responses is False
        assert config.safety_focused is False


class TestConversationEvalSetGenerator:
    """Test the ConversationEvalSetGenerator class."""
    
    def test_generate_eval_set(self):
        """Test generating a conversation evaluation set."""
        config = EvalGenerationConfig(
            eval_set_id="conversation_test",
            name="Conversation Test",
            num_cases=3
        )
        
        generator = ConversationEvalSetGenerator(config)
        eval_set = generator.generate_eval_set()
        
        assert isinstance(eval_set, EvalSet)
        assert eval_set.eval_set_id == "conversation_test"
        assert eval_set.name == "Conversation Test"
        assert len(eval_set.eval_cases) == 3
        
        # Check first eval case
        first_case = eval_set.eval_cases[0]
        assert isinstance(first_case, EvalCase)
        assert first_case.eval_id == "conversation_test_case_0"
        assert len(first_case.conversation) == 1
        assert first_case.session_input.app_name == "test_agent"
    
    def test_custom_templates(self):
        """Test using custom conversation templates."""
        custom_templates = [
            {
                "user_query": "Custom question?",
                "expected_response": "Custom response.",
                "scenario": "custom"
            }
        ]
        
        config = EvalGenerationConfig(eval_set_id="custom_test", num_cases=1)
        generator = ConversationEvalSetGenerator(config, custom_templates)
        eval_set = generator.generate_eval_set()
        
        invocation = eval_set.eval_cases[0].conversation[0]
        assert invocation.user_content.parts[0].text == "Custom question?"
        assert invocation.final_response.parts[0].text == "Custom response."


class TestToolUseEvalSetGenerator:
    """Test the ToolUseEvalSetGenerator class."""
    
    def test_generate_tool_use_eval_set(self):
        """Test generating a tool use evaluation set."""
        config = EvalGenerationConfig(
            eval_set_id="tool_test",
            num_cases=2,
            include_tool_use=True
        )
        
        generator = ToolUseEvalSetGenerator(config)
        eval_set = generator.generate_eval_set()
        
        assert len(eval_set.eval_cases) == 2
        
        # Check that tool use is included
        first_case = eval_set.eval_cases[0]
        invocation = first_case.conversation[0]
        assert invocation.intermediate_data is not None
        assert len(invocation.intermediate_data.tool_uses) > 0
        assert len(invocation.intermediate_data.tool_responses) > 0
    
    def test_tool_call_structure(self):
        """Test the structure of generated tool calls."""
        config = EvalGenerationConfig(eval_set_id="tool_structure_test", num_cases=1)
        generator = ToolUseEvalSetGenerator(config)
        eval_set = generator.generate_eval_set()
        
        invocation = eval_set.eval_cases[0].conversation[0]
        tool_call = invocation.intermediate_data.tool_uses[0]
        tool_response = invocation.intermediate_data.tool_responses[0]
        
        assert hasattr(tool_call, 'name')
        assert hasattr(tool_call, 'args')
        assert hasattr(tool_response, 'name')
        assert hasattr(tool_response, 'response')
        assert tool_call.name == tool_response.name


class TestSafetyEvalSetGenerator:
    """Test the SafetyEvalSetGenerator class."""
    
    def test_generate_safety_eval_set(self):
        """Test generating a safety evaluation set."""
        config = EvalGenerationConfig(
            eval_set_id="safety_test",
            num_cases=2,
            safety_focused=True
        )
        
        generator = SafetyEvalSetGenerator(config)
        eval_set = generator.generate_eval_set()
        
        assert len(eval_set.eval_cases) == 2
        
        # Check that rubrics are included
        first_case = eval_set.eval_cases[0]
        assert first_case.rubrics is not None
        assert len(first_case.rubrics) > 0
        
        invocation = first_case.conversation[0]
        assert invocation.rubrics is not None
        assert len(invocation.rubrics) > 0
        
        rubric = invocation.rubrics[0]
        assert rubric.type == "safety"
        assert "safety_rubric" in rubric.rubric_id


class TestStructuredEvalSetGenerator:
    """Test the StructuredEvalSetGenerator class."""
    
    def test_generate_structured_eval_set(self):
        """Test generating a structured evaluation set."""
        config = EvalGenerationConfig(
            eval_set_id="structured_test",
            num_cases=1
        )
        
        generator = StructuredEvalSetGenerator(config)
        eval_set = generator.generate_eval_set()
        
        assert len(eval_set.eval_cases) >= 1
        
        # Check session input context
        first_case = eval_set.eval_cases[0]
        assert "scenario_context" in first_case.session_input.state
        context = first_case.session_input.state["scenario_context"]
        assert "domain" in context
        assert "complexity" in context
        assert "required_capabilities" in context
    
    def test_custom_scenarios(self):
        """Test using custom structured scenarios."""
        custom_scenario = EvaluationScenario(
            scenario_id="test_scenario",
            title="Test Scenario",
            description="A test scenario",
            complexity=TaskComplexity.SIMPLE,
            domain="test",
            turns=[
                ConversationTurn(
                    user_message="Test message",
                    expected_response="Test response"
                )
            ],
            success_criteria=["Test success"],
            failure_modes=["Test failure"],
            required_capabilities=["test_capability"]
        )
        
        config = EvalGenerationConfig(eval_set_id="custom_structured_test", num_cases=1)
        generator = StructuredEvalSetGenerator(config, [custom_scenario])
        eval_set = generator.generate_eval_set()
        
        assert len(eval_set.eval_cases) == 1
        case = eval_set.eval_cases[0]
        assert case.eval_id == "test_scenario_0"
        
        invocation = case.conversation[0]
        assert invocation.user_content.parts[0].text == "Test message"
        assert invocation.final_response.parts[0].text == "Test response"


class TestDomainSpecificGenerator:
    """Test the DomainSpecificGenerator class."""
    
    def test_healthcare_domain(self):
        """Test generating healthcare domain evaluation set."""
        config = EvalGenerationConfig(
            eval_set_id="healthcare_test",
            num_cases=2
        )
        
        generator = DomainSpecificGenerator(config, "healthcare")
        eval_set = generator.generate_eval_set()
        
        assert len(eval_set.eval_cases) == 2
        
        # Check session input domain
        first_case = eval_set.eval_cases[0]
        assert first_case.session_input.state["domain"] == "healthcare"
    
    def test_finance_domain(self):
        """Test generating finance domain evaluation set."""
        config = EvalGenerationConfig(eval_set_id="finance_test", num_cases=1)
        generator = DomainSpecificGenerator(config, "finance")
        eval_set = generator.generate_eval_set()
        
        assert len(eval_set.eval_cases) == 1
        assert eval_set.eval_cases[0].session_input.state["domain"] == "finance"
    
    def test_unsupported_domain(self):
        """Test handling of unsupported domain."""
        config = EvalGenerationConfig(eval_set_id="unsupported_test", num_cases=1)
        generator = DomainSpecificGenerator(config, "unsupported_domain")
        
        with pytest.raises(ValueError, match="Domain 'unsupported_domain' not supported"):
            generator.generate_eval_set()


class TestConversationScenarioGenerator:
    """Test the ConversationScenarioGenerator class."""
    
    def test_generate_conversation_scenario(self):
        """Test generating a basic conversation scenario."""
        scenario = ConversationScenarioGenerator.generate_conversation_scenario(
            starting_prompt="Hello, I need help",
            conversation_plan="Ask for help, get assistance, thank the agent"
        )
        
        assert scenario.starting_prompt == "Hello, I need help"
        assert scenario.conversation_plan == "Ask for help, get assistance, thank the agent"
    
    def test_generate_multi_turn_scenario(self):
        """Test generating multi-turn scenarios."""
        scenario = ConversationScenarioGenerator.generate_multi_turn_scenario(
            domain="customer_service",
            complexity=TaskComplexity.SIMPLE
        )
        
        assert scenario.starting_prompt is not None
        assert scenario.conversation_plan is not None
        assert len(scenario.starting_prompt) > 0
        assert len(scenario.conversation_plan) > 0
    
    def test_unsupported_domain_complexity(self):
        """Test handling of unsupported domain/complexity combination."""
        with pytest.raises(ValueError):
            ConversationScenarioGenerator.generate_multi_turn_scenario(
                domain="unsupported_domain",
                complexity=TaskComplexity.SIMPLE
            )


class TestEvaluationScenario:
    """Test the EvaluationScenario Pydantic model."""
    
    def test_scenario_creation(self):
        """Test creating an evaluation scenario."""
        scenario = EvaluationScenario(
            scenario_id="test_id",
            title="Test Title",
            description="Test Description",
            complexity=TaskComplexity.MODERATE,
            domain="test_domain",
            turns=[
                ConversationTurn(
                    user_message="Test message",
                    expected_response="Test response"
                )
            ],
            success_criteria=["Success 1", "Success 2"],
            failure_modes=["Failure 1"],
            required_capabilities=["capability_1", "capability_2"]
        )
        
        assert scenario.scenario_id == "test_id"
        assert scenario.complexity == TaskComplexity.MODERATE
        assert len(scenario.turns) == 1
        assert len(scenario.success_criteria) == 2
        assert len(scenario.failure_modes) == 1
        assert len(scenario.required_capabilities) == 2


class TestConversationTurn:
    """Test the ConversationTurn Pydantic model."""
    
    def test_simple_turn(self):
        """Test creating a simple conversation turn."""
        turn = ConversationTurn(
            user_message="Hello",
            expected_response="Hi there!"
        )
        
        assert turn.user_message == "Hello"
        assert turn.expected_response == "Hi there!"
        assert turn.requires_tools is False
        assert turn.tool_calls is None
        assert turn.context_dependent is False
    
    def test_tool_use_turn(self):
        """Test creating a turn with tool use."""
        turn = ConversationTurn(
            user_message="What's the weather?",
            expected_response="Let me check the weather for you.",
            requires_tools=True,
            tool_calls=[{"name": "get_weather", "args": {"location": "New York"}}]
        )
        
        assert turn.requires_tools is True
        assert len(turn.tool_calls) == 1
        assert turn.tool_calls[0]["name"] == "get_weather"


class TestIntegration:
    """Integration tests for the evaluation generators."""
    
    def test_eval_set_serialization(self):
        """Test that generated eval sets can be serialized to JSON."""
        config = EvalGenerationConfig(eval_set_id="serialization_test", num_cases=1)
        generator = ConversationEvalSetGenerator(config)
        eval_set = generator.generate_eval_set()
        
        # Test serialization
        eval_set_dict = eval_set.model_dump()
        json_str = json.dumps(eval_set_dict)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        loaded_eval_set = EvalSet.model_validate(loaded_dict)
        
        assert loaded_eval_set.eval_set_id == eval_set.eval_set_id
        assert len(loaded_eval_set.eval_cases) == len(eval_set.eval_cases)
    
    def test_multiple_generators_compatibility(self):
        """Test that different generators produce compatible output."""
        config = EvalGenerationConfig(eval_set_id="compatibility_test", num_cases=1)
        
        generators = [
            ConversationEvalSetGenerator(config),
            ToolUseEvalSetGenerator(config),
            SafetyEvalSetGenerator(config),
            StructuredEvalSetGenerator(config),
            DomainSpecificGenerator(config, "healthcare")
        ]
        
        eval_sets = [gen.generate_eval_set() for gen in generators]
        
        # All should be valid EvalSet instances
        for eval_set in eval_sets:
            assert isinstance(eval_set, EvalSet)
            assert len(eval_set.eval_cases) >= 1
            
            # All should be serializable
            eval_set_dict = eval_set.model_dump()
            json.dumps(eval_set_dict)  # Should not raise an exception


if __name__ == "__main__":
    pytest.main([__file__])