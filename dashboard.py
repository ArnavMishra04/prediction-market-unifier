# dashboard.py
import streamlit as st
import json
from pathlib import Path
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Prediction Market Dashboard",
    page_icon="📊",
    layout="wide"
)

# Simple settings
OUTPUT_DIR = "./data/output"

def load_data():
    """Load the generated data files."""
    try:
        final_data_path = Path(OUTPUT_DIR) / "final_report.json"
        if final_data_path.exists():
            with open(final_data_path, 'r') as f:
                return json.load(f)
        else:
            st.warning("No data found. Please run the main application first.")
            return []
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return []

def create_dashboard():
    """Create the Streamlit dashboard."""
    st.title("📊 Prediction Market Dashboard")
    
    # Load data
    final_data = load_data()
    
    if not final_data:
        st.info("No data available. Run 'python -m src.main' first to generate data.")
        return
    
    # Display summary statistics
    st.header("📈 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(final_data))
    
    with col2:
        multi_source = len([p for p in final_data if len(p.get('prices', {})) > 1])
        st.metric("Multi-Source Products", multi_source)
    
    with col3:
        arbitrage_ops = len([p for p in final_data if p.get('arbitrage_opportunity', 0) > 0.1])
        st.metric("Arbitrage Opportunities", arbitrage_ops)
    
    with col4:
        avg_confidence = sum(p.get('confidence_score', 0) for p in final_data) / len(final_data)
        st.metric("Avg Confidence", f"{avg_confidence:.2f}")
    
    # Show data table
    st.header("📋 Market Data")
    
    # Create a DataFrame for display
    display_data = []
    for product in final_data:
        row = {
            'Product': product.get('canonical_name', ''),
            'Confidence': product.get('confidence_score', 0),
            'Best Price': product.get('best_price', 0),
            'Best Source': product.get('best_source', ''),
            'Arbitrage %': product.get('arbitrage_opportunity', 0) * 100,
            'Price Range': f"{product.get('min_price', 0):.3f} - {product.get('max_price', 0):.3f}",
            'Sources': len(product.get('prices', {}))
        }
        # Add individual prices
        prices = product.get('prices', {})
        for source, price in prices.items():
            row[f'{source.capitalize()}'] = price
        display_data.append(row)
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True)
    
    # Show arbitrage opportunities
    arbitrage_products = [p for p in final_data if p.get('arbitrage_opportunity', 0) > 0.1]
    if arbitrage_products:
        st.header("💰 Arbitrage Opportunities")
        
        for product in arbitrage_products:
            with st.expander(f"📈 {product['canonical_name']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Arbitrage Opportunity", 
                             f"{product['arbitrage_opportunity'] * 100:.1f}%")
                
                with col2:
                    st.metric("Price Range", 
                             f"{product['min_price']:.3f} - {product['max_price']:.3f}")
                
                with col3:
                    st.metric("Confidence", f"{product['confidence_score']:.2f}")
                
                # Show individual prices
                st.subheader("Prices by Source")
                prices = product.get('prices', {})
                for source, price in prices.items():
                    st.write(f"**{source.capitalize()}**: {price:.3f}")
    
    # Show raw JSON data
    st.header("📄 Raw Data")
    with st.expander("View JSON Data"):
        st.json(final_data)
    
    # Download buttons
    st.header("💾 Download Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download JSON"):
            st.download_button(
                label="Download JSON",
                data=json.dumps(final_data, indent=2),
                file_name=f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    create_dashboard()