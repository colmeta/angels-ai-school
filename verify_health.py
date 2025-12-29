import asyncio
import sys
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, ".")

from fastapi import status
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check_healthy():
    """Test standard healthy response"""
    print("Testing Healthy State...")
    with patch("api.services.monitoring.MonitoringService._check_database") as mock_db:
        # Mock successful DB check
        mock_db.return_value = {
            "healthy": True, 
            "response_time_ms": 10, 
            "status": "connected"
        }
        
        # Mock Clarity API check (since it makes real calls)
        with patch("api.services.monitoring.MonitoringService._check_clarity_api") as mock_clarity:
            mock_clarity.return_value = {
                "healthy": True,
                "response_time_ms": 50,
                "status": "available"
            }
            
            response = client.get("/api/health")
            print(f"Status: {response.status_code}")
            print(f"Body: {response.json()}")
            
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
            print("✅ Healthy State Passed")

def test_health_check_db_failure():
    """Test 503 response when DB fails"""
    print("\nTesting DB Failure State...")
    with patch("api.services.monitoring.MonitoringService._check_database") as mock_db:
        # Mock FAILED DB check
        mock_db.return_value = {
            "healthy": False, 
            "error": "Connection refused",
            "status": "disconnected"
        }
        
        with patch("api.services.monitoring.MonitoringService._check_clarity_api") as mock_clarity:
            mock_clarity.return_value = {
                "healthy": True,
                "status": "available"
            }

            response = client.get("/api/health")
            print(f"Status: {response.status_code}")
            print(f"Body: {response.json()}")
            
            assert response.status_code == 503
            assert response.json()["checks"]["database"]["healthy"] == False
            print("✅ DB Failure State Passed")

def test_health_check_degraded():
    """Test 200 response (Degraded) when External API fails but DB is OK"""
    print("\nTesting Degraded State...")
    with patch("api.services.monitoring.MonitoringService._check_database") as mock_db:
        # Mock successful DB check
        mock_db.return_value = {
            "healthy": True, 
            "status": "connected"
        }
        
        with patch("api.services.monitoring.MonitoringService._check_clarity_api") as mock_clarity:
            # Mock FAILED Clarity API
            mock_clarity.return_value = {
                "healthy": False,
                "error": "Timeout",
                "status": "unavailable"
            }
            
            response = client.get("/api/health")
            print(f"Status: {response.status_code}")
            print(f"Body: {response.json()}")
            
            assert response.status_code == 200
            assert response.json()["status"] == "degraded"
            print("✅ Degraded State Passed")

if __name__ == "__main__":
    try:
        test_health_check_healthy()
        test_health_check_db_failure()
        test_health_check_degraded()
        print("\n🎉 All Health Check Verification Tests Passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
