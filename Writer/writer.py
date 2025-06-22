import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from scraper.general_scraper import ProductScraper
    from scripts.script_writer import ScriptWriter
except ImportError:
    # Try alternative import path
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from scraper.general_scraper import ProductScraper
        from scripts.script_writer import ScriptWriter
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure you're running from the Writer directory and all files exist.")
        raise


class Writer:
    """
    A class that processes string input and generates comprehensive product data
    using the ProductScraper class.
    """
    
    def __init__(self):
        """
        Initialize the Writer with a ProductScraper instance.
        """
        self.scraper = ProductScraper()
        print("✅ Writer initialized")
        self.script_writer = ScriptWriter()
    
    def process_product_input(self, product_input: str) -> Dict[str, Any]:
        """
        Process a product input string and generate comprehensive product data.
        
        Args:
            product_input: String description or introduction of the product
            product_name: Optional name for the product (used for file naming)
            
        Returns:
            Dictionary containing processed product data
        """
        print(f"🔄 Processing product input: {product_input[:50]}...")
        
        try:
            # Step 1: Generate detailed product details
            print("📝 Generating product details...")
            product_details = self.scraper.product_details(product_input)
            
            # Step 2: Generate pros and cons based on input and details
            print("✅❌ Generating pros and cons...")
            product_pros_cons = self.scraper.product_pros_cons(product_input, product_details)
            
            # Step 3: Analyze sentiment
            print("😊 Analyzing sentiment...")
            product_sentiment = self.scraper.product_sentiment(product_input)
            
            # Step 4: Compile product data
            product_data = {
                "product_details": product_details,
                "product_pros_cons": product_pros_cons, 
                "product_sentiment": product_sentiment
            }
            
            print(f"✅ Product data generated successfully")
            return product_data
            
        except Exception as e:
            print(f"❌ Error processing product input: {str(e)}")
            return {}

    def generate_script(self, product_data: Dict[str, Any], time: str) -> str:
        """
        Generate a script based on the product data.
        """
        return self.script_writer.generate_script(product_data, time)


    

def main():
    """
    Main function to demonstrate the GeneralProductProcessor usage.
    """
    # Initialize the processor
    processor = Writer()

    
    test_input = "Meta Ray-Ban Smart Glasses are innovative smart glasses that combine classic Ray-Ban styling with advanced technology. They feature built-in cameras, speakers, and voice control capabilities."
    
    product_data = processor.process_product_input(test_input)
    #print(f"\n✅ Product data: {product_data}")
    
    print(f"\n✅ Processing product details completed!")

    script = processor.generate_script(product_data, "40 seconds")
    #print(f"\n✅ Script: {script}")
    print(f"\n✅ Script generated successfully")

    return script
    


if __name__ == "__main__":
    main() 