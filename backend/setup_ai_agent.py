"""
Setup script to configure the .env file with xAI API key.
Run this script to add your API key to the .env file.
"""

import os
from pathlib import Path


def setup_env():
    """Configure the .env file with xAI API key."""
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    print("🔧 Git Alpha Engine - AI Agent Setup")
    print("=" * 50)
    
    # Check if .env already exists
    if env_file.exists():
        print("✅ .env file already exists")
        update = input("Do you want to update the XAI_API_KEY? (y/n): ").strip().lower()
        if update != 'y':
            print("Setup cancelled.")
            return
    
    # Get API key from user
    print("\nPlease enter your xAI API key:")
    print("(Get one at: https://console.x.ai/)")
    api_key = input("XAI_API_KEY: ").strip()
    
    if not api_key:
        print("❌ Error: API key cannot be empty")
        return
    
    # Read template or create from scratch
    if env_example.exists():
        with open(env_example, 'r') as f:
            content = f.read()
    else:
        content = """# Environment Configuration
DATABASE_URL=sqlite:///./git_alpha.db
SECRET_KEY=your-secret-key-here-change-this
XAI_API_KEY=your-xai-api-key-here
XAI_MODEL=grok-beta
AGENT_DEBUG_MODE=true
AGENT_MARKDOWN=true
"""
    
    # Replace placeholder with actual API key
    content = content.replace("your-xai-api-key-here", api_key)
    content = content.replace("XAI_API_KEY=xai-", f"XAI_API_KEY={api_key}")
    
    # Write to .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("\n✅ Configuration saved to .env file!")
    print("\n📝 Next steps:")
    print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
    print("2. Restart the backend server: uvicorn main:app --reload")
    print("3. Test the AI agent at: http://localhost:8000/docs")
    print("\n🎉 Setup complete!")


if __name__ == "__main__":
    setup_env()
