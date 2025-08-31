# src/agents/data_formatter.py
from crewai import Agent, Task
from typing import List, Dict, Any
from src.utils.logging_config import setup_logger
from src.utils.file_utils import read_json_file, write_json_file, write_csv_file
from pathlib import Path
from src.config.settings import settings
from src.models.market_data import MarketSource

logger = setup_logger(__name__)

def create_data_formatter_agent() -> Agent:
    """
    Create a CrewAI agent for formatting data and generating reports.
    
    Returns:
        Configured CrewAI Agent instance
    """
    return Agent(
        role="Data Formatter and Report Generator",
        goal="Transform unified prediction market data into structured reports (JSON and CSV) and generate insights",
        backstory=(
            "You are a data visualization and reporting specialist with expertise "
            "in financial markets. You create clear, actionable reports from "
            "complex data sets, highlighting opportunities and insights for traders "
            "and analysts."
        ),
        verbose=True,
        allow_delegation=False,
    )

def create_data_formatting_task(agent: Agent, input_path: Path, json_output_path: Path, csv_output_path: Path) -> Task:
    """
    Create a task for formatting data and generating reports.
    
    Args:
        agent: The agent to perform the task
        input_path: Path to the unified product data
        json_output_path: Path to save the formatted JSON
        csv_output_path: Path to save the CSV report
        
    Returns:
        Configured CrewAI Task instance
    """
    return Task(
        description=(
            "Transform the unified prediction market data into well-structured "
            "JSON for internal processing and CSV for reporting. "
            "Include all relevant data points and calculate any derived metrics "
            "such as arbitrage opportunities. Optionally generate insights or "
            "comments on significant price discrepancies or market trends."
        ),
        agent=agent,
        expected_output=(
            "Two output files: "
            "1. A comprehensive JSON file with all unified product data "
            "2. A CSV report suitable for business analysts and traders "
            "The CSV should include columns for product name, prices by source, "
            "confidence score, best price, and arbitrage opportunity."
        ),
        output_file=json_output_path,
        async_execution=False,
        context=[],
    )

def execute_data_formatting(input_path: Path, json_output_path: Path, csv_output_path: Path) -> Dict[str, Any]:
    """
    Execute the data formatting and report generation process.
    
    Args:
        input_path: Path to the unified product data
        json_output_path: Path to save the formatted JSON
        csv_output_path: Path to save the CSV report
        
    Returns:
        Dictionary containing formatting results and insights
    """
    logger.info("Starting data formatting and report generation")
    
    try:
        # Read the unified product data
        unified_products = read_json_file(input_path)
        logger.info(f"Loaded {len(unified_products)} unified products for formatting")
        
        # Enhance data with additional calculations
        enhanced_products = enhance_unified_data(unified_products)
        
        # Save enhanced JSON
        write_json_file(enhanced_products, json_output_path)
        
        # Generate CSV report
        generate_csv_report(enhanced_products, csv_output_path)
        
        # Generate insights
        insights = generate_insights(enhanced_products)
        
        logger.info("Data formatting completed successfully")
        return {
            "success": True,
            "products_processed": len(enhanced_products),
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error during data formatting: {e}")
        return {
            "success": False,
            "error": str(e),
            "products_processed": 0,
            "insights": []
        }

def enhance_unified_data(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enhance unified product data with additional calculations.
    
    Args:
        products: List of unified product data
        
    Returns:
        Enhanced product data with additional metrics
    """
    enhanced_products = []
    
    for product in products:
        enhanced = product.copy()
        
        # Calculate arbitrage opportunity if multiple sources exist
        prices = enhanced.get('prices', {})
        if len(prices) > 1:
            price_values = [float(price) for price in prices.values()]
            max_price = max(price_values)
            min_price = min(price_values)
            enhanced['arbitrage_opportunity'] = max_price - min_price
            enhanced['max_price'] = max_price
            enhanced['min_price'] = min_price
        else:
            enhanced['arbitrage_opportunity'] = 0.0
            price_value = list(prices.values())[0] if prices else 0.0
            enhanced['max_price'] = price_value
            enhanced['min_price'] = price_value
        
        enhanced_products.append(enhanced)
    
    return enhanced_products

def generate_csv_report(products: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Generate a CSV report from unified product data.
    
    Args:
        products: List of unified product data
        output_path: Path to save the CSV report
    """
    # Flatten the data for CSV format
    csv_data = []
    
    for product in products:
        row = {
            'canonical_name': product.get('canonical_name', ''),
            'confidence_score': product.get('confidence_score', 0),
            'best_price': product.get('best_price', 0),
            'best_source': product.get('best_source', ''),
            'arbitrage_opportunity': product.get('arbitrage_opportunity', 0),
            'max_price': product.get('max_price', 0),
            'min_price': product.get('min_price', 0),
        }
        
        # Add prices by source
        prices = product.get('prices', {})
        for source, price in prices.items():
            # Convert MarketSource enum to string if needed
            source_str = source.value if hasattr(source, 'value') else str(source)
            row[f'price_{source_str}'] = price
        
        csv_data.append(row)
    
    # Write CSV file
    write_csv_file(csv_data, output_path)

def generate_insights(products: List[Dict[str, Any]]) -> List[str]:
    """
    Generate insights from the unified product data.
    
    Args:
        products: List of unified product data
        
    Returns:
        List of insight strings
    """
    insights = []
    
    # Find products with significant arbitrage opportunities
    arbitrage_products = [
        p for p in products 
        if p.get('arbitrage_opportunity', 0) > 0.1 and len(p.get('prices', {})) > 1
    ]
    
    if arbitrage_products:
        insights.append(
            f"Found {len(arbitrage_products)} products with significant arbitrage opportunities (>10%)"
        )
    
    # Find high-confidence matches
    high_confidence_products = [
        p for p in products if p.get('confidence_score', 0) > 0.8
    ]
    
    if high_confidence_products:
        insights.append(
            f"Found {len(high_confidence_products)} products with high-confidence matches (>80%)"
        )
    
    # Check if we have data from multiple sources
    multi_source_products = [
        p for p in products if len(p.get('prices', {})) > 1
    ]
    
    if multi_source_products:
        insights.append(
            f"Successfully matched {len(multi_source_products)} products across multiple prediction markets"
        )
    
    if not insights:
        insights.append("No significant insights identified from the current data")
    
    return insights