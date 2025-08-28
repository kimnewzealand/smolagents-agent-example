"""Utility functions for the Compliance Agent."""

import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel

from tools.final_answer import FinalAnswerTool
from tools.get_calendar import Get_Compliance_Calendar_Tool
from tools.compliance_web_search import ComplianceWebSearchTool


def load_environment() -> str:
    """Load environment variables and return API key."""
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    return api_key


def load_agent_config(filepath: str = "agent.json") -> Dict[str, Any]:
    """Load agent configuration from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Agent configuration file '{filepath}' not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in agent configuration: {e}")


def load_prompt_templates(filepath: str = "prompts.yaml") -> dict:
    """Load prompt templates from YAML file."""
    import yaml
    try:
        with open(filepath, 'r', encoding='utf-8') as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        print(f"⚠️ Warning: Prompt templates file '{filepath}' not found, using defaults")
        return {}


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


def create_tools_from_config(tool_names: List[str]) -> List:
    """Create tool instances from tool names in config."""
    tool_mapping = {
        "get_compliance_calendar": Get_Compliance_Calendar_Tool,
        "compliance_web_search": ComplianceWebSearchTool,
        "final_answer": FinalAnswerTool,
    }
    
    tools = []
    for tool_name in tool_names:
        if tool_name in tool_mapping:
            tools.append(tool_mapping[tool_name]())
        else:
            print(f"⚠️ Warning: Tool '{tool_name}' not found in mapping")
    
    return tools


def create_agent_from_config(config: Dict[str, Any], model: LiteLLMModel, current_period: str = None) -> CodeAgent:
    """Create agent from agent.json configuration and prompts.yaml templates."""
    tools = create_tools_from_config(config["tools"])
    
    # Load prompt templates from prompts.yaml
    prompt_templates = load_prompt_templates()
    
    # Add current period context to agent description
    description = config.get("description", "Compliance agent for New Zealand startups")
    if current_period:
        agent_description = f"{description}. Current period: {current_period}"
    else:
        agent_description = description
    
    return CodeAgent(
        model=model,
        tools=tools,
        max_steps=config.get("max_steps", 6),
        verbosity_level=config.get("verbosity_level", 1),
        prompt_templates=prompt_templates,
        grammar=config.get("grammar"),
        planning_interval=config.get("planning_interval"),
        name=config.get("name"),
        description=agent_description,
        additional_authorized_imports=config.get("authorized_imports", []),
    )
