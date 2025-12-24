"""
Auto A/B Testing for AI Features
Automatically tests Core vs Hybrid vs Flash modes
"""
from api.services.feature_flags import get_feature_flag_service, Experiment, ExperimentStatus
from datetime import datetime, timedelta

def setup_ai_experiments():
    """Setup automatic A/B tests for AI features"""
    service = get_feature_flag_service()
    
    # Experiment 1: AI Mode Performance Test
    # Test which AI mode gets better engagement
    ai_mode_experiment = Experiment(
        name="ai_mode_comparison",
        description="Compare Core vs Hybrid vs Flash AI modes for user engagement",
        variants=["core", "hybrid", "flash"],
        traffic_split=[30, 50, 20],  # Hybrid gets most traffic (recommended)
        status=ExperimentStatus.ACTIVE,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )
    service.register_experiment(ai_mode_experiment)
    
    # Experiment 2: AI Response Time vs Accuracy
    # Measure if faster responses (Flash) convert better than accurate ones (Core)
    response_experiment = Experiment(
        name="ai_speed_vs_accuracy",
        description="Test if users prefer fast AI (Flash) or accurate AI (Core)",
        variants=["fast_flash", "accurate_core", "balanced_hybrid"],
        traffic_split=[25, 25, 50],
        status=ExperimentStatus.ACTIVE,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=30)
    )
    service.register_experiment(response_experiment)
    
    # Experiment 3: Cloud Sync Adoption
    # Test if users with cloud sync enabled use the system more
    sync_experiment = Experiment(
        name="cloud_sync_adoption",
        description="Measure impact of cloud sync on user retention",
        variants=["sync_enabled", "sync_disabled"],
        traffic_split=[70, 30],  # Most users get sync (Hybrid/Flash)
        status=ExperimentStatus.ACTIVE,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=60)
    )
    service.register_experiment(sync_experiment)
    
    # Experiment 4: Low-RAM Optimization
    # Test if quantized models maintain user satisfaction
    ram_experiment = Experiment(
        name="quantized_model_satisfaction",
        description="Test user satisfaction with quantized models on low-RAM devices",
        variants=["full_model", "quantized_model"],
        traffic_split=[40, 60],  # More users get quantized (Hybrid mode)
        status=ExperimentStatus.ACTIVE,
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=45)
    )
    service.register_experiment(ram_experiment)
    
    print("✅ AI A/B experiments initialized")
    return service

# Auto-run on import
setup_ai_experiments()
