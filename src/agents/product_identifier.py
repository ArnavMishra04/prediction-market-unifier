# src/agents/product_identifier.py
from crewai import Agent, Task
from typing import List, Dict, Any
import json
from src.utils.logging_config import setup_logger
from src.utils.file_utils import read_json_file, write_json_file
from pathlib import Path
from src.config.settings import settings
from src.models.market_data import UnifiedProduct, MarketSource
from litellm import completion

logger = setup_logger(__name__)

def create_product_identifier_agent() -> Agent:
    """
    Create a CrewAI agent for identifying and matching products across markets.
    
    Returns:
        Configured CrewAI Agent instance
    """
    return Agent(
        role="Prediction Market Product Matcher",
        goal="Match identical prediction market products across different websites and calculate confidence scores",
        backstory=(
            "You are a data matching specialist with expertise in financial instruments "
            "and prediction markets. You use advanced NLP techniques to identify "
            "identical or similar products across different platforms, accounting for "
            "naming variations and market specifics."
        ),
        verbose=True,
        allow_delegation=False,
    )

def create_product_matching_task(agent: Agent, input_path: Path, output_path: Path) -> Task:
    """
    Create a task for matching products across prediction markets.
    
    Args:
        agent: The agent to perform the task
        input_path: Path to the collected market data
        output_path: Path to save the matched products
        
    Returns:
        Configured CrewAI Task instance
    """
    return Task(
        description=(
            "Analyze prediction market data from multiple sources and identify "
            "which products represent the same underlying event or question. "
            "Calculate a confidence score for each match based on product name "
            "similarity and other available metadata. Output a unified product "
            "board with prices from all available sources for each matched product."
        ),
        agent=agent,
        expected_output=(
            "A JSON file containing unified prediction market products with "
            "prices from all available sources and confidence scores for matching. "
            "Example format: "
            '[{"canonical_name": "Standardized Product Name", "prices": {"polymarket": 0.75, "predictit": 0.72}, '
            '"confidence_score": 0.95, "best_price": 0.75, "best_source": "polymarket"}]'
        ),
        output_file=output_path,
        async_execution=False,
        context=[],
    )

def execute_product_matching(input_path: Path, output_path: Path) -> List[Dict[str, Any]]:
    """
    Execute the product matching process using LLM-assisted matching.
    
    Args:
        input_path: Path to the collected market data
        output_path: Path to save the matched products
        
    Returns:
        List of unified product items
    """
    logger.info("Starting product matching across prediction markets")
    
    try:
        # Read the collected market data
        market_data = read_json_file(input_path)
        logger.info(f"Loaded {len(market_data)} market items for matching")
        
        # Use LLM to match products across sources
        unified_products = match_products_with_llm(market_data)
        
        # Save the unified products
        write_json_file([product.dict() for product in unified_products], output_path)
        
        logger.info(f"Created {len(unified_products)} unified products")
        return unified_products
        
    except Exception as e:
        logger.error(f"Error during product matching: {e}")
        # Fallback to simple matching if LLM fails
        return fallback_product_matching(market_data, output_path)

def match_products_with_llm(market_data: List[Dict[str, Any]]) -> List[UnifiedProduct]:
    """
    Use LLM to match products across different prediction markets.
    
    Args:
        market_data: List of market items from different sources
        
    Returns:
        List of unified products with matched items
    """
    try:
        # For demo purposes, we'll use algorithmic matching instead of LLM
        # to avoid API dependencies. In production, you would use the LLM.
        return match_products_algorithmically(market_data)
        
    except Exception as e:
        logger.error(f"LLM matching failed: {e}")
        # Fall back to algorithmic matching
        return match_products_algorithmically(market_data)

def create_matching_prompt(sources: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Create a prompt for LLM-based product matching.
    
    Args:
        sources: Market data grouped by source
        
    Returns:
        Formatted prompt for the LLM
    """
    prompt = """
    You are a prediction market analyst. Your task is to identify which products 
    across different prediction markets represent the same underlying event or question.
    
    Below are prediction market products from different sources. Please:
    1. Group products that represent the same event
    2. Create a canonical name for each group
    3. For each group, provide prices from all available sources
    4. Calculate a confidence score (0-1) for your matching
    5. Identify the best price available across sources
    
    Format your response as a JSON list with the following structure:
    [
      {
        "canonical_name": "Standardized event description",
        "prices": {
          "source1": price1,
          "source2": price2,
          ...
        },
        "confidence_score": 0.95,
        "best_price": 0.75,
        "best_source": "source1"
      }
    ]
    
    Available sources and their products:
    """
    
    for source, products in sources.items():
        prompt += f"\n\n{source.upper()}:\n"
        for i, product in enumerate(products, 1):
            prompt += f"{i}. {product['name']} - ${product['price']}\n"
    
    prompt += "\n\nPlease respond with only the JSON array, no additional text."
    return prompt

def parse_llm_response(response: str) -> List[UnifiedProduct]:
    """
    Parse the LLM response into UnifiedProduct objects.
    
    Args:
        response: LLM response string
        
    Returns:
        List of UnifiedProduct objects
    """
    try:
        # Extract JSON from response
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        json_str = response[json_start:json_end]
        
        products_data = json.loads(json_str)
        unified_products = []
        
        for product_data in products_data:
            # Convert string keys to MarketSource enum where possible
            prices = {}
            for source, price in product_data.get('prices', {}).items():
                try:
                    source_enum = MarketSource(source.lower())
                    prices[source_enum] = float(price)
                except (ValueError, KeyError):
                    # Skip invalid sources
                    continue
            
            unified_product = UnifiedProduct(
                canonical_name=product_data.get('canonical_name', 'Unknown'),
                prices=prices,
                confidence_score=float(product_data.get('confidence_score', 0.5)),
                best_price=float(product_data.get('best_price', 0.0)),
                best_source=MarketSource(product_data.get('best_source', 'manual').lower()),
            )
            unified_products.append(unified_product)
        
        return unified_products
        
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}")
        raise

def match_products_algorithmically(market_data: List[Dict[str, Any]]) -> List[UnifiedProduct]:
    """
    Fallback algorithm for product matching using simple text similarity.
    
    Args:
        market_data: List of market items from different sources
        
    Returns:
        List of unified products with matched items
    """
    # Simple implementation for demo purposes
    # In production, you would use more sophisticated matching algorithms
    
    unified_products = []
    
    # Group by simplified product names (very basic approach)
    product_groups = {}
    
    for item in market_data:
        # Create a simplified key for grouping
        simplified_name = simplify_product_name(item['name'])
        
        if simplified_name not in product_groups:
            product_groups[simplified_name] = []
        
        product_groups[simplified_name].append(item)
    
    # Create unified products from groups
    for canonical_name, items in product_groups.items():
        if len(items) >= 1:  # Create unified products even for single items
            prices = {}
            for item in items:
                try:
                    source_enum = MarketSource(item['source'].lower())
                    prices[source_enum] = float(item['price'])
                except (ValueError, KeyError):
                    continue
            
            if prices:  # Only add if we have valid prices
                best_source = max(prices.items(), key=lambda x: x[1])[0] if len(prices) > 1 else list(prices.keys())[0]
                best_price = prices[best_source]
                
                # Simple confidence score based on number of matches
                confidence = min(0.3 + (len(items) * 0.2), 0.9) if len(items) > 1 else 0.7
                
                unified_product = UnifiedProduct(
                    canonical_name=canonical_name,
                    prices=prices,
                    confidence_score=confidence,
                    best_price=best_price,
                    best_source=best_source,
                )
                unified_products.append(unified_product)
    
    return unified_products

def simplify_product_name(name: str) -> str:
    """
    Simplify product name for basic matching.
    
    Args:
        name: Original product name
        
    Returns:
        Simplified name for grouping
    """
    # Remove common prefixes/suffixes and normalize
    simplified = name.lower()
    simplified = simplified.replace('will ', '').replace('?', '')
    simplified = simplified.replace('2024', '').replace('2025', '')
    simplified = simplified.replace('president', '').replace('election', '')
    simplified = simplified.replace('win', '').replace('victory', '')
    simplified = ' '.join(simplified.split())  # Normalize whitespace
    return simplified.strip()

def fallback_product_matching(market_data: List[Dict[str, Any]], output_path: Path) -> List[Dict[str, Any]]:
    """
    Provide fallback product matching if the main matching fails.
    
    Args:
        market_data: List of market items from different sources
        output_path: Path to save the matched products
        
    Returns:
        List of unified product items as dictionaries
    """
    logger.warning("Using fallback product matching")
    
    # Use algorithmic matching as fallback
    unified_products = match_products_algorithmically(market_data)
    
    # Convert to dict for JSON serialization
    products_dict = [product.dict() for product in unified_products]
    
    write_json_file(products_dict, output_path)
    return products_dict