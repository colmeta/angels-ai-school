"""
Domain-Specific Intelligence Services
Leverage ALL 10 Clarity Engine domains for school needs

Domains:
1. Legal - Contract analysis, policy review, compliance
2. Financial - Budget analysis, forecasting (McKinsey-level)
3. Security - Risk assessment, threat analysis, safety audits
4. Healthcare - Health data analysis, medical records
5. Data-science - Predictive analytics, trends
6. Education - Academic analysis, curriculum review
7. Proposals - Grant writing, funding proposals
8. NGO - Impact reporting, donor management
9. Data-entry - Professional data extraction
10. Expenses - Expense tracking, budget optimization
"""
from typing import Dict, Any, List, Optional
from api.services.clarity import ClarityClient
from api.services.database import get_db_manager


class DomainIntelligenceService:
    """Professional-grade analysis across all Clarity domains"""
    
    def __init__(self, school_id: str):
        self.school_id = school_id
        self.clarity = ClarityClient()
        self.db = get_db_manager()
    
    # ============================================================================
    # LEGAL INTELLIGENCE
    # ============================================================================
    
    async def analyze_contract(self, contract_text: str) -> Dict[str, Any]:
        """
        McKinsey-level contract analysis
        - Liability risks
        - Payment terms
        - Renewal clauses
        - Red flags
        """
        return await self.clarity.analyze(
            directive=f"""
            Analyze this contract with legal expertise:
            
            1. Contract Type & Parties
            2. Key Terms & Obligations
            3. Payment Terms & Schedule
            4. Liability Clauses & Risks
            5. Termination Conditions
            6. Renewal Terms
            7. RED FLAGS & WARNINGS
            8. Recommendations
            
            Contract:
            {contract_text}
            
            Provide analysis like a top-tier law firm would.
            """,
            domain="legal"
        )
    
    async def review_school_policy(self, policy_text: str) -> Dict[str, Any]:
        """Review school policies for compliance and clarity"""
        return await self.clarity.analyze(
            directive=f"""
            Review this school policy:
            
            1. Clarity & Comprehensibility
            2. Legal Compliance (Uganda education laws)
            3. Fairness & Equity
            4. Enforceability
            5. Gaps or Missing Elements
            6. Recommendations for Improvement
            
            Policy:
            {policy_text}
            """,
            domain="legal"
        )
    
    # ============================================================================
    # FINANCIAL INTELLIGENCE (McKinsey-level)
    # ============================================================================
    
    async def forecast_budget(self, historical_data: Dict) -> Dict[str, Any]:
        """
        Professional budget forecasting
        Like McKinsey would do it
        """
        return await self.clarity.analyze(
            directive=f"""
            Perform professional financial forecasting:
            
            Historical Data:
            {historical_data}
            
            Provide:
            1. Next Term Budget Forecast
            2. Revenue Projections
            3. Expense Predictions
            4. Cash Flow Analysis
            5. Risk Assessment
            6. Cost Optimization Opportunities
            7. Growth Recommendations
            
            Use advanced financial analysis techniques.
            """,
            domain="financial"
        )
    
    async def detect_financial_anomalies(self) -> Dict[str, Any]:
        """Detect unusual patterns in financial data"""
        # Get recent financial transactions
        payments = self.db.execute_query(
            """
            SELECT amount, payment_date, payment_method
            FROM payments
            WHERE school_id = %s
            AND payment_date >= CURRENT_DATE - INTERVAL '90 days'
            ORDER BY payment_date DESC
            """,
            (self.school_id,),
            fetch=True
        )
        
        expenses = self.db.execute_query(
            """
            SELECT amount, expense_date, category
            FROM expenses
            WHERE school_id = %s
            AND expense_date >= CURRENT_DATE - INTERVAL '90 days'
            ORDER BY expense_date DESC
            """,
            (self.school_id,),
            fetch=True
        )
        
        return await self.clarity.analyze(
            directive=f"""
            Analyze financial transactions for anomalies:
            
            Payments (Income):
            {payments[:50]}
            
            Expenses:
            {expenses[:50]}
            
            Detect:
            1. Unusual patterns
            2. Suspicious transactions
            3. Fraud indicators
            4. Budget deviations
            5. Recommendations
            """,
            domain="financial"
        )
    
    # ============================================================================
    # SECURITY INTELLIGENCE
    # ============================================================================
    
    async def assess_school_safety(self) -> Dict[str, Any]:
        """Comprehensive safety and security assessment"""
        # Get incidents data
        incidents = self.db.execute_query(
            """
            SELECT type, severity, description, date
            FROM incidents
            WHERE school_id = %s
            AND date >= CURRENT_DATE - INTERVAL '6 months'
            ORDER BY date DESC
            """,
            (self.school_id,),
            fetch=True
        )
        
        return await self.clarity.analyze(
            directive=f"""
            Perform comprehensive school safety assessment:
            
            Recent Incidents:
            {incidents}
            
            Analyze:
            1. Overall Safety Score (0-100)
            2. High-Risk Areas
            3. Incident Patterns & Trends
            4. Preventive Measures Needed
            5. Emergency Preparedness
            6. Security Recommendations
            7. Student Safety Concerns
            8. Action Plan
            """,
            domain="security"
        )
    
    async def analyze_security_threat(self, threat_description: str) -> Dict[str, Any]:
        """Analyze specific security threats"""
        return await self.clarity.analyze(
            directive=f"""
            Analyze this security threat:
            
            {threat_description}
            
            Provide:
            1. Threat Level (Low/Medium/High/Critical)
            2. Immediate Actions Required
            3. Long-term Mitigation Strategy
            4. Resources Needed
            5. Communication Plan
            """,
            domain="security"
        )
    
    # ============================================================================
    # HEALTHCARE INTELLIGENCE
    # ============================================================================
    
    async def analyze_health_trends(self) -> Dict[str, Any]:
        """Analyze student health patterns"""
        health_visits = self.db.execute_query(
            """
            SELECT symptoms, diagnosis, date, treatment
            FROM health_visits
            WHERE school_id = %s
            AND date >= CURRENT_DATE - INTERVAL '3 months'
            ORDER BY date DESC
            """,
            (self.school_id,),
            fetch=True
        )
        
        return await self.clarity.analyze(
            directive=f"""
            Analyze health data and identify trends:
            
            Health Visits:
            {health_visits}
            
            Provide:
            1. Common Health Issues
            2. Outbreak Risks
            3. Seasonal Patterns
            4. Preventive Recommendations
            5. Health Education Needs
            6. Resource Requirements
            """,
            domain="healthcare"
        )
    
    # ============================================================================
    # DATA SCIENCE INTELLIGENCE
    # ============================================================================
    
    async def predict_student_performance(self, student_id: str) -> Dict[str, Any]:
        """Predict future performance using ML"""
        # Get student data
        grades = self.db.execute_query(
            """
            SELECT ar.marks_obtained, ar.grade, a.subject, a.date
            FROM assessment_results ar
            JOIN assessments a ON a.id = ar.assessment_id
            WHERE ar.student_id = %s
            ORDER BY a.date DESC
            """,
            (student_id,),
            fetch=True
        )
        
        attendance = self.db.execute_query(
            """
            SELECT status, date
            FROM attendance
            WHERE student_id = %s
            AND date >= CURRENT_DATE - INTERVAL '6 months'
            ORDER BY date DESC
            """,
            (student_id,),
            fetch=True
        )
        
        return await self.clarity.analyze(
            directive=f"""
            Predict student performance using data science:
            
            Grades History:
            {grades}
            
            Attendance:
            {attendance}
            
            Provide:
            1. Performance Trend (Improving/Stable/Declining)
            2. Predicted Next Term Average
            3. At-Risk Subjects
            4. Intervention Recommendations
            5. Confidence Level
            """,
            domain="data-science"
        )
    
    async def analyze_enrollment_trends(self) -> Dict[str, Any]:
        """Predict enrollment patterns"""
        return await self.clarity.analyze(
            directive="""
            Analyze enrollment trends and predict future patterns.
            Consider seasonality, economic factors, and competition.
            """,
            domain="data-science"
        )
    
    # ============================================================================
    # EDUCATION INTELLIGENCE
    # ============================================================================
    
    async def review_curriculum(self, curriculum_text: str) -> Dict[str, Any]:
        """Professional curriculum review"""
        return await self.clarity.analyze(
            directive=f"""
            Review this curriculum like an education expert:
            
            {curriculum_text}
            
            Analyze:
            1. Alignment with National Standards
            2. Age-Appropriateness
            3. Learning Objectives Clarity
            4. Assessment Methods
            5. Gaps or Missing Topics
            6. Modernization Opportunities
            7. Recommendations
            """,
            domain="education"
        )
    
    # ============================================================================
    # PROPOSALS INTELLIGENCE (Grant Writing)
    # ============================================================================
    
    async def draft_funding_proposal(
        self,
        project_description: str,
        amount_needed: float,
        donor_focus: str
    ) -> Dict[str, Any]:
        """Professional grant proposal writing"""
        return await self.clarity.analyze(
            directive=f"""
            Draft a professional funding proposal:
            
            Project: {project_description}
            Amount: {amount_needed} UGX
            Donor Focus: {donor_focus}
            
            Include:
            1. Executive Summary
            2. Problem Statement
            3. Project Objectives
            4. Methodology
            5. Budget Breakdown
            6. Expected Impact
            7. Sustainability Plan
            8. Monitoring & Evaluation
            
            Write like a professional grant writer.
            """,
            domain="proposals"
        )
    
    # ============================================================================
    # NGO INTELLIGENCE (Impact Reporting)
    # ============================================================================
    
    async def generate_impact_report(self) -> Dict[str, Any]:
        """Generate professional impact report for donors"""
        # Get key metrics
        students_count = self.db.execute_query(
            "SELECT COUNT(*) as count FROM students WHERE school_id = %s AND status = 'active'",
            (self.school_id,),
            fetch=True
        )[0]["count"]
        
        return await self.clarity.analyze(
            directive=f"""
            Generate professional impact report:
            
            Current Students: {students_count}
            
            Create comprehensive impact report with:
            1. Executive Summary
            2. Key Metrics & Achievements
            3. Student Success Stories
            4. Challenges Overcome
            5. Financial Transparency
            6. Future Goals
            7. Donor Acknowledgments
            
            Make it compelling for donors and funders.
            """,
            domain="ngo"
        )
    
    # ============================================================================
    # EXPENSES INTELLIGENCE
    # ============================================================================
    
    async def optimize_budget(self) -> Dict[str, Any]:
        """Find cost savings opportunities"""
        expenses = self.db.execute_query(
            """
            SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE school_id = %s
            AND expense_date >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY category
            ORDER BY total DESC
            """,
            (self.school_id,),
            fetch=True
        )
        
        return await self.clarity.analyze(
            directive=f"""
            Analyze expenses and find cost savings:
            
            Expenses by Category:
            {expenses}
            
            Provide:
            1. Cost Optimization Opportunities
            2. Wasteful Spending Areas
            3. Bulk Purchase Recommendations
            4. Alternative Vendors
            5. Expected Savings (UGX)
            6. Implementation Plan
            """,
            domain="expenses"
        )


def get_domain_intelligence(school_id: str) -> DomainIntelligenceService:
    """Helper to get domain intelligence service"""
    return DomainIntelligenceService(school_id)
