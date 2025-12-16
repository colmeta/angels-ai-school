
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print(f"Checking imports from: {project_root}")

try:
    from api.core.mcp import get_mcp_client
    from api.services.clarity import get_clarity_client
    
    # Initialize
    print("Initializing Clarity MCP Client...")
    client = get_clarity_client()
    
    # Verify Singleton
    mcp = get_mcp_client()
    
    if client == mcp:
        print("✅ SUCCESS: MCP Singleton is working correctly.")
        print(f"✅ Provider: {type(mcp).__name__}")
    else:
        print("❌ FAILURE: MCP Singleton mismatch.")
        exit(1)

except ImportError as e:
    print(f"❌ FAILURE: Import Error - {e}")
    exit(1)
except Exception as e:
    print(f"❌ FAILURE: Runtime Error - {e}")
    exit(1)
