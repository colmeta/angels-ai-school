import sys
from unittest.mock import MagicMock, patch

# Mock the entire clarity service module to prevent init side effects
mock_clarity = MagicMock()
sys.modules["api.services.clarity"] = mock_clarity

# Also mock database middleware or other things that might connect on import/startup
sys.modules["api.services.monitoring"] = MagicMock()

# Now import app
try:
    from api.main import app
    print("✅ App imported successfully with mocks")
except Exception as e:
    print(f"❌ App import failed: {e}")
    sys.exit(1)

from fastapi.testclient import TestClient

# We need to re-import monitoring to patch it successfully for the TEST itself
# But since we mocked it in sys.modules, we need to be careful.
# Actually, since we want to test `api.routes.monitoring`, we need that module to be real,
# but `api.services.monitoring` to be mocked/controlled.

# Let's manually reload the route module to ensure it uses the mocked service or we can patch it there.
import importlib
import api.routes.monitoring
importlib.reload(api.routes.monitoring)

client = TestClient(app)

def test_health_route():
    print("Testing /api/health...")
    
    # We need to patch the get_monitoring_service in the ROUTE module
    # because that's where it's imported from.
    with patch("api.routes.monitoring.get_monitoring_service") as mock_get_service:
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # 1. Healthy
        mock_service.health_check.return_value = {"status": "healthy"}
        resp = client.get("/api/health")
        print(f"Healthy: {resp.status_code}")
        assert resp.status_code == 200
        
        # 2. Unhealthy (DB Down)
        mock_service.health_check.return_value = {"status": "unhealthy"}
        resp = client.get("/api/health")
        print(f"Unhealthy: {resp.status_code}")
        assert resp.status_code == 503
        
        # 3. Degraded
        mock_service.health_check.return_value = {"status": "degraded"}
        resp = client.get("/api/health")
        print(f"Degraded: {resp.status_code}")
        assert resp.status_code == 200

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(test_health_route()) # In case the endpoint is async
        # Wait, TestClient handles async endpoints automatically, no need for asyncio.run usually 
        # unless we are calling the async function directly. TestClient calls the app.
        # But wait, my previous script used `async def test...` which is wrong for TestClient usage usually? 
        # No, you can use sync test functions.
        
        # Let's just run it sync
        test_health_route()
        print("🎉 Verification Passed!")
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
