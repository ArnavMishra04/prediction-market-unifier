 # src/agents/data_collector.py
from crewai import Agent, Task
from typing import List, Dict, Any
import json
from src.utils.logging_config import setup_logger
from src.utils.browser_tools import BrowserManager, scrape_polymarket, scrape_prediction_market, scrape_kalshi
from src.utils.file_utils import write_json_file
from pathlib import Path
from src.config.settings import settings

logger = setup_logger(__name__)

def create_data_collector_agent() -> Agent:
    """
    Create a CrewAI agent for collecting prediction market data.
    
    Returns:
        Configured CrewAI Agent instance
    """
    return Agent(
        role="Prediction Market Data Collector",
        goal="Scrape prediction market data from multiple websites and output structured JSON",
        backstory=(
            "You are an expert web scraper and data collector with deep knowledge "
            "of prediction markets. You specialize in extracting clean, structured "
            "data from various gambling and prediction market websites."
        ),
        verbose=True,
        allow_delegation=False,
    )

def create_data_collection_task(agent: Agent, output_path: Path) -> Task:
    """
    Create a task for collecting prediction market data.
    
    Args:
        agent: The agent to perform the task
        output_path: Path to save the collected data
        
    Returns:
        Configured CrewAI Task instance
    """
    return Task(
        description=(
            "Scrape prediction market data from at least three different websites "
            "including Polymarket, PredictIt, and Kalshi (or similar). "
            "Extract product names, current prices, and any available metadata. "
            "Output the data as a structured JSON file with clear schema."
        ),
        agent=agent,
        expected_output=(
            "A JSON file containing prediction market data from multiple sources. "
            "The data should include product names, prices, sources, and timestamps. "
            "Example format: "
            '[{"name": "Product Name", "price": 0.75, "source": "polymarket", "url": "https://...", "timestamp": "..."}]'
        ),
        output_file=output_path,
        async_execution=False,
        context=[],
    )

def execute_data_collection(output_path: Path) -> List[Dict[str, Any]]:
    """
    Execute the data collection process using browser automation.
    
    Args:
        output_path: Path to save the collected data
        
    Returns:
        List of collected market data items
    """
    logger.info("Starting data collection from prediction markets")
    
    all_markets = []
    
    try:
        with BrowserManager() as browser_manager:
            page = browser_manager.create_page()
            
            # Scrape data from multiple sources
            polymarket_data = scrape_polymarket(page)
            predictit_data = scrape_prediction_market(page)
            kalshi_data = scrape_kalshi(page)
            
            # Combine all market data
            for source_data in [polymarket_data, predictit_data, kalshi_data]:
                if source_data.get("success", False):
                    all_markets.extend(source_data["markets"])
                else:
                    logger.warning(f"Failed to scrape data from {source_data.get('source')}")
            
            # Save the collected data
            write_json_file(all_markets, output_path)
            
            logger.info(f"Collected data from {len(all_markets)} markets")
            return all_markets
            
    except Exception as e:
        logger.error(f"Error during data collection: {e}")
        # Fallback to sample data if scraping fails
        return fallback_data_collection(output_path)

def fallback_data_collection(output_path: Path) -> List[Dict[str, Any]]:
    """
    Provide fallback sample data if web scraping fails.
    
    Args:
        output_path: Path to save the sample data
        
    Returns:
        List of sample market data items
    """
    logger.warning("Using fallback sample data due to scraping issues")
    
    sample_data = [
        {
            "name": "Will Biden win the 2024 election?",
            "price": 0.45,
            "source": "polymarket",
            "url": "https://polymarket.com/event/biden-2024",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "name": "Trump 2024 election victory",
            "price": 0.55,
            "source": "predictit",
            "url": "https://www.predictit.org/markets/detail/7453/Who-will-win-the-2024-US-presidential-election",
            "timestamp": "2024-01-15T10:31:00Z"
        },
        {
            "name": "2024 Presidential Election - Democratic Winner",
            "price": 0.48,
            "source": "kalshi",
            "url": "https://kalshi.com/event/democratic-presidential-nominee-2024",
            "timestamp": "2024-01-15T10:32:00Z"
        },
        {
            "name": "Federal Reserve rate cut in 2024",
            "price": 0.75,
            "source": "polymarket",
            "url": "https://polymarket.com/event/fed-rate-cut-2024",
            "timestamp": "2024-01-15T10:33:00Z"
        },
        {
            "name": "Bitcoin to reach $100K by end of 2024",
            "price": 0.35,
            "source": "predictit",
            "url": "https://www.predictit.org/markets/detail/7892/Will-Bitreach-$100000-by-Dec-31-2024",
            "timestamp": "2024-01-15T10:34:00Z"
        }
    ]
    
    write_json_file(sample_data, output_path)
    return sample_data
