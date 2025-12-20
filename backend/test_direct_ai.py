"""Direct test of AI Agent Service to see the actual error"""
import asyncio
import sys
from dotenv import load_dotenv
load_dotenv()

# Add the current directory to path so we can import from app
sys.path.insert(0, '.')

from app.services.ai_agent_service import AIAgentService

async def test_direct():
    print("🧪 Testing AI Agent Service directly...")
    print(f"✓ Is configured: {AIAgentService.is_configured()}")
    
    try:
        print("\n📤 Sending test query...")
        response = await AIAgentService.query("What is the price of TSLA?")
        print(f"\n✅ Success!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct())
