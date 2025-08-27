from smolagents import CodeAgent, HfApiModel,tool

import yaml
from tools.final_answer import FinalAnswerTool

from Gradio_UI import GradioUI

@tool
def get_compliance_calendar() -> str:
    """
    Get key compliance calendar dates and deadlines for New Zealand startups.

    Returns:
        String with important compliance deadlines and requirements
    """
    calendar_info = """
📅 NEW ZEALAND STARTUP COMPLIANCE CALENDAR:

ANNUAL REQUIREMENTS:
• Annual Return: Due by anniversary of incorporation date
• Income Tax Return: Due 7 April (or extension date if applicable)
• Financial Statements: Must be completed within 5 months of balance date

ONGOING REQUIREMENTS (if applicable):
• GST Returns:
  - Monthly (if turnover >$24M)
  - 2-monthly (if turnover $500K-$24M)
  - 6-monthly (if turnover <$500K)
• PAYE Returns: Monthly (if employing staff)
• Provisional Tax: Payments due 28 Aug, 15 Jan, 7 May

EMPLOYMENT COMPLIANCE (if hiring):
• Employment agreements within first day of work
• Holiday and leave entitlements
• Health and safety requirements
• Minimum wage compliance

KEY THRESHOLDS:
• GST Registration: Required if turnover >$60,000
• PAYE: Required when paying employees/contractors >$200
• Company Registration: Required before starting business operations

IMPORTANT DATES 2024/2025:
• 28 August 2024: Provisional tax payment due
• 15 January 2025: Provisional tax payment due
• 7 April 2025: Income tax returns due
• 7 May 2025: Provisional tax payment due
"""
    return calendar_info


final_answer = FinalAnswerTool()

# If the agent does not answer, the model is overloaded, please use another model or the following Hugging Face Endpoint that also contains qwen2.5 coder:
# model_id='https://pflgm2locj2t89co.us-east-1.aws.endpoints.huggingface.cloud' 

model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',# it is possible that this model may be overloaded
custom_role_conversions=None,
)


with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[get_compliance_calendar,final_answer], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)


GradioUI(agent).launch()