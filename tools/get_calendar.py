
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
