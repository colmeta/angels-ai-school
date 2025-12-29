from typing import Dict, Any, List
from api.services.database import get_db_manager

class CostAnalysisService:
    """
    Calculates the financial impact of using the AI System vs. Traditional Methods.
    Focuses on "Digital Savings" - money saved by not using paper/transport.
    """

    # Unit Costs (USD Est.) - Configurable per region in future
    COST_PHYSICAL_REPORT_CARD = 0.50  # Paper, printing, envelope
    COST_PHYSICAL_LETTER = 0.30       # Paper, envelope, delivery
    COST_PHYSICAL_RECEIPT = 0.15      # Receipt book leaf
    COST_PHYSICAL_INCIDENT_FORM = 0.10 # Printed disciplinary form
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.db = get_db_manager()

    def get_savings_dashboard(self) -> Dict[str, Any]:
        """
        Returns a comprehensive dashboard of savings.
        """
        # 1. Digital Reports Generated
        # Using 'assessment_results' to estimate unique report cards (student + term)
        report_data = self.db.execute_query(
            """SELECT COUNT(DISTINCT (student_id, term, year)) as total 
               FROM assessment_results 
               WHERE school_id = %s""",
            (self.school_id,), fetch=True
        )
        report_count = report_data[0]["total"] if report_data else 0
        
        # 2. Digital Communications (replacing Letters)
        # Using 'messages' table (SMS/Email)
        message_data = self.db.execute_query(
            "SELECT COUNT(*) as total FROM messages WHERE school_id = %s",
            (self.school_id,), fetch=True
        )
        message_count = message_data[0]["total"] if message_data else 0
        
        # 3. Digital Receipts (replacing Receipt Books)
        # Using 'payments' table
        payment_data = self.db.execute_query(
            "SELECT COUNT(*) as total FROM payments WHERE school_id = %s",
            (self.school_id,), fetch=True
        )
        receipt_count = payment_data[0]["total"] if payment_data else 0

        # 4. Digital Incident Reporting (replacing paper forms)
        # Using 'incidents' table
        incident_data = self.db.execute_query(
            "SELECT COUNT(*) as total FROM incidents WHERE school_id = %s",
            (self.school_id,), fetch=True
        )
        incident_count = incident_data[0]["total"] if incident_data else 0

        # Calculate Savings
        savings_reports = report_count * self.COST_PHYSICAL_REPORT_CARD
        savings_comms = message_count * self.COST_PHYSICAL_LETTER
        savings_receipts = receipt_count * self.COST_PHYSICAL_RECEIPT
        savings_incidents = incident_count * self.COST_PHYSICAL_INCIDENT_FORM
        
        total_savings = savings_reports + savings_comms + savings_receipts + savings_incidents

        return {
            "currency": "USD",
            "total_savings": round(total_savings, 2),
            "breakdown": {
                "reports": {
                    "count": report_count,
                    "unit_cost": self.COST_PHYSICAL_REPORT_CARD,
                    "saved": round(savings_reports, 2),
                    "label": "Digital Report Cards"
                },
                "communications": {
                    "count": message_count,
                    "unit_cost": self.COST_PHYSICAL_LETTER,
                    "saved": round(savings_comms, 2),
                    "label": "SMS & Emails"
                },
                "receipts": {
                    "count": receipt_count,
                    "unit_cost": self.COST_PHYSICAL_RECEIPT,
                    "saved": round(savings_receipts, 2),
                    "label": "Digital Receipts"
                },
                "incidents": {
                    "count": incident_count,
                    "unit_cost": self.COST_PHYSICAL_INCIDENT_FORM,
                    "saved": round(savings_incidents, 2),
                    "label": "Digital Incident Forms"
                }
            },
            "impact_statement": f"By going digital, you have saved approximately ${round(total_savings, 2)} in stationery and logistics costs."
        }
