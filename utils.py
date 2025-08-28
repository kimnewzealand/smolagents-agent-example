"""Utility functions for the Compliance Agent."""

import argparse
import json
import os
import yaml
from typing import Dict, Any
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel, PromptTemplates, PlanningPromptTemplate, ManagedAgentPromptTemplate, FinalAnswerPromptTemplate, DuckDuckGoSearchTool, FinalAnswerTool
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
            config = json.load(f)
            if not isinstance(config, dict):
                raise ValueError(f"Configuration must be a JSON object, got {type(config)}")
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Agent configuration file '{filepath}' not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in agent configuration: {e}")


def load_prompt_templates(filepath: str = "prompts.yaml") -> PromptTemplates:
    """Load prompt templates from YAML file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as stream:
            templates = yaml.safe_load(stream)
            
            prompt_templates = PromptTemplates(
                system_prompt=templates.get("system_prompt"),
                planning=PlanningPromptTemplate(templates
                ),
                managed_agent=ManagedAgentPromptTemplate(
                   templates.get("managed_agent")
                ),
                final_answer=FinalAnswerPromptTemplate(templates.get("final_answer"))
            )
            return prompt_templates
    except AttributeError as e:
        print(f"Error loading prompt templates: {e}")
        return PromptTemplates()
    except FileNotFoundError:
        print(f"⚠️ Warning: Prompt templates file '{filepath}' not found")
        return PromptTemplates()
    except Exception as e:
        print(f"Error loading prompt templates: {e}")
        return PromptTemplates()





def create_model_from_config(config: Dict[str, Any], api_key: str) -> LiteLLMModel:
    """Create model from agent.json configuration."""
    try:
        model_config = config["model"]
        
        # Handle both old and new config formats
        if isinstance(model_config, dict) and "data" in model_config:
            model_data = model_config["data"]
        else:
            model_data = model_config
            
        return LiteLLMModel(
            model_id=model_data["model_id"],
            api_key=api_key,
            max_tokens=model_data.get("max_tokens", 2096),
            temperature=model_data.get("temperature", 0.5),
        )
    except Exception as e:
        print(f"Error in create_model_from_config: {e}")
        print(f"Config structure: {config}")
        raise


def create_agent_from_config(config: Dict[str, Any], model: LiteLLMModel, current_period: str = None) -> CodeAgent:
    """Create agent from agent.json configuration and prompts.yaml templates."""
    try:
        # Instantiate actual tool objects instead of using strings
        tool_instances = []
        
        for tool_name in config["tools"]:
            if tool_name == "get_compliance_calendar":
                tool_instances.append(Get_Compliance_Calendar_Tool())
            elif tool_name == "web_search":
                tool_instances.append(DuckDuckGoSearchTool())
            elif tool_name == "final_answer":
                tool_instances.append(FinalAnswerTool())
        
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
            tools=tool_instances,
            max_steps=config.get("max_steps", 6),
            verbosity_level=config.get("verbosity_level", 1),
            prompt_templates=prompt_templates,
            planning_interval=config.get("planning_interval"),
            name=config.get("name"),
            description=agent_description,
            additional_authorized_imports=config.get("authorized_imports", []),
        )
    except Exception as e:
        print(f"Error in create_agent_from_config: {e}")
        raise



















