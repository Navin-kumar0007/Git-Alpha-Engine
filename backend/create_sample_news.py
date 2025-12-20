"""
Create sample news articles for testing
"""
import sys
import os
from datetime import datetime

# Force using the correct database from .env
os.environ.setdefault('DATABASE_URL', 'sqlite:///./git_alpha.db')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()  # Load .env to get DATABASE_URL

from app.db import SessionLocal
from app.models import NewsArticle

def create_sample_articles():
    """Create sample news articles"""
    db = SessionLocal()
    
    try:
        sample_articles = [
            {
                "title": "Bitcoin Surges Past $100K Amid Institutional Adoption",
                "description": "Bitcoin reaches new all-time high as major institutions announce increased crypto allocations.",
                "content": "Bitcoin has surged past the $100,000 mark for the first time, driven by increased institutional adoption and positive regulatory developments.",
                "url": "https://example.com/bitcoin-100k",
                "source_name": "Crypto News",
                "category": "crypto",
                "sentiment_score": 0.8,
                "impact_score": 9,
                "related_tickers": '["BTC", "ETH"]',
            },
            {
                "title": "Ethereum 2.0 Upgrade Shows Promising Results",
                "description": "The latest Ethereum upgrade demonstrates improved scalability and reduced gas fees.",
                "content": "Ethereum's recent network upgrade has shown significant improvements in transaction speeds and cost efficiency.",
                "url": "https://example.com/ethereum-upgrade",
                "source_name": "Tech Today",
                "category": "technology",
                "sentiment_score": 0.6,
                "impact_score": 7,
                "related_tickers": '["ETH", "MATIC"]',
            },
            {
                "title": "Global Markets Rally on Tech Sector Strength",
                "description": "Technology stocks lead market gains as investors remain optimistic about AI developments.",
                "content": "Major stock indices closed higher today, driven by strong performance in the technology sector.",
                "url": "https://example.com/markets-rally",
                "source_name": "Financial Times",
                "category": "business",
                "sentiment_score": 0.5,
                "impact_score": 6,
                "related_tickers": '["AAPL", "MSFT", "GOOGL"]',
            },
            {
                "title": "Solana Network Sees Record Transaction Volume",
                "description": "Solana blockchain processes over 5,000 transactions per second during peak trading hours.",
                "content": "The Solana network has demonstrated impressive scalability, handling record transaction volumes without major issues.",
                "url": "https://example.com/solana-volume",
                "source_name": "Blockchain Daily",
                "category": "crypto",
                "sentiment_score": 0.7,
                "impact_score": 8,
                "related_tickers": '["SOL", "AVAX"]',
            },
            {
                "title": "AI Startup Raises $200M in Series C Funding",
                "description": "Leading AI company secures major funding round from top venture capital firms.",
                "content": "A prominent AI startup announced a successful $200 million Series C funding round, bringing its valuation to $2 billion.",
                "url": "https://example.com/ai-funding",
                "source_name": "TechCrunch",
                "category": "technology",
                "sentiment_score": 0.6,
                "impact_score": 7,
                "related_tickers": '["MSFT", "NVDA"]',
            },
            {
                "title": "Federal Reserve Maintains Interest Rates",
                "description": "Central bank holds rates steady citing balanced economic outlook.",
                "content": "The Federal Reserve decided to maintain current interest rates, signaling confidence in economic stability.",
                "url": "https://example.com/fed-rates",
                "source_name": "Bloomberg",
                "category": "business",
                "sentiment_score": 0.0,
                "impact_score": 8,
                "related_tickers": '["BTC", "AAPL"]',
            },
            {
                "title": "Cardano Launches New DeFi Protocol",
                "description": "Major decentralized finance platform goes live on Cardano blockchain.",
                "content": "A highly anticipated DeFi protocol has officially launched on the Cardano network, bringing new capabilities to the ecosystem.",
                "url": "https://example.com/cardano-defi",
                "source_name": "Crypto Insider",
                "category": "crypto",
                "sentiment_score": 0.75,
                "impact_score": 7,
                "related_tickers": '["ADA", "DOT"]',
            },
            {
                "title": "Nvidia Announces Next-Gen AI Chips",
                "description": "Tech giant unveils powerful new processors designed for AI workloads.",
                "content": "Nvidia has announced its next generation of AI-optimized processors, promising significant performance improvements.",
                "url": "https://example.com/nvidia-ai-chips",
                "source_name": "Tech News",
                "category": "technology",
                "sentiment_score": 0.8,
                "impact_score": 9,
                "related_tickers": '["NVDA", "AMD"]',
            },
        ]
        
        created_count = 0
        for article_data in sample_articles:
            # Check if article already exists
            existing = db.query(NewsArticle).filter(NewsArticle.url == article_data["url"]).first()
            
            if not existing:
                article = NewsArticle(
                    **article_data,
                    published_at=datetime.utcnow(),
                )
                db.add(article)
                created_count += 1
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("SAMPLE NEWS ARTICLES CREATED")
        print("=" * 60)
        print(f"\n[SUCCESS] Created {created_count} sample articles!")
        print("\nRefresh your News Hub to see the articles!")
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_articles()
