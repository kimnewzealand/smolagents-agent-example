"""Simple evaluation script for the Compliance Agent."""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any

from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel

from tools.final_answer import FinalAnswerTool
from tools.get_calendar import Get_Compliance_Calendar_Tool
from tools.web_search import WebSearchTool


class ComplianceAgentEvaluator:
    """Simple evaluator for the compliance agent."""
    
    def __init__(self, config_path: str = "agent.json"):
        self.config = self._load_config(config_path)
        self.test_cases = self._load_test_cases()
        self.results = []
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration."""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
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
    
    def _create_agent(self) -> CodeAgent:
        """Create agent for evaluation."""
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        model_data = self.config["model"]["data"]
        model = LiteLLMModel(
            model_id=model_data["model_id"],
            api_key=api_key,
            max_tokens=model_data.get("max_tokens", 2096),
            temperature=model_data.get("temperature", 0.5),
        )
        
        tools = [
            Get_Compliance_Calendar_Tool(),
            WebSearchTool(),
            FinalAnswerTool(),
        ]
        
        return CodeAgent(
            model=model,
            tools=tools,
            max_steps=self.config.get("max_steps", 8),
            verbosity_level=0,  # Quiet for eval
            name=self.config.get("name"),
            description=self.config.get("description"),
        )
    
    def _evaluate_response(self, test_case: Dict, response: str, execution_time: float, tools_used: List[str]) -> Dict[str, Any]:
        """Evaluate a single response."""
        # Simple scoring metrics
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
    
    def run_evaluation(self) -> Dict[str, Any]:
        """Run the full evaluation suite."""
        print("🧪 Starting Compliance Agent Evaluation...")
        agent = self._create_agent()
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📝 Test {i}/{len(self.test_cases)}: {test_case['id']}")
            print(f"Query: {test_case['query']}")
            
            start_time = time.time()
            tools_used = []
            
            try:
                # Capture tools used during execution
                original_tools = agent.tools.copy()
                
                response = agent.run(test_case["query"])
                execution_time = time.time() - start_time
                
                # Extract tools used (simplified - would need agent instrumentation for full tracking)
                if "compliance calendar" in response.lower():
                    tools_used.append("get_compliance_calendar")
                if "search" in response.lower() or "recent" in response.lower():
                    tools_used.append("web_search")
                if response:  # Assume final_answer was used if we got a response
                    tools_used.append("final_answer")
                
                result = self._evaluate_response(test_case, response, execution_time, tools_used)
                self.results.append(result)
                
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
                self.results.append(error_result)
                print(f"❌ Failed: {str(e)}")
        
        return self._generate_summary()
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate evaluation summary."""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if "error" not in r])
        avg_quality = sum(r["quality_score"] for r in self.results) / total_tests if total_tests > 0 else 0
        avg_time = sum(r["execution_time"] for r in self.results) / total_tests if total_tests > 0 else 0
        
        summary = {
            "evaluation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "model_config": self.config["model"]["data"],
                "agent_config": {
                    "max_steps": self.config.get("max_steps"),
                    "tools": self.config.get("tools"),
                    "name": self.config.get("name")
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
            "category_breakdown": self._get_category_breakdown(),
            "detailed_results": self.results
        }
        
        return summary
    
    def _get_category_breakdown(self) -> Dict[str, Dict]:
        """Get performance breakdown by category."""
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"count": 0, "total_quality": 0, "total_time": 0}
            
            categories[cat]["count"] += 1
            categories[cat]["total_quality"] += result["quality_score"]
            categories[cat]["total_time"] += result["execution_time"]
        
        # Calculate averages
        for cat, data in categories.items():
            data["avg_quality"] = data["total_quality"] / data["count"]
            data["avg_time"] = data["total_time"] / data["count"]
        
        return categories
    
    def save_results(self, filename: str = None) -> str:
        """Save evaluation results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eval_results_{timestamp}.json"
        
        os.makedirs("eval_logs", exist_ok=True)
        filepath = os.path.join("eval_logs", filename)
        
        summary = self._generate_summary()
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return filepath


def main():
    """Run evaluation and save results."""
    evaluator = ComplianceAgentEvaluator()
    
    try:
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
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())