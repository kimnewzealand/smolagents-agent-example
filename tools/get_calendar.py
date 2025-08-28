
from smolagents.tools import Tool

class Get_Compliance_Calendar_Tool(Tool):
    name = "get_compliance_calendar"
    description = "Get key compliance calendar dates and deadlines for New Zealand startups. Returns important compliance deadlines and requirements."
    inputs = {}
    output_type = "string"
    
    def __init__(self):
        super().__init__()
        self.is_initialized = True

    def forward(self) -> str:
        calendar_info = """
📅 NEW ZEALAND STARTUP COMPLIANCE CALENDAR:

ONGOING REQUIREMENTS:
• GST Returns:
  - 6-monthly (turnover <$500K) due 5 Sep, 5 Feb
• PAYE Returns: Monthly
• Provisional Tax: Payments due 28 Aug, 15 Jan, 7 May

IMPORTANT DATES 2025/2026:

• 28 August 2025: Provisional tax payment due
• 15 January 2026: Provisional tax payment due
• 7 April 2026: Income tax returns due
• 7 May 2026: Provisional tax payment due
"""
        return calendar_info
