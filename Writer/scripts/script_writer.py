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
from pathlib import Path

class ScriptWriter:
    def __init__(self):
        # Initialize Llama API client if key is available
        self.llama_client = None
        try:
            self.llama_client = LlamaAPIClient(
                api_key=os.environ.get("LLAMA_API_KEY"), # This is the default and can be omitted
            )
            print("✅ Llama API client initialized")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize Llama API client: {str(e)}")

    def generate_script(self, product_details, product_pros_cons, product_sentiment, time):
        prompt = f"""
        Given the following product details {product_details}, pros and cons {product_pros_cons}, sentiment analysis {product_sentiment},
        Generate a {time} long introduction script to describe this product, attract more target users, make the context fun and appealing. 
        Give me script only.
        """
        return self._call_llama_api(prompt)

    def _call_llama_api(self, prompt: str, model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"):
        if not self.llama_client:
            return ""   
        try:
            completion = self.llama_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1000,
                temperature=0.3
            )
            #print(f"{completion.completion_message.content}")
            return completion.completion_message.content.text

        except Exception as e:
            print(f"❌ Error calling Llama API: {str(e)}")
            return ""
    
    def _build_prompt(self, product_details, product_pros_cons, product_sentiment):
        pass
    
    def _generate_placeholder_script(self, product_details, product_pros_cons, product_sentiment, time):
        pass

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

def main(product_name: str = "Meta Ray-Ban Smart Glasses"):
    """Main function for testing the scraper."""
    writer = ScriptWriter()
    # Load product data
    # Clean product name for filename (remove special characters, replace spaces with underscores)
    clean_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_name = clean_name.replace(' ', '_').replace('-', '_')

    script_dir = Path(__file__).parent.parent
    filepath = f'{script_dir}/scraper/output/products/{clean_name}.json'

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            product_details = data["product_details"]
            product_pros_cons = data["product_pros_cons"]
            product_sentiment = data["product_sentiment"]
    else:
        print(f"❌ Product data file not found: {filepath}")
        return

    # Generate script
    intro_script = writer.generate_script(product_details, product_pros_cons, product_sentiment, "40 seconds")
    #placeholder_script = writer._generate_placeholder_script(product_details, product_pros_cons, product_sentiment, "40 seconds") # for in between talk
    
    script_data = {
        "intro_script": intro_script,
        #"placeholder_script": placeholder_script
    }
    # Save to JSON
    writer.save_to_json(script_data, product_name)


if __name__ == "__main__":
    main() 