"""Simple evaluation script for the Compliance Agent."""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any


class ComplianceAgentEvaluator:
    """Simple evaluator for the compliance agent."""
    
    def __init__(self, agent=None):
        self.test_cases = self._load_test_cases()
        self.results = []
        self.agent = agent

    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Define test cases for evaluation."""
        return [
            {
                "id": "gst_requirements", 
                "query": "What are the GST requirements for my startup in New Zealand?",
                "expected_tools": ["get_compliance_calendar"],
                "category": "gst",
                "expected_output": {
                    "contains": ["GST", "registration", "$60,000", "15%"],
                    "mentions_threshold": True,
                    "mentions_rate": True,
                    "provides_deadline": True
                }
            },
            {
                "id": "upcoming_deadlines",
                "query": "What compliance deadlines are coming up in the next 3 months?",
                "expected_tools": ["get_compliance_calendar"],
                "category": "deadlines",
                "expected_output": {
                    "contains": ["deadline", "tax", "return"],
                    "mentions_dates": True,
                    "provides_calendar": True,
                    "actionable_items": True
                }
            }
        ]
    
    def _create_agent(self):
        """Use provided agent"""
        if self.agent:
            return self.agent
    
    def _evaluate_response(self, test_case: Dict, response: str, execution_time: float) -> Dict[str, Any]:
        """Evaluate a single response."""
        # Simple scoring metrics
        response_length = len(response)
        
        # Basic quality checks
        quality_score = 0
        if response_length > 50:  # Non-trivial response
            quality_score += 1
        if execution_time < 30:  # Reasonable response time
            quality_score += 1
        
        return {
            "test_id": test_case["id"],
            "category": test_case["category"],
            "query": test_case["query"],
            "response": response,
            "response_length": response_length,
            "execution_time": execution_time,
            "expected_tools": test_case["expected_tools"],
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
            
            try:
                response = agent.run(test_case["query"])
                execution_time = time.time() - start_time
                
                result = self._evaluate_response(test_case, response, execution_time)
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
                "agent_name": "NZ_Compliance_Agent",
                "evaluation_version": "1.0"
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






