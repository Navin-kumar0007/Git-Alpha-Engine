"""Test script to verify Groq API connection"""
from dotenv import load_dotenv
load_dotenv()

import os
from agno.agent import Agent
from agno.models.groq import Groq

# Test API key loading
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key loaded: {'Yes' if api_key else 'No'}")
print(f"API Key starts with: {api_key[:15] if api_key else 'N/A'}")

# Try to create a simple agent
try:
    print("\nAttempting to create Groq agent...")
    agent = Agent(
        name="Test Agent",
        model=Groq(id="llama-3.3-70b-versatile", api_key=api_key),
        markdown=False
    )
    print("✅ Agent created successfully!")
    
    # Try a simple query
    print("\nTesting simple query...")
    response = agent.run("Say hello in one sentence")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    print("\n✅ Groq API is working! Migration successful!")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
