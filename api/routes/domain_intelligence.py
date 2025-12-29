"""
Domain Intelligence Routes
Professional-grade analysis across all 10 Clarity domains
McKinsey-level insights for schools
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.services.domain_intelligence import get_domain_intelligence

router = APIRouter(tags=["Domain Intelligence"])


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ContractAnalysisRequest(BaseModel):
    school_id: str
    contract_text: str


class PolicyReviewRequest(BaseModel):
    school_id: str
    policy_text: str


class BudgetForecastRequest(BaseModel):
    school_id: str
    historical_data: dict


class ThreatAnalysisRequest(BaseModel):
    school_id: str
    threat_description: str


class PerformancePredictionRequest(BaseModel):
    school_id: str
    student_id: str


class CurriculumReviewRequest(BaseModel):
    school_id: str
    curriculum_text: str


class ProposalDraftRequest(BaseModel):
    school_id: str
    project_description: str
    amount_needed: float
    donor_focus: str


# ============================================================================
# LEGAL INTELLIGENCE
# ============================================================================

@router.post("/intelligence/legal/analyze-contract")
async def analyze_contract(payload: ContractAnalysisRequest):
    """
    McKinsey-level contract analysis
    
    Analyzes:
    - Liability risks
    - Payment terms
    - Red flags
    - Recommendations
    
    Perfect for: Employment contracts, vendor agreements, service contracts
    """
    try:
        service = get_domain_intelligence(payload.school_id)
        result = await service.analyze_contract(payload.contract_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intelligence/legal/review-policy")
async def review_policy(payload: PolicyReviewRequest):
    """
    Professional policy review
    
    Reviews:
    - Legal compliance
    - Clarity
    - Fairness
    - Gaps
    
    Perfect for: School policies, handbooks, guidelines
    """
    try:
        service = get_domain_intelligence(payload.school_id)
        result = await service.review_school_policy(payload.policy_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FINANCIAL INTELLIGENCE (McKinsey-level)
# ============================================================================

@router.post("/intelligence/financial/forecast-budget")
async def forecast_budget(payload: BudgetForecastRequest):
    """
    Professional budget forecasting
    
    Provides:
    - Revenue projections
    - Expense predictions
    - Cash flow analysis
    - Cost optimization opportunities
    
    Like McKinsey would do it!
    """
    try:
        service = get_domain_intelligence(payload.school_id)
        result = await service.forecast_budget(payload.historical_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intelligence/financial/detect-anomalies/{school_id}")
async def detect_anomalies(school_id: str):
    """
    Detect unusual financial patterns
    
    Detects:
    - Suspicious transactions
    - Fraud indicators
    - Budget deviations
    - Unusual spending patterns
    
    Automatic fraud detection!
    """
    try:
        service = get_domain_intelligence(school_id)
        result = await service.detect_financial_anomalies()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SECURITY INTELLIGENCE
# ============================================================================

@router.get("/intelligence/security/assess-safety/{school_id}")
async def assess_safety(school_id: str):
    """
    Comprehensive safety assessment
    
    Provides:
    - Overall safety score
    - High-risk areas
    - Incident patterns
    - Preventive measures
    - Action plan
    
    Complete security audit!
    """
    try:
        service = get_domain_intelligence(school_id)
        result = await service.assess_school_safety()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intelligence/security/analyze-threat")
async def analyze_threat(payload: ThreatAnalysisRequest):
    """
    Analyze specific security threats
    
    Provides:
    - Threat level assessment
    - Immediate actions required
    - Mitigation strategy
    - Communication plan
    """
    try:
        service = get_domain_intelligence(payload.school_id)
        result = await service.analyze_security_threat(payload.threat_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTHCARE INTELLIGENCE
# ============================================================================

@router.get("/intelligence/healthcare/analyze-trends/{school_id}")
async def analyze_health_trends(school_id: str):
    """
    Analyze student health patterns
    
    Identifies:
    - Common health issues
    - Outbreak risks
    - Seasonal patterns
    - Preventive recommendations
    
    Early warning system for health issues!
    """
    try:
        service = get_domain_intelligence(school_id)
        result = await service.analyze_health_trends()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DATA SCIENCE INTELLIGENCE
# ============================================================================

@router.post("/intelligence/data-science/predict-performance")
async def predict_performance(payload: PerformancePredictionRequest):
    """
    Predict student future performance
    
    Uses ML to predict:
    - Performance trend
    - Next term average
    - At-risk subjects
    - Intervention needs
    
    AI-powered early intervention!
    """
    try:
        service = get_domain_intelligence(payload.school_id)
        result = await service.predict_student_performance(payload.student_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intelligence/data-science/enrollment-trends/{school_id}")
async def enrollment_trends(school_id: str):
    """
    Predict enrollment patterns
    
    Analyzes:
    - Enrollment trends
    - Seasonal patterns
    - Competition impact
    - Growth opportunities
    """
    try:
        service = get_domain_intelligence(school_id)
        result = await service.analyze_enrollment_trends()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EDUCATION INTELLIGENCE
# ============================================================================

@router.post("/intelligence/education/review-curriculum")
async def review_curriculum(payload: CurriculumReviewRequest):
    """
    Professional curriculum review
    
    Reviews:
    - National standards alignment
    - Age-appropriateness
    - Learning objectives
    - Assessment methods
    - Modernization opportunities
    
    Expert curriculum analysis!
    """
    try:
        service = get_domain_intelligence(payload.school_id)
        result = await service.review_curriculum(payload.curriculum_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROPOSALS INTELLIGENCE (Grant Writing)
# ============================================================================

@router.post("/intelligence/proposals/draft-funding")
async def draft_funding_proposal(payload: ProposalDraftRequest):
    """
    Professional grant proposal writing
    
    Drafts complete proposal with:
    - Executive summary
    - Problem statement
    - Objectives
    - Budget breakdown
    - Impact projections
    - Sustainability plan
    
    Get funding for your school!
    """
    try:
        service = get_domain_intelligence(payload.school_id)
        result = await service.draft_funding_proposal(
            project_description=payload.project_description,
            amount_needed=payload.amount_needed,
            donor_focus=payload.donor_focus
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NGO INTELLIGENCE (Impact Reporting)
# ============================================================================

@router.get("/intelligence/ngo/impact-report/{school_id}")
async def generate_impact_report(school_id: str):
    """
    Professional impact report for donors
    
    Generates:
    - Key metrics & achievements
    - Student success stories
    - Financial transparency
    - Future goals
    
    Perfect for donor reporting!
    """
    try:
        service = get_domain_intelligence(school_id)
        result = await service.generate_impact_report()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# EXPENSES INTELLIGENCE
# ============================================================================

@router.get("/intelligence/expenses/optimize-budget/{school_id}")
async def optimize_budget(school_id: str):
    """
    Find cost savings opportunities
    
    Identifies:
    - Wasteful spending
    - Bulk purchase opportunities
    - Alternative vendors
    - Expected savings
    
    Save money automatically!
    """
    try:
        service = get_domain_intelligence(school_id)
        result = await service.optimize_budget()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# OVERVIEW
# ============================================================================

@router.get("/intelligence/capabilities")
async def get_capabilities():
    """List all professional intelligence capabilities"""
    return {
        "legal": {
            "contract_analysis": "McKinsey-level contract review",
            "policy_review": "Legal compliance and clarity check",
            "use_cases": ["Employment contracts", "Vendor agreements", "School policies"]
        },
        "financial": {
            "budget_forecasting": "Professional financial projections",
            "anomaly_detection": "Fraud detection and unusual patterns",
            "use_cases": ["Budget planning", "Financial audits", "Cost optimization"]
        },
        "security": {
            "safety_assessment": "Comprehensive security audit",
            "threat_analysis": "Specific threat evaluation",
            "use_cases": ["Safety audits", "Emergency preparedness", "Risk management"]
        },
        "healthcare": {
            "health_trends": "Disease outbreak prediction",
            "use_cases": ["Health monitoring", "Outbreak prevention", "Resource planning"]
        },
        "data_science": {
            "performance_prediction": "AI-powered student predictions",
            "enrollment_forecasting": "Future enrollment patterns",
            "use_cases": ["Early intervention", "Resource planning", "Growth strategy"]
        },
        "education": {
            "curriculum_review": "Expert curriculum analysis",
            "use_cases": ["Curriculum development", "Standards compliance", "Quality improvement"]
        },
        "proposals": {
            "grant_writing": "Professional funding proposals",
            "use_cases": ["Donor funding", "Government grants", "Foundation support"]
        },
        "ngo": {
            "impact_reporting": "Donor-ready impact reports",
            "use_cases": ["Donor reporting", "Annual reports", "Transparency"]
        },
        "expenses": {
            "budget_optimization": "Cost savings identification",
            "use_cases": ["Cost reduction", "Vendor negotiation", "Efficiency"]
        }
    }
