 # src/models/market_data.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class MarketSource(str, Enum):
    POLYMARKET = "polymarket"
    PREDICTION_MARKET = "prediction_market"
    KALSHI = "kalshi"
    MANUAL = "manual"

class MarketProduct(BaseModel):
    name: str = Field(..., description="The name of the prediction market product")
    price: float = Field(..., description="Current price of the product", ge=0, le=1)
    source: MarketSource = Field(..., description="The source website of the data")
    url: Optional[str] = Field(None, description="URL to the product page")
    volume: Optional[float] = Field(None, description="Trading volume if available")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the data was collected")

class UnifiedProduct(BaseModel):
    canonical_name: str = Field(..., description="Standardized product name")
    prices: Dict[MarketSource, float] = Field(..., description="Prices from different sources")
    confidence_score: float = Field(..., description="Confidence in product matching", ge=0, le=1)
    best_price: float = Field(..., description="Best available price across sources")
    best_source: MarketSource = Field(..., description="Source with the best price")
    arbitrage_opportunity: Optional[float] = Field(None, description="Arbitrage opportunity percentage")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the unification was performed")
