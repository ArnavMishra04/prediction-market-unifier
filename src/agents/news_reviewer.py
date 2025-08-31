# src/agents/news_reviewer.py
from crewai import Agent, Task
from litellm import completion
import json
from typing import List, Dict, Any

class NewsReviewer:
    def __init__(self):
        self.agent = Agent(
            role="Prediction Market News Analyst",
            goal="Generate insightful news reviews about prediction market products and arbitrage opportunities",
            backstory=(
                "You are a financial news analyst specializing in prediction markets. "
                "You create engaging, informative reviews that highlight trading opportunities "
                "and market trends for traders and investors."
            ),
            verbose=True,
            allow_delegation=False
        )
    
    def generate_review(self, products: List[Dict[str, Any]]) -> str:
        """Generate a news review based on the unified products."""
        task = Task(
            description=(
                "Analyze these prediction market products and create a comprehensive news review. "
                "Highlight:\n"
                "1. Significant arbitrage opportunities\n"
                "2. Market trends and patterns\n"
                "3. Interesting product comparisons\n"
                "4. Trading recommendations\n"
                "5. Overall market sentiment\n\n"
                f"Products: {json.dumps(products, indent=2)}"
            ),
            agent=self.agent,
            expected_output="A well-structured news review article in markdown format",
            async_execution=False
        )
        
        # For demo, we'll generate a simple review
        review = self._generate_simple_review(products)
        return review
    
    def _generate_simple_review(self, products: List[Dict[str, Any]]) -> str:
        """Generate a simple news review without LLM."""
        arbitrage_products = [p for p in products if p.get('arbitrage_opportunity', 0) > 0.1]
        
        review = "# Prediction Market News Review\n\n"
        review += f"## Market Overview\nFound {len(products)} total products across platforms\n\n"
        
        if arbitrage_products:
            review += "## 🚀 Arbitrage Opportunities\n"
            for product in arbitrage_products:
                review += f"### {product['canonical_name']}\n"
                review += f"- **Arbitrage**: {product['arbitrage_opportunity'] * 100:.1f}%\n"
                review += f"- **Price Range**: {product.get('min_price', 0):.3f} - {product.get('max_price', 0):.3f}\n"
                review += f"- **Confidence**: {product.get('confidence_score', 0):.2f}\n\n"
        
        review += "## 📊 Market Analysis\n"
        review += "Significant price discrepancies detected across prediction markets. "
        review += "Traders should consider cross-platform arbitrage strategies.\n\n"
        
        return review