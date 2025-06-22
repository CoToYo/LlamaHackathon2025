import os
from pyexpat import model
from llama_api_client import LlamaAPIClient
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from urllib.parse import quote_plus
import time
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import pandas as pd

class ProductScraper:
    def __init__(self):
        """
        Initialize the ProductScraper with API keys from the centralized manager.
        """
        # Initialize Llama API client if key is available
        self.llama_client = None
        try:
            self.llama_client = LlamaAPIClient(
                api_key=os.environ.get("LLAMA_API_KEY"), # This is the default and can be omitted
            )
            print("✅ Llama API client initialized")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize Llama API client: {str(e)}")
            
        
        # Initialize session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    

    def product_details(self, product: str):
        details_prompt = f"""
        Given this provided product introduction {product}, please give me a more detailed introduction about this product.
        """
        return self._call_llama_api(details_prompt)
    
    
    def product_pros_cons(self, product, product_details):
        pros_cons_prompt = f"""
                If there are any real user review, extract it. Otherwise predict potential product reviews and user feedback 
                based on the original product description {product} and early generated product details {product_details}.
                Focus on actual user experiences, ratings, and opinions.
        """
        
        return self._call_llama_api(pros_cons_prompt)
    
    def product_sentiment(self, input: str):
        sentiment_prompt = f"""
        please analyze the sentiment based on the product details {input}.
        """
        return self._call_llama_api(sentiment_prompt)

    def save_to_json(self, data: Dict[str, Any], product_name: str, filepath: Optional[str] = None):
        """
        Save scraped data to JSON file.
        
        Args:
            data: Product data dictionary
            product_name: Name of the product (used for filename generation)
            filepath: Path to save the JSON file (optional, will generate from product name if not provided)
        """
        try:
            # Generate filename from product name if not provided
            if filepath is None:
                # Clean product name for filename (remove special characters, replace spaces with underscores)
                clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_name = clean_name.replace(' ', '_').replace('-', '_')
                filepath = f"output/products/{clean_name}.json"
            
            # Ensure data directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Data saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving data: {str(e)}")

    def _call_llama_api(self, prompt: str, model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"):
        """
        Make a call to the Llama API with the given prompt.
        """
        if not self.llama_client:
            return ""
            
        try:
            completion = self.llama_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1000,
                temperature=0.3
            )
            print(f"{completion.completion_message.content}")
            return completion.completion_message.content.text
        except Exception as e:
            print(f"❌ Error calling Llama API: {str(e)}")
            return ""


def main(input):
    """Main function for testing the scraper."""
    scraper = ProductScraper()

    product_details = scraper.product_details(input)
    product_pros_cons = scraper.product_pros_cons(input, product_details)
    product_sentiment = scraper.product_sentiment(input)

    product_data = {
        "product_details": product_details,
        "product_pros_cons": product_pros_cons,
        "product_sentiment": product_sentiment
    }
    # Save to JSON
    #scraper.save_to_json(product_data, product_name)
    return product_data


if __name__ == "__main__":
    main("") 