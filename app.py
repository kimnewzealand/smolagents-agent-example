"""Compliance Agent for New Zealand startup regulatory requirements."""

import gradio as gr

from utils import (
    load_environment, 
    parse_arguments,
    load_agent_config, 
    create_model_from_config,
    create_agent_from_config,
)


def create_compliance_agent():
    """Create compliance agent."""
    config = load_agent_config()
    api_key = load_environment()
    model = create_model_from_config(config, api_key)

    return create_agent_from_config(config, model)


def create_gradio_interface(agent):
    """Create Gradio interface for the compliance agent."""
    
    def chat_with_agent(user_input: str) -> str:
        """Handle chat interaction with the agent."""
        if not user_input.strip():
            return "Please enter a question about compliance."
        
        try:
            result = agent.run(user_input)
            return result
        except Exception as e:
            return f"❌ Error: {str(e)}\n💡 Try a simpler question or the model may be overloaded."

    def process_input(user_input: str):
        """Process chat input."""
        return chat_with_agent(user_input)
    
    # Create simple interface
    try:
        demo = gr.Interface(
            fn=process_input,
            inputs=[
                gr.Textbox(label="Ask about compliance", placeholder="e.g., What are the GST registration requirements?")
            ],
            outputs=[
                gr.Textbox(label="Agent Response")
            ],
            title="🏢 NZ Startup Compliance Agent",
            description="Ask me about New Zealand startup regulatory requirements, tax obligations, and compliance deadlines."
        )
    except AttributeError:
        demo = gr.Interface(
            fn=process_input,
            inputs=["text"],
            outputs=["text"],
            title="🏢 NZ Startup Compliance Agent"
        )
    
    return demo


def run_interactive_session(agent) -> None:
    """Run the interactive compliance agent session via Gradio UI."""
    print("🤖 Compliance Agent Ready!")
    print("🌐 Starting Gradio interface...")
    
    demo = create_gradio_interface(agent)
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        show_error=True,
        inbrowser=True
    )


def run_evaluation_in_app(agent) -> None:
    """Run evaluation using the imported evaluator."""
    try:
        from eval import ComplianceAgentEvaluator
        
        evaluator = ComplianceAgentEvaluator(agent)
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


def main() -> None:
    """Main application entry point."""
    try:
        args = parse_arguments()
        
        # Initialize agent once
        agent = create_compliance_agent()
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        return 1
    try:        
        if args.eval:
            # Run evaluation mode
            run_evaluation_in_app(agent)
        else:
            # Run interactive mode with Gradio UI
            run_interactive_session(agent)
        
    except Exception as e:
        print(f"❌ Failed to run application: {e}")
        return 1
    
    print("Goodbye! 👋")
    return 0


if __name__ == "__main__":
    exit(main())
