"""Utility functions for the Compliance Agent."""

import argparse
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel, PromptTemplates,DuckDuckGoSearchTool, FinalAnswerTool
from tools.get_calendar import Get_Compliance_Calendar_Tool


def load_environment() -> str:
    """Load environment variables and return API key."""
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    return api_key


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Compliance Agent for New Zealand startups")
    parser.add_argument(
        "--eval", 
        action="store_true", 
        help="Run evaluation mode instead of interactive session"
    )
    return parser.parse_args()


def load_agent_config(filepath: str = "agent.json") -> Dict[str, Any]:
    """Load agent configuration from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Agent configuration file '{filepath}' not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in agent configuration: {e}")


def load_prompt_templates(filepath: str = "prompts.yaml") -> PromptTemplates:
    """Load prompt templates from YAML file."""
    import yaml
    try:
        with open(filepath, 'r', encoding='utf-8') as stream:
            templates = yaml.safe_load(stream)
            return PromptTemplates(templates if templates else {})
    except FileNotFoundError:
        print(f"⚠️ Warning: Prompt templates file '{filepath}' not found")
        return PromptTemplates()


def create_model_from_config(config: Dict[str, Any], api_key: str) -> LiteLLMModel:
    """Create model from agent.json configuration."""
    model_config = config["model"]
    model_data = model_config["data"]
    
    return LiteLLMModel(
        model_id=model_data["model_id"],
        api_key=api_key,
        max_tokens=model_data.get("max_tokens", 2096),
        temperature=model_data.get("temperature", 0.5),
    )


def create_agent_from_config(config: Dict[str, Any], model: LiteLLMModel) -> CodeAgent:
    """Create agent from agent.json configuration and prompts.yaml templates."""
    # Instantiate actual tool objects instead of using strings
    tool_instances = []
    
    for tool_name in config["tools"]:
        if tool_name == "get_compliance_calendar":
            tool_instances.append(Get_Compliance_Calendar_Tool())
        elif tool_name == "compliance_web_search":
            tool_instances.append(DuckDuckGoSearchTool())
        elif tool_name == "final_answer":
            tool_instances.append(FinalAnswerTool())
    
    # Load prompt templates from prompts.yaml
    prompt_templates = load_prompt_templates()
    
    # Set agent description
    agent_description = config.get("description", "Compliance agent for New Zealand startups")
    
    return CodeAgent(
        model=model,
        tools=tool_instances,  # Use instantiated tools
        max_steps=config.get("max_steps", 6),
        verbosity_level=config.get("verbosity_level", 1),
        prompt_templates=prompt_templates,
        planning_interval=config.get("planning_interval"),
        name=config.get("name"),
        description=agent_description,
        additional_authorized_imports=config.get("authorized_imports", []),
    )


