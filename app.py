"""Compliance Agent for New Zealand startup regulatory requirements."""

import argparse
import gradio as gr
from datetime import datetime
from typing import Dict, Any

from tools.get_calendar import Get_Compliance_Calendar_Tool
from eval import ComplianceAgentEvaluator
from utils import (
    load_environment, 
    load_agent_config, 
    load_prompt_templates,
    create_model_from_config,
    create_tools_from_config,
    create_agent_from_config
)


def create_gradio_interface():
    """Create Gradio interface for the compliance agent."""
    
    # Global agent variable to be set when date is selected
    current_agent = None
    
    def initialize_agent(month: int, year: int) -> str:
        """Initialize agent with selected date context."""
        nonlocal current_agent
        try:
            if not (1 <= month <= 12):
                return "❌ Month must be between 1 and 12"
            if year < 2020 or year > 2030:
                return "❌ Year must be between 2020 and 2030"
            
            # Load configuration and create agent
            config = load_agent_config()
            api_key = load_environment()
            model = create_model_from_config(config, api_key)
            
            month_name = datetime(year, month, 1).strftime("%B")
            current_period = f"{month_name} {year}"
            current_agent = create_agent_from_config(config, model, current_period)
            
            return f"✅ Agent initialized for {current_period}. You can now ask compliance questions!"
            
        except Exception as e:
            return f"❌ Failed to initialize agent: {str(e)}"
    
    def chat_with_agent(user_input: str) -> str:
        """Handle chat interaction with the agent."""
        nonlocal current_agent
        
        if current_agent is None:
            return "⚠️ Please initialize the agent first by setting the date context above."
        
        if not user_input.strip():
            return "Please enter a question about compliance."
        
        try:
            result = current_agent.run(user_input)
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
    
    def process_input(month: int, year: int, user_input: str):
        """Process both initialization and chat input."""
        # First initialize if needed
        if current_agent is None:
            init_result = initialize_agent(month, year)
            if "❌" in init_result:
                return init_result, ""
        
        # Then process the chat
        chat_result = chat_with_agent(user_input)
        return f"Agent Status: Ready for {datetime(int(year), int(month), 1).strftime('%B %Y')}", chat_result
    
    # Create simple interface using available components
    try:
        # Try using Interface if available
        demo = gr.Interface(
            fn=process_input,
            inputs=[
                gr.Number(label="Month (1-12)", value=datetime.now().month),
                gr.Number(label="Year", value=datetime.now().year),
                gr.Textbox(label="Ask about compliance", placeholder="e.g., What are the GST registration requirements?")
            ],
            outputs=[
                gr.Textbox(label="Agent Status"),
                gr.Textbox(label="Agent Response")
            ],
            title="🏢 NZ Startup Compliance Agent",
            description="Ask me about New Zealand startup regulatory requirements, tax obligations, and compliance deadlines."
        )
    except AttributeError:
        # Fallback to basic function if Interface not available
        print("⚠️ Gradio Interface not available, using basic setup")
        demo = gr.Interface(
            fn=lambda m, y, q: process_input(int(m), int(y), q),
            inputs=["number", "number", "text"],
            outputs=["text", "text"],
            title="🏢 NZ Startup Compliance Agent"
        )
    
    return demo


def run_interactive_session() -> None:
    """Run the interactive compliance agent session via Gradio UI."""
    print("🤖 Compliance Agent Ready!")
    print("🌐 Starting Gradio interface...")
    
    demo = create_gradio_interface()
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True,
        inbrowser=True
    )


def run_evaluation(config: Dict[str, Any]) -> None:
    """Run evaluation using the imported evaluator."""
    try:
        evaluator = ComplianceAgentEvaluator()
        summary = evaluator.run_evaluation()
        filepath = evaluator.save_results()
        
        print(f"\n📊 Evaluation Complete!")
        print(f"📁 Results saved to: {filepath}")
        print(f"\n📈 Summary:")
        print(f"  • Tests: {summary['summary_metrics']['successful_tests']}/{summary['summary_metrics']['total_tests']}")
        print(f"  • Success Rate: {summary['summary_metrics']['success_rate']:.1%}")
        print(f"  • Avg Quality: {summary['summary_metrics']['average_quality_score']:.1f}/5")
        print(f"  • Avg Time: {summary['summary_metrics']['average_execution_time']:.1f}s")
        
        print(f"\n📋 Category Breakdown:")
        for cat, data in summary['category_breakdown'].items():
            print(f"  • {cat}: {data['avg_quality']:.1f}/5 quality, {data['avg_time']:.1f}s avg")
            
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")


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
        
        if args.eval:
            # Run evaluation mode
            config = load_agent_config()
            print(f"✅ Loaded agent configuration with {len(config['tools'])} tools")
            run_evaluation(config)
        else:
            # Run interactive mode with Gradio UI
            run_interactive_session()
        
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return 1
    
    print("Goodbye! 👋")
    return 0


if __name__ == "__main__":
    exit(main())
