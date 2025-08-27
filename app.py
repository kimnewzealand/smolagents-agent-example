"""Compliance Agent for New Zealand startup regulatory requirements."""

import argparse
import json
import os
import time
import gradio as gr
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel

from tools.final_answer import FinalAnswerTool
from tools.get_calendar import Get_Compliance_Calendar_Tool
from tools.web_search import WebSearchTool


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


def create_tools_from_config(tool_names: list) -> list:
    """Create tool instances from tool names in config."""
    tool_mapping = {
        "get_compliance_calendar": Get_Compliance_Calendar_Tool,
        "web_search": WebSearchTool,
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


def get_user_context() -> Tuple[str, str]:
    """Get current month and year from user input."""
    print("📅 Please provide current date context:")
    
    while True:
        try:
            month_input = input("Enter current month (1-12) or press Enter for current: ").strip()
            year_input = input("Enter current year (YYYY) or press Enter for current: ").strip()
            
            current_date = datetime.now()
            month = int(month_input) if month_input else current_date.month
            year = int(year_input) if year_input else current_date.year
            
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")
            if year < 2020 or year > 2030:
                raise ValueError("Year must be between 2020 and 2030")
                
            month_name = datetime(year, month, 1).strftime("%B")
            return f"{month_name} {year}", f"{year}-{month:02d}"
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}. Please try again.")
        except KeyboardInterrupt:
            print("\nUsing current date...")
            current_date = datetime.now()
            month_name = current_date.strftime("%B")
            return f"{month_name} {current_date.year}", f"{current_date.year}-{current_date.month:02d}"


def create_gradio_interface(agent: CodeAgent) -> gr.Interface:
    """Create Gradio interface for the compliance agent."""
    
    def chat_with_agent(user_input: str) -> str:
        """Handle chat interaction with the agent."""
        if not user_input.strip():
            return "Please enter a question about compliance."
        
        try:
            result = agent.run(user_input)
            return result
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}\n💡 Try a simpler question or the model may be overloaded."
            
            # Fallback to direct tool call
            try:
                calendar_tool = Get_Compliance_Calendar_Tool()
                calendar_info = calendar_tool.forward()
                return f"{error_msg}\n\n📅 Here's the compliance calendar:\n{calendar_info}"
            except Exception:
                return f"{error_msg}\n\nPlease try again later."
    
    # Create the interface
    demo = gr.Interface(
        fn=chat_with_agent,
        inputs=gr.Textbox(
            label="Ask about compliance",
            placeholder="e.g., What are the GST registration requirements for my startup?",
            lines=3
        ),
        outputs=gr.Textbox(
            label="Agent Response",
            lines=10
        ),
        title="🏢 NZ Startup Compliance Agent",
        description="Ask me about New Zealand startup regulatory requirements, tax obligations, and compliance deadlines.",
        examples=[
            "What are the key compliance dates for New Zealand startups?",
            "What are the GST registration requirements for my startup?",
            "Have there been any recent tax changes in New Zealand?",
            "What employment law compliance do I need for hiring my first employee?",
            "What are the steps to register a company in New Zealand?"
        ],
        theme=gr.themes.Soft(),
        flagging_mode="never"
    )
    
    return demo


def run_interactive_session(agent: CodeAgent) -> None:
    """Run the interactive compliance agent session via Gradio UI."""
    print("🤖 Compliance Agent Ready!")
    print("🌐 Starting Gradio interface...")
    
    demo = create_gradio_interface(agent)
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True
    )


def get_test_cases() -> List[Dict[str, Any]]:
    """Define test cases for evaluation."""
    return [
        {
            "id": "basic_calendar",
            "query": "What are the key compliance dates for New Zealand startups?",
            "expected_tools": ["get_compliance_calendar"],
            "category": "basic"
        },
        {
            "id": "gst_requirements", 
            "query": "What are the GST registration requirements for my startup?",
            "expected_tools": ["get_compliance_calendar"],
            "category": "tax"
        },
        {
            "id": "recent_changes",
            "query": "Have there been any recent tax changes in New Zealand?",
            "expected_tools": ["web_search", "get_compliance_calendar"],
            "category": "current"
        },
        {
            "id": "employment_law",
            "query": "What employment law compliance do I need for hiring my first employee?",
            "expected_tools": ["get_compliance_calendar", "web_search"],
            "category": "employment"
        },
        {
            "id": "company_registration",
            "query": "What are the steps to register a company in New Zealand?",
            "expected_tools": ["get_compliance_calendar"],
            "category": "registration"
        }
    ]


def evaluate_response(test_case: Dict, response: str, execution_time: float, tools_used: List[str]) -> Dict[str, Any]:
    """Evaluate a single response."""
    response_length = len(response)
    has_final_answer = "final_answer" in tools_used
    used_expected_tools = any(tool in tools_used for tool in test_case["expected_tools"])
    
    # Basic quality checks
    quality_score = 0
    if response_length > 50:  # Non-trivial response
        quality_score += 1
    if has_final_answer:  # Used final answer tool
        quality_score += 1
    if used_expected_tools:  # Used relevant tools
        quality_score += 2
    if execution_time < 30:  # Reasonable response time
        quality_score += 1
    
    return {
        "test_id": test_case["id"],
        "category": test_case["category"],
        "query": test_case["query"],
        "response": response,
        "response_length": response_length,
        "execution_time": execution_time,
        "tools_used": tools_used,
        "expected_tools": test_case["expected_tools"],
        "used_expected_tools": used_expected_tools,
        "has_final_answer": has_final_answer,
        "quality_score": quality_score,
        "max_quality_score": 5,
        "timestamp": datetime.now().isoformat()
    }


def run_evaluation(config: Dict[str, Any]) -> None:
    """Run evaluation mode."""
    print("🧪 Starting Compliance Agent Evaluation...")
    
    # Create agent for evaluation
    api_key = load_environment()
    model = create_model_from_config(config, api_key)
    agent = create_agent_from_config(config, model)
    agent.verbosity_level = 0  # Quiet for eval
    
    test_cases = get_test_cases()
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n� Test {i}/{len(test_cases)}: {test_case['id']}")
        print(f"Query: {test_case['query']}")
        
        start_time = time.time()
        tools_used = []
        
        try:
            response = agent.run(test_case["query"])
            execution_time = time.time() - start_time
            
            # Extract tools used (simplified detection)
            if "compliance calendar" in response.lower():
                tools_used.append("get_compliance_calendar")
            if "search" in response.lower() or "recent" in response.lower():
                tools_used.append("web_search")
            if response:  # Assume final_answer was used if we got a response
                tools_used.append("final_answer")
            
            result = evaluate_response(test_case, response, execution_time, tools_used)
            results.append(result)
            
            print(f"✅ Completed in {execution_time:.2f}s")
            print(f"Quality Score: {result['quality_score']}/{result['max_quality_score']}")
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = {
                "test_id": test_case["id"],
                "category": test_case["category"],
                "query": test_case["query"],
                "response": f"ERROR: {str(e)}",
                "execution_time": execution_time,
                "tools_used": [],
                "error": str(e),
                "quality_score": 0,
                "max_quality_score": 5,
                "timestamp": datetime.now().isoformat()
            }
            results.append(error_result)
            print(f"❌ Failed: {str(e)}")
    
    # Generate summary and save results
    save_evaluation_results(config, results)


def save_evaluation_results(config: Dict[str, Any], results: List[Dict]) -> None:
    """Save evaluation results to file."""
    total_tests = len(results)
    successful_tests = len([r for r in results if "error" not in r])
    avg_quality = sum(r["quality_score"] for r in results) / total_tests if total_tests > 0 else 0
    avg_time = sum(r["execution_time"] for r in results) / total_tests if total_tests > 0 else 0
    
    # Category breakdown
    categories = {}
    for result in results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "total_quality": 0, "total_time": 0}
        
        categories[cat]["count"] += 1
        categories[cat]["total_quality"] += result["quality_score"]
        categories[cat]["total_time"] += result["execution_time"]
    
    for cat, data in categories.items():
        data["avg_quality"] = data["total_quality"] / data["count"]
        data["avg_time"] = data["total_time"] / data["count"]
    
    summary = {
        "evaluation_metadata": {
            "timestamp": datetime.now().isoformat(),
            "model_config": config["model"]["data"],
            "agent_config": {
                "max_steps": config.get("max_steps"),
                "tools": config.get("tools"),
                "name": config.get("name")
            }
        },
        "summary_metrics": {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
            "average_quality_score": avg_quality,
            "average_execution_time": avg_time,
            "max_quality_score": 5
        },
        "category_breakdown": categories,
        "detailed_results": results
    }
    
    # Save to file
    os.makedirs("eval_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join("eval_logs", f"eval_results_{timestamp}.json")
    
    with open(filepath, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\n📊 Evaluation Complete!")
    print(f"📁 Results saved to: {filepath}")
    print(f"\n📈 Summary:")
    print(f"  • Tests: {successful_tests}/{total_tests}")
    print(f"  • Success Rate: {summary['summary_metrics']['success_rate']:.1%}")
    print(f"  • Avg Quality: {avg_quality:.1f}/5")
    print(f"  • Avg Time: {avg_time:.1f}s")
    
    print(f"\n📋 Category Breakdown:")
    for cat, data in categories.items():
        print(f"  • {cat}: {data['avg_quality']:.1f}/5 quality, {data['avg_time']:.1f}s avg")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Compliance Agent for New Zealand startups")
    parser.add_argument(
        "--eval", 
        action="store_true", 
        help="Run evaluation mode instead of interactive session"
    )
    return parser.parse_args()


def main() -> None:
    """Main application entry point."""
    try:
        args = parse_arguments()
        
        # Load configuration from agent.json
        config = load_agent_config()
        print(f"✅ Loaded agent configuration with {len(config['tools'])} tools")
        
        if args.eval:
            # Run evaluation mode
            run_evaluation(config)
        else:
            # Run interactive mode with Gradio UI
            current_period, period_code = get_user_context()
            print(f"✅ Using period: {current_period}\n")
            
            api_key = load_environment()
            model = create_model_from_config(config, api_key)
            agent = create_agent_from_config(config, model, current_period)
            
            print(f"🔧 Agent initialized with tools: {', '.join(config['tools'])}")
            run_interactive_session(agent)
        
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return 1
    
    print("Goodbye! 👋")
    return 0


if __name__ == "__main__":
    exit(main())
