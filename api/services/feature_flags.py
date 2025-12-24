"""
Feature Flags Service for A/B Testing
Enables gradual rollouts, A/B experiments, and feature toggling
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import random
import hashlib


class VariantType(str, Enum):
    CONTROL = "control"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"
    VARIANT_C = "variant_c"


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused" 
    COMPLETED = "completed"


class FeatureFlag:
    """Individual feature flag configuration"""
    
    def __init__(
        self,
        name: str,
        enabled: bool = False,
        description: str = "",
        rollout_percentage: int = 0,
        target_schools: Optional[List[int]] = None,
        target_roles: Optional[List[str]] = None
    ):
        self.name = name
        self.enabled = enabled
        self.description = description
        self.rollout_percentage = rollout_percentage
        self.target_schools = target_schools or []
        self.target_roles = target_roles or []
    
    def is_enabled_for_user(
        self,
        user_id: int,
        school_id: Optional[int] = None,
        role: Optional[str] = None
    ) -> bool:
        """Determine if feature is enabled for specific user"""
        
        # Check if globally disabled
        if not self.enabled:
            return False
        
        # Check school targeting
        if self.target_schools and school_id:
            if school_id not in self.target_schools:
                return False
        
        # Check role targeting
        if self.target_roles and role:
            if role not in self.target_roles:
                return False
        
        # Check rollout percentage (consistent hashing)
        if self.rollout_percentage < 100:
            user_hash = int(hashlib.md5(f"{self.name}_{user_id}".encode()).hexdigest(), 16)
            user_bucket = user_hash % 100
            if user_bucket >= self.rollout_percentage:
                return False
        
        return True


class Experiment:
    """A/B test experiment configuration"""
    
    def __init__(
        self,
        name: str,
        description: str,
        variants: List[str],
        traffic_split: List[int],
        status: ExperimentStatus = ExperimentStatus.DRAFT,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        self.name = name
        self.description = description
        self.variants = variants
        self.traffic_split = traffic_split
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        
        # Validate traffic split
        if len(variants) != len(traffic_split):
            raise ValueError("Variants and traffic_split must have same length")
        
        if sum(traffic_split) != 100:
            raise ValueError("Traffic split must sum to 100")
    
    def get_variant_for_user(self, user_id: int) -> str:
        """Assign user to experiment variant (consistent assignment)"""
        
        if self.status != ExperimentStatus.ACTIVE:
            return self.variants[0]  # Return control
        
        # Check if experiment is within date range
        now = datetime.now()
        if self.start_date and now < self.start_date:
            return self.variants[0]
        if self.end_date and now > self.end_date:
            return self.variants[0]
        
        # Consistent hash-based assignment
        user_hash = int(hashlib.md5(f"{self.name}_{user_id}".encode()).hexdigest(), 16)
        user_bucket = user_hash % 100
        
        cumulative = 0
        for variant, percentage in zip(self.variants, self.traffic_split):
            cumulative += percentage
            if user_bucket < cumulative:
                return variant
        
        return self.variants[0]  # Fallback to control


class FeatureFlagService:
    """Service for managing feature flags and A/B experiments"""
    
    def __init__(self):
        self.flags: Dict[str, FeatureFlag] = {}
        self.experiments: Dict[str, Experiment] = {}
        self._init_default_flags()
    
    def _init_default_flags(self):
        """Initialize default feature flags"""
        
        # Example flags
        self.flags["new_dashboard_ui"] = FeatureFlag(
            name="new_dashboard_ui",
            enabled=False,
            description="New redesigned dashboard UI",
            rollout_percentage=10
        )
        
        self.flags["ai_powered_insights"] = FeatureFlag(
            name="ai_powered_insights",
            enabled=True,
            description="AI-powered insights in analytics",
            rollout_percentage=50
        )
        
        self.flags["bulk_operations_v2"] = FeatureFlag(
            name="bulk_operations_v2",
            enabled=False,
            description="Improved bulk operations interface",
            rollout_percentage=0,
            target_roles=["admin", "teacher"]
        )
    
    def register_flag(self, flag: FeatureFlag):
        """Register a new feature flag"""
        self.flags[flag.name] = flag
    
    def is_enabled(
        self,
        flag_name: str,
        user_id: int,
        school_id: Optional[int] = None,
        role: Optional[str] = None
    ) -> bool:
        """Check if feature flag is enabled for user"""
        
        flag = self.flags.get(flag_name)
        if not flag:
            return False
        
        return flag.is_enabled_for_user(user_id, school_id, role)
    
    def register_experiment(self, experiment: Experiment):
        """Register an A/B test experiment"""
        self.experiments[experiment.name] = experiment
    
    def get_variant(self, experiment_name: str, user_id: int) -> str:
        """Get experiment variant for user"""
        
        experiment = self.experiments.get(experiment_name)
        if not experiment:
            return "control"
        
        return experiment.get_variant_for_user(user_id)
    
    def track_exposure(
        self,
        experiment_name: str,
        user_id: int,
        variant: str
    ):
        """Track that user was exposed to experiment variant"""
        # This would log to analytics/database
        # For now, we'll just pass
        pass
    
    def track_conversion(
        self,
        experiment_name: str,
        user_id: int,
        metric_name: str,
        value: Any = None
    ):
        """Track conversion event for experiment analysis"""
        # This would log to analytics/database
        pass
    
    def get_all_flags(self) -> Dict[str, Dict]:
        """Get all feature flags and their status"""
        return {
            name: {
                "enabled": flag.enabled,
                "description": flag.description,
                "rollout_percentage": flag.rollout_percentage
            }
            for name, flag in self.flags.items()
        }
    
    def get_all_experiments(self) -> Dict[str, Dict]:
        """Get all experiments and their status"""
        return {
            name: {
                "description": exp.description,
                "variants": exp.variants,
                "traffic_split": exp.traffic_split,
                "status": exp.status.value
            }
            for name, exp in self.experiments.items()
        }


# Global singleton instance
_feature_flag_service = None


def get_feature_flag_service() -> FeatureFlagService:
    """Get or create feature flag service singleton"""
    global _feature_flag_service
    if _feature_flag_service is None:
        _feature_flag_service = FeatureFlagService()
    return _feature_flag_service
