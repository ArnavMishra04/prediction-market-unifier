# src/agents/rag_chat.py
from crewai import Agent, Task
import json

class RAGChatAgent:
    def __init__(self):
        self.agent = Agent(
            role="Prediction Market Chat Assistant",
            goal="Answer questions about prediction market products using RAG",
            backstory=(
                "You are a knowledgeable assistant that helps users understand "
                "prediction market products, arbitrage opportunities, and trading strategies."
            ),
            verbose=True,
            allow_delegation=False
        )
    
    def chat_about_products(self, question: str, products: List[Dict[str, Any]]) -> str:
        """Chat about products using RAG techniques."""
        context = self._create_rag_context(products)
        
        task = Task(
            description=(
                f"Question: {question}\n\n"
                f"Context: {context}\n\n"
                "Provide a helpful answer based on the prediction market data."
            ),
            agent=self.agent,
            expected_output="A clear, informative answer to the user's question",
            async_execution=False
        )
        
        # Simple response for demo
        return self._simple_rag_response(question, products)
    
    def _create_rag_context(self, products: List[Dict[str, Any]]) -> str:
        """Create RAG context from products."""
        context = "Prediction Market Products:\n\n"
        for product in products:
            context += f"Product: {product['canonical_name']}\n"
            context += f"Prices: {json.dumps(product.get('prices', {}), indent=2)}\n"
            context += f"Arbitrage: {product.get('arbitrage_opportunity', 0) * 100:.1f}%\n"
            context += f"Confidence: {product.get('confidence_score', 0):.2f}\n\n"
        return context
    
    def _simple_rag_response(self, question: str, products: List[Dict[str, Any]]) -> str:
        """Simple RAG response for demo."""
        if "arbitrage" in question.lower():
            arbitrage_products = [p for p in products if p.get('arbitrage_opportunity', 0) > 0.1]
            if arbitrage_products:
                return f"I found {len(arbitrage_products)} arbitrage opportunities. The best is {arbitrage_products[0]['canonical_name']} with {arbitrage_products[0]['arbitrage_opportunity'] * 100:.1f}% spread."
            return "No significant arbitrage opportunities found currently."
        
        return "I can help you analyze prediction market products. Ask me about arbitrage opportunities or specific products."