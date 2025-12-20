import asyncio
import sys
import os

# Add backend dir to path
sys.path.append(os.getcwd())

from app.services.market_data import get_assets_with_metrics

async def main():
    try:
        print("Running get_assets_with_metrics...")
        data = await get_assets_with_metrics()
        print("Success!")
        print(data)
    except Exception as e:
        print("Failed!")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
