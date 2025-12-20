import random
import numpy as np
from textblob import TextBlob
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import os
import logging

logger = logging.getLogger(__name__)

# --- AUTO-FIX: Download missing AI data ---
# --- AUTO-FIX: Download missing AI data (patched) ---
def download_nltk_data():
    """
    Ensure required NLTK resources are present.

    We use correct resource paths and catch both LookupError and OSError
    to avoid crashing the app on partially installed data.
    """
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("corpora/brown", "brown"),
        ("corpora/wordnet", "wordnet"),
        ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
    ]

    for path, name in resources:
        try:
            nltk.data.find(path)
        except (LookupError, OSError):
            nltk.download(name)


download_nltk_data()

class AlphaEngine:
    def __init__(self):
        # 1. Predictive Model
        self.model = RandomForestRegressor(n_estimators=100)
        self._mock_train_model()

        # 2. Semantic Search Engine (TF-IDF)
        # Knowledge Base for Crypto Assets
        self.asset_knowledge = {
            "bitcoin": "store of value gold digital currency proof of work payment inflation hedge layer 1",
            "ethereum": "smart contracts layer 1 defi nfts dapps evm programmable money proof of stake",
            "solana": "high speed layer 1 scaling low fees proof of history defi dapps",
            "cardano": "scientific peer review layer 1 sustainability proof of stake",
            "polkadot": "interoperability parachains layer 0 cross-chain",
            "chainlink": "oracle data feeds middleware infrastructure web3 api real world data",
            "dogecoin": "meme community currency payment scrypt musk",
            "avalanche": "subnets scaling layer 1 fast finality evm",
            "cosmos": "internet of blockchains ibc interoperability sdk",
            "near": "usability sharding layer 1 developer friendly"
        }
        self._init_semantic_search()

        self.bullish_terms = {'mainnet', 'launch', 'release', 'scale', 'optimize', 'partnership', 'growth', 'feature', 'upgrade', 'merge'}
        self.bearish_terms = {'bug', 'fix', 'leak', 'patch', 'fail', 'error', 'exploit', 'hack', 'delay', 'vulnerability'}

    def _mock_train_model(self):
        X = np.random.rand(100, 3) 
        y = np.random.rand(100)
        self.model.fit(X, y)

    def _init_semantic_search(self):
        """Train a local NLP model on asset descriptions"""
        self.corpus_ids = list(self.asset_knowledge.keys())
        self.corpus_data = list(self.asset_knowledge.values())
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_data)

    def analyze_sentiment(self, commit_messages: list[str]) -> tuple[float, list[str]]:
        if not commit_messages: return 50.0, []
        
        polarities = []
        keywords = []
        for msg in commit_messages:
            try:
                blob = TextBlob(msg)
                base_polarity = blob.sentiment.polarity
                msg_lower = msg.lower()
                if any(term in msg_lower for term in self.bullish_terms): base_polarity += 0.3
                elif any(term in msg_lower for term in self.bearish_terms): base_polarity -= 0.1
                base_polarity = max(min(base_polarity, 1.0), -1.0)
                polarities.append(base_polarity)
                tags = blob.tags 
                keywords.extend([w for w, t in tags if t == 'NN' and '/' not in w and '.' not in w][:2])
            except Exception: continue

        if polarities:
            avg_polarity = sum(polarities) / len(polarities)
            jitter = random.uniform(-2.0, 2.0)
            sentiment_score = ((avg_polarity + 1) / 2) * 100 + jitter
        else:
            sentiment_score = 50.0
        
        unique_keywords = list(set(keywords))[:5]
        return round(sentiment_score, 1), unique_keywords

    def calculate_alpha_score(self, velocity: int, sentiment_score: float) -> int:
        norm_velocity = min(velocity, 150) / 1.5
        final_score = (norm_velocity * 0.6) + (sentiment_score * 0.4)
        return int(min(max(final_score, 0), 100))

    def semantic_search(self, query: str) -> list[str]:
        """
        AI Search: Input 'smart contract' -> Output ['ethereum', 'solana', 'avalanche']
        """
        if not query: return []
        try:
            query_vec = self.vectorizer.transform([query])
            cosine_similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            # Get top 3 matches
            related_docs_indices = cosine_similarities.argsort()[:-4:-1]
            results = []
            for i in related_docs_indices:
                if cosine_similarities[i] > 0.1: # Threshold for relevance
                    results.append(self.corpus_ids[i])
            return results
        except Exception:
            return []

    def get_recommendations(self, asset_id: str) -> list[str]:
        """
        Find similar assets based on content description
        """
        if asset_id not in self.corpus_ids: return []
        idx = self.corpus_ids.index(asset_id)
        cosine_similarities = cosine_similarity(self.tfidf_matrix[idx:idx+1], self.tfidf_matrix).flatten()
        related_indices = cosine_similarities.argsort()[:-4:-1]
        # Exclude self
        return [self.corpus_ids[i] for i in related_indices if self.corpus_ids[i] != asset_id]

engine = AlphaEngine()


class AIEngine:
    """AI Engine for news analysis with clustering and topic extraction"""

    def __init__(self):
        """Initialize AI engine"""
        self.bullish_terms = {
            'growth', 'surge', 'rally', 'bull', 'gain', 'profit', 'increase',
            'partnership', 'launch', 'upgrade', 'breakthrough', 'success', 'expansion'
        }
        self.bearish_terms = {
            'crash', 'decline', 'fall', 'drop', 'loss', 'bear', 'fail',
            'hack', 'exploit', 'vulnerability', 'scam', 'fraud', 'collapse', 'warning'
        }
        
        # Source reliability scores (higher = more reliable)
        self.source_reliability = {
            'bloomberg': 0.9, 'reuters': 0.9, 'associated press': 0.9,
            'financial times': 0.85, 'wall street journal': 0.85,
            'cnbc': 0.8, 'yahoo finance': 0.75, 'coindesk': 0.75,
            'cointelegraph': 0.7, 'techcrunch': 0.75
        }

    def analyze_sentiment(self, text: str, source: str = None) -> float:
        """
        Analyze sentiment of text with optional source weighting

        Args:
            text: Text to analyze
            source: Optional news source for reliability weighting

        Returns:
            Sentiment score from -1.0 (negative) to 1.0 (positive)
        """
        if not text:
            return 0.0

        try:
            blob = TextBlob(text)
            base_polarity = blob.sentiment.polarity

            # Adjust based on financial keywords
            text_lower = text.lower()
            bullish_count = sum(1 for term in self.bullish_terms if term in text_lower)
            bearish_count = sum(1 for term in self.bearish_terms if term in text_lower)
            
            # Stronger adjustment for multiple keyword matches
            if bullish_count > 0:
                base_polarity += min(0.3, bullish_count * 0.1)
            if bearish_count > 0:
                base_polarity -= min(0.3, bearish_count * 0.1)

            # Apply source reliability weighting if provided
            if source:
                source_lower = source.lower()
                reliability = next(
                    (score for name, score in self.source_reliability.items() if name in source_lower),
                    0.5
                )
                # Weight sentiment by reliability (more reliable = more impact)
                base_polarity *= (0.5 + reliability * 0.5)

            # Clamp to [-1, 1]
            return max(min(base_polarity, 1.0), -1.0)

        except Exception:
            return 0.0

    def generate_summary(self, text: str, max_sentences: int = 3) -> tuple:
        """
        Generate a scored summary of the text

        Args:
            text: Text to summarize
            max_sentences: Maximum number of sentences in summary

        Returns:
            Tuple of (summary_text, confidence_score)
        """
        if not text:
            return "", 0.0

        try:
            blob = TextBlob(text)
            sentences = blob.sentences

            if len(sentences) <= max_sentences:
                return text, 1.0

            # Score sentences by importance
            sentence_scores = []
            important_words = set(self.bullish_terms) | set(self.bearish_terms)
            
            for i, sentence in enumerate(sentences):
                score = 0.0
                sentence_lower = str(sentence).lower()
                
                # Position score (earlier sentences often more important)
                position_score = 1.0 - (i / len(sentences)) * 0.5
                
                # Keyword score
                keyword_score = sum(0.2 for word in important_words if word in sentence_lower)
                
                # Length score (prefer medium length sentences)
                word_count = len(sentence.words)
                length_score = 1.0 if 10 <= word_count <= 25 else 0.5
                
                score = position_score + keyword_score + length_score
                sentence_scores.append((str(sentence), score))

            # Sort by score and take top N
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            top_sentences = sentence_scores[:max_sentences]
            
            # Maintain original order
            summary_sentences = [s for s, _ in sorted(top_sentences, 
                                                      key=lambda x: sentences.index(x[0]))]
            summary = " ".join(summary_sentences)
            
            # Calculate confidence based on coverage
            confidence = min(len(summary) / len(text), 1.0) * 0.8 + 0.2
            
            return summary, confidence

        except Exception:
            # Fallback: return first 200 characters
            fallback = text[:200] + "..." if len(text) > 200 else text
            return fallback, 0.5

    def extract_tickers(self, text: str) -> list:
        """
        Extract ticker symbols from text

        Args:
            text: Text to extract tickers from

        Returns:
            List of ticker symbols
        """
        if not text:
            return []

        # Common crypto and stock tickers
        known_tickers = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
            'ADA': 'cardano', 'DOT': 'polkadot', 'DOGE': 'dogecoin',
            'AVAX': 'avalanche', 'MATIC': 'polygon', 'LINK': 'chainlink',
            'AAPL': 'apple', 'MSFT': 'microsoft', 'GOOGL': 'google',
            'AMZN': 'amazon', 'TSLA': 'tesla', 'META': 'meta',
            'NVDA': 'nvidia', 'AMD': 'amd', 'XRP': 'ripple',
            'BNB': 'binance', 'ATOM': 'cosmos', 'NEAR': 'near'
        }

        found_tickers = []
        text_upper = text.upper()

        for ticker in known_tickers:
            # Look for ticker as standalone word
            if f' {ticker} ' in f' {text_upper} ' or f'${ticker}' in text_upper:
                found_tickers.append(ticker)

        return list(set(found_tickers))  # Remove duplicates

    def calculate_impact_score(self, sentiment_score: float, tickers: list, 
                               source: str = None) -> int:
        """
        Calculate impact score based on sentiment, tickers, and source

        Args:
            sentiment_score: Sentiment score (-1 to 1)
            tickers: List of related tickers
            source: Optional news source

        Returns:
            Impact score (1-10)
        """
        # Base score from sentiment magnitude
        base_score = abs(sentiment_score) * 5

        # Ticker boost (more tickers = higher impact)
        ticker_boost = min(len(tickers) * 0.8, 3)

        # Source reliability boost
        source_boost = 0
        if source:
            source_lower = source.lower()
            reliability = next(
                (score for name, score in self.source_reliability.items() if name in source_lower),
                0.5
            )
            source_boost = reliability * 2

        # Calculate final score (1-10)
        impact = int(base_score + ticker_boost + source_boost)
        return max(1, min(impact, 10))

    def cluster_articles(self, articles: list, num_clusters: int = 5) -> dict:
        """
        Cluster articles by similarity using TF-IDF and k-means

        Args:
            articles: List of article dictionaries with 'id', 'title', 'description'
            num_clusters: Number of clusters to create

        Returns:
            Dictionary mapping cluster_id to list of article_ids and cluster label
        """
        if not articles or len(articles) < num_clusters:
            # If too few articles, put each in its own cluster
            return {
                i: {'article_ids': [article['id']], 'label': article.get('title', 'Unknown')[:50]}
                for i, article in enumerate(articles)
            }

        try:
            from sklearn.cluster import KMeans
            from collections import Counter

            # Prepare text for clustering
            texts = [
                f"{article.get('title', '')} {article.get('description', '')}"
                for article in articles
            ]

            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
            tfidf_matrix = vectorizer.fit_transform(texts)

            # Perform k-means clustering
            kmeans = KMeans(n_clusters=min(num_clusters, len(articles)), random_state=42)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)

            # Group articles by cluster
            clusters = {}
            feature_names = vectorizer.get_feature_names_out()

            for cluster_id in range(num_clusters):
                # Get articles in this cluster
                cluster_article_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
                
                if not cluster_article_indices:
                    continue

                article_ids = [articles[i]['id'] for i in cluster_article_indices]

                # Get top terms for cluster label
                cluster_center = kmeans.cluster_centers_[cluster_id]
                top_indices = cluster_center.argsort()[-3:][::-1]
                cluster_label = " / ".join([feature_names[i] for i in top_indices])

                clusters[cluster_id] = {
                    'article_ids': article_ids,
                    'label': cluster_label,
                    'size': len(article_ids)
                }

            return clusters

        except Exception as e:
            # Fallback: simple clustering by similarity in titles
            logger.warning(f"Clustering failed: {e}, using fallback")
            return {
                0: {'article_ids': [a['id'] for a in articles], 'label': 'All Articles', 'size': len(articles)}
            }

    def find_similar_articles(self, target_article: dict, all_articles: list, 
                            top_n: int = 5) -> list:
        """
        Find articles similar to the target article

        Args:
            target_article: Article dict with 'title', 'description'
            all_articles: List of article dicts to search
            top_n: Number of similar articles to return

        Returns:
            List of article_ids sorted by similarity
        """
        if not target_article or not all_articles:
            return []

        try:
            # Prepare texts
            target_text = f"{target_article.get('title', '')} {target_article.get('description', '')}"
            all_texts = [
                f"{article.get('title', '')} {article.get('description', '')}"
                for article in all_articles
            ]

            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([target_text] + all_texts)

            # Calculate cosine similarity
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

            # Get top N most similar (excluding the article itself)
            similar_indices = similarities.argsort()[-top_n:][::-1]
            similar_article_ids = [all_articles[i]['id'] for i in similar_indices if similarities[i] > 0.1]

            return similar_article_ids

        except Exception:
            return []

    def extract_trending_topics(self, articles: list, top_n: int = 10) -> list:
        """
        Extract trending topics from a corpus of articles

        Args:
            articles: List of article dicts with 'title', 'description', 'published_at'
            top_n: Number of top topics to return

        Returns:
            List of tuples (topic, score, article_count)
        """
        if not articles:
            return []

        try:
            from collections import Counter
            from datetime import datetime, timedelta

            # Combine all text
            all_text = " ".join([
                f"{article.get('title', '')} {article.get('description', '')}"
                for article in articles
            ])

            # Extract keywords using TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=50,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            
            texts = [
                f"{article.get('title', '')} {article.get('description', '')}"
                for article in articles
            ]
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()

            # Calculate average TF-IDF score for each term
            avg_scores = tfidf_matrix.mean(axis=0).A1
            term_scores = list(zip(feature_names, avg_scores))
            term_scores.sort(key=lambda x: x[1], reverse=True)

            # Count articles per topic
            trending_topics = []
            for term, score in term_scores[:top_n]:
                article_count = sum(1 for text in texts if term.lower() in text.lower())
                trending_topics.append({
                    'topic': term,
                    'score': float(score),
                    'article_count': article_count
                })

            return trending_topics

        except Exception as e:
            logger.warning(f"Topic extraction failed: {e}")
            return []