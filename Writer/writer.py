import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from scraper.general_scraper import ProductScraper
    from scripts.script_writer import ScriptWriter
    from comment_responder.comment_responder import CommentResponder
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
    def __init__(self):
        self.scraper = ProductScraper()
        print("✅ ProductScraper initialized")
        self.script_writer = ScriptWriter()
        print("✅ ScriptWriter initialized")
        self.comment_responder = CommentResponder()
        print("✅ CommentResponder initialized")
    
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

    def generate_comment_response(self, product_data: Dict[str, Any], question: str, time: str) -> str:
        """
        Generate a comment response based on the product data.
        """
        return self.comment_responder.generate_command_response(product_data, question, time)


    

def main():
    """
    Main function to demonstrate the Writer usage.
    """
    # Initialize the processor
    processor = Writer()
   
    test_input = "placeholder"
    test_question = "placeholder"
    intro_time = "40 seconds"
    answer_time = "10 seconds"

    ##### Write the script #####
    product_data = processor.process_product_input(test_input)
    #print(f"\n✅ Product data: {product_data}")
    
    print(f"\n✅ Processing product details completed!")

    script = processor.generate_script(product_data, intro_time)

    print(f"\n✅ Script: {script}")

    print(f"\n✅ Script generated successfully")


    ##### Answer the question #####
    print(f"\n❓Question is: {test_question}")
    comment_response = processor.generate_comment_response(product_data, test_question, answer_time)
    print(f"\n✅ Comment response: {comment_response}")

    return script, comment_response
    


if __name__ == "__main__":
    main() 