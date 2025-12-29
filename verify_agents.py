import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from api.agents.staff.director import DigitalCEO

async def main():
    print("🤖 Initializing Digital CEO...")
    ceo = DigitalCEO()
    
    print("\n📊 Requesting School Overview (Routine Mode)...")
    # Mock context
    context = {"school_id": "angels-ai-demo"}
    
    try:
        response = await ceo.perform_task("get_school_overview", context)
        print(f"✅ Response Received from {response.agent}")
        print(f"📈 Result: {response.result}")
        
        if response.error:
            print(f"⚠️ Warning: {response.error}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
