"""
AI Agent Service using Groq (FREE!) for financial analysis.
Provides real-time stock data analysis and web search capabilities.
"""

import os
from typing import Optional
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.yfinance import YFinanceTools


class AIAgentService:
    """Service for managing the Groq AI finance agent."""
    
    _instance: Optional[Agent] = None
    
    @classmethod
    def get_agent(cls) -> Agent:
        """
        Get or create the AI agent instance (singleton pattern).
        
        Returns:
            Agent: Configured Groq finance agent
        """
        if cls._instance is None:
            cls._instance = cls._create_agent()
        return cls._instance
    
    @classmethod
    def _create_agent(cls) -> Agent:
        """
        Create and configure the Groq AI finance agent.
        
        Returns:
            Agent: Configured agent with tools and instructions
        """
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Get optional configuration
        model_id = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        debug_mode = os.getenv("AGENT_DEBUG_MODE", "false").lower() == "true"
        use_markdown = os.getenv("AGENT_MARKDOWN", "true").lower() == "true"
        
        # Create the agent with Groq model and financial tools
        agent = Agent(
            name="Git Alpha Finance Agent",
            model=Groq(id=model_id, api_key=api_key),
            tools=[YFinanceTools()],
            instructions=[
                "You are a helpful financial assistant for Git Alpha Engine traders.",
                "Always use tables to display financial/numerical data.",
                "For text data, use bullet points and small paragraphs.",
                "Be concise but informative.",
                "When analyzing stocks, provide key metrics like P/E ratio, market cap, 52-week range.",
                "Include analyst recommendations when available.",
                "Use real-time data from YFinance whenever possible.",
            ],
            debug_mode=debug_mode,
            markdown=use_markdown,
        )
        
        return agent
    
    @classmethod
    async def query(cls, message: str) -> str:
        """
        Send a query to the AI agent and get a response.
        
        Args:
            message: User's question or request
            
        Returns:
            str: Agent's response
        """
        agent = cls.get_agent()
        
        # Run the agent with the user's message
        response = agent.run(message)
        
        # Extract the content from the response
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
    
    @classmethod
    async def stream_query(cls, message: str):
        """
        Stream a query response from the AI agent.
        
        Args:
            message: User's question or request
            
        Yields:
            str: Chunks of the agent's response
        """
        agent = cls.get_agent()
        
        # Stream the response
        for chunk in agent.run(message, stream=True):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    @classmethod
    def is_configured(cls) -> bool:
        """
        Check if the agent is properly configured.
        
        Returns:
            bool: True if GROQ_API_KEY is set
        """
        return bool(os.getenv("GROQ_API_KEY"))
