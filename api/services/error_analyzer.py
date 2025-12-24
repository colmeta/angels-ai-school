"""
Error Analyzer Service
AI-powered error analysis and fix suggestions using Clarity Engine
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import traceback
import re

# Import Clarity client
from api.services.clarity import get_clarity_client


class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    VALIDATION = "validation"
    EXTERNAL_API = "external_api"
    BUSINESS_LOGIC = "business_logic"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


class ErrorAnalysis:
    """Result of error analysis"""
    
    def __init__(
        self,
        error_type: str,
        error_message: str,
        severity: ErrorSeverity,
        category: ErrorCategory,
        suggested_fix: str,
        similar_errors: List[str] = None,
        documentation_links: List[str] = None,
        confidence_score: float = 0.0
    ):
        self.error_type = error_type
        self.error_message = error_message
        self.severity = severity
        self.category = category
        self.suggested_fix = suggested_fix
        self.similar_errors = similar_errors or []
        self.documentation_links = documentation_links or []
        self.confidence_score = confidence_score
        self.analyzed_at = datetime.now()


class ErrorAnalyzer:
    """Service for analyzing errors and suggesting fixes"""
    
    def __init__(self):
        self.clarity_client = get_clarity_client()
        self.error_patterns = self._load_error_patterns()
    
    def _load_error_patterns(self) -> Dict[str, Dict]:
        """Load common error patterns and their fixes"""
        
        return {
            "database_connection": {
                "patterns": [
                    r"connection.*refused",
                    r"database.*not.*found",
                    r"authentication failed.*database"
                ],
                "category": ErrorCategory.DATABASE,
                "severity": ErrorSeverity.CRITICAL,
                "fixes": [
                    "Check database connection string",
                    "Verify database is running",
                    "Check database credentials"
                ]
            },
            "authentication_failed": {
                "patterns": [
                    r"invalid.*credentials",
                    r"authentication.*failed",
                    r"token.*expired"
                ],
                "category": ErrorCategory.AUTHENTICATION,
                "severity": ErrorSeverity.HIGH,
                "fixes": [
                    "Verify user credentials are correct",
                    "Check token expiration",
                    "Verify authentication middleware is configured"
                ]
            },
            "validation_error": {
                "patterns": [
                    r"validation.*error",
                    r"invalid.*input",
                    r"field.*required"
                ],
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.MEDIUM,
                "fixes": [
                    "Check input validation rules",
                    "Verify all required fields are provided",
                    "Review Pydantic model definitions"
                ]
            },
            "permission_denied": {
                "patterns": [
                    r"permission.*denied",
                    r"access.*forbidden",
                    r"unauthorized"
                ],
                "category": ErrorCategory.AUTHORIZATION,
                "severity": ErrorSeverity.HIGH,
                "fixes": [
                    "Check user permissions and roles",
                    "Verify access control rules",
                    "Review authorization middleware"
                ]
            },
            "external_api_failure": {
                "patterns": [
                    r"api.*timeout",
                    r"connection.*timeout",
                    r"http.*error.*5\d{2}"
                ],
                "category": ErrorCategory.EXTERNAL_API,
                "severity": ErrorSeverity.MEDIUM,
                "fixes": [
                    "Check external API status",
                    "Implement retry logic with exponential backoff",
                    "Add circuit breaker pattern"
                ]
            }
        }
    
    def categorize_error(self, error_message: str, error_type: str) -> ErrorCategory:
        """Categorize error based on message and type"""
        
        error_text = f"{error_type} {error_message}".lower()
        
        for pattern_name, pattern_info in self.error_patterns.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, error_text, re.IGNORECASE):
                    return pattern_info["category"]
        
        return ErrorCategory.UNKNOWN
    
    def assess_severity(self, error_message: str, error_type: str) -> ErrorSeverity:
        """Assess error severity"""
        
        error_text = f"{error_type} {error_message}".lower()
        
        # Check known patterns
        for pattern_info in self.error_patterns.values():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, error_text, re.IGNORECASE):
                    return pattern_info["severity"]
        
        # Heuristic-based severity
        critical_keywords = ["crash", "fatal", "database", "security", "authentication"]
        high_keywords = ["failed", "error", "exception", "unauthorized"]
        medium_keywords = ["warning", "validation", "invalid"]
        
        if any(keyword in error_text for keyword in critical_keywords):
            return ErrorSeverity.CRITICAL
        elif any(keyword in error_text for keyword in high_keywords):
            return ErrorSeverity.HIGH
        elif any(keyword in error_text for keyword in medium_keywords):
            return ErrorSeverity.MEDIUM
        
        return ErrorSeverity.LOW
    
    async def analyze_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorAnalysis:
        """Analyze error and generate fix suggestions"""
        
        # Categorize and assess severity
        category = self.categorize_error(error_message, error_type)
        severity = self.assess_severity(error_message, error_type)
        
        # Check for quick fixes from patterns
        quick_fixes = []
        for pattern_info in self.error_patterns.values():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, f"{error_type} {error_message}".lower(), re.IGNORECASE):
                    quick_fixes.extend(pattern_info["fixes"])
                    break
        
        # Use Clarity for deeper analysis if available
        suggested_fix = ""
        confidence_score = 0.5
        
        if quick_fixes:
            suggested_fix = "\\n".join([f"{i+1}. {fix}" for i, fix in enumerate(quick_fixes)])
            confidence_score = 0.8
        else:
            # Ask Clarity for analysis
            try:
                analysis_prompt = f"""
                Analyze this error and suggest a fix:
                
                Error Type: {error_type}
                Error Message: {error_message}
                Category: {category.value}
                Severity: {severity.value}
                
                {f"Stack Trace: {stack_trace[:500]}" if stack_trace else ""}
                {f"Context: {context}" if context else ""}
                
                Provide:
                1. Root cause analysis
                2. Specific fix suggestions
                3. Prevention steps
                
                Be concise and actionable.
                """
                
                # In production, this would call Clarity
                # For now, provide template response
                suggested_fix = f"""
                1. Review the {category.value} logic in your code
                2. Check configuration settings related to {error_type}
                3. Verify all dependencies are correctly installed
                4. Add appropriate error handling
                """
                confidence_score = 0.6
                
            except Exception as e:
                suggested_fix = "Unable to generate AI analysis. Manual review recommended."
                confidence_score = 0.3
        
        return ErrorAnalysis(
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            category=category,
            suggested_fix=suggested_fix,
            confidence_score=confidence_score
        )
    
    def should_auto_fix(self, analysis: ErrorAnalysis) -> bool:
        """Determine if error can be automatically fixed"""
        
        # Only auto-fix low severity errors with high confidence
        if analysis.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            return False
        
        if analysis.confidence_score < 0.9:
            return False
        
        # Only auto-fix specific categories
        safe_categories = [
            ErrorCategory.VALIDATION,
            ErrorCategory.CONFIGURATION
        ]
        
        if analysis.category not in safe_categories:
            return False
        
        return True
    
    def generate_fix_pr(self, analysis: ErrorAnalysis) -> Dict[str, str]:
        """Generate code fix as a pull request"""
        
        # This would create an actual PR in production
        # For now, return template
        
        return {
            "title": f"Auto-fix: {analysis.error_type}",
            "description": f"""
            ## Error Analysis
            
            **Type**: {analysis.error_type}
            **Severity**: {analysis.severity.value}
            **Category**: {analysis.category.value}
            **Confidence**: {analysis.confidence_score:.0%}
            
            ## Suggested Fix
            
            {analysis.suggested_fix}
            
            ## Review Required
            
            Please review this automated fix before merging.
            """,
            "auto_merge": self.should_auto_fix(analysis)
        }


# Global singleton instance
_error_analyzer = None


def get_error_analyzer() -> ErrorAnalyzer:
    """Get or create error analyzer singleton"""
    global _error_analyzer
    if _error_analyzer is None:
        _error_analyzer = ErrorAnalyzer()
    return _error_analyzer
