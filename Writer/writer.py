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
   
    test_input = f"""
    (1) PRODUCT SPECS

Product Name: Samsung 43-Inch Class Serif QLED 4K Smart TV
Model Number: QN43LS01TAFXZA
Brand: Samsung
Color: Black
Screen Size: 43 inches
Item Weight: 38.8 pounds
Product Dimensions: 16.4 x 38.8 x 40.5 inches
Aspect Ratio: 16:9
Voltage: 120 Volts
Batteries: 2 AAA batteries required
Speaker Type: Built-In
Special Features:
- Flat screen
- 100% Color Volume with Quantum Dot
- NFC on TV (Android audio mirroring)
- Ambient Mode+ (custom décor/art display)
- Quantum Processor 4K (AI upscaling)
- Alexa Built-In
- Smart TV OS with Bixby, Alexa, Google Assistant

Smart Features:
- Access to Samsung TV Plus (200+ free channels)
- One-touch mirroring via NFC
- Wi-Fi built-in; no external boxes needed
- Solar-powered remote with USB charging option

Ratings & Availability:
- 4.0 out of 5 stars (207 reviews)
- Amazon Best Seller Rank:
   - #63,593 in Electronics
   - #171 in QLED TVs
- ASIN: B086LKCLQL
- First Available: April 27, 2020

(2) USER REVIEW

What Users Love:
- Design: Stylish, unique, and seamlessly blends into decor
- Functionality: Standalone smart TV with built-in apps
- Portability: Easy to move around and set up
- Art Mode: Loved by users for displaying images and weather
- No Additional Devices: Works without Firestick or Apple TV
- Remote: Solar-powered and convenient

Common Complaints:
- Durability Issues: One user experienced "Black Screen of Death" after 3 years
- UI/UX Frustrations: Remote syncing problems, app installation confusion, Hulu glitches
- Network Instability: Random disconnects requiring reboots
- Software Limitations: Clunky navigation and non-intuitive menus

Notable Quotes:
- “Looks very aesthetic, we are very happy.”
- “Elegant and interesting in design. Perfectly acceptable picture quality.”
- “Died right after 3 years... can’t recommend it despite the looks.”
- “I was able to toss all my boxes... the TV stands alone and looks really great.”
- “Bought for the design — not disappointed, but the software is meh.”

(3) IMPORTANT FAQ

Q: Is this TV wall-mountable?
A: No, this model is designed to stand independently like furniture and is not optimized for wall mounting.

Q: Does it come with art or do I need to pay for Ambient Mode content?
A: Comes with preloaded visuals and the exclusive Bouroullec palette. No extra fees for Ambient Mode+ content.

Q: Can I use this TV without any streaming boxes (Fire Stick, Apple TV)?
A: Yes. The built-in smart OS supports most major apps and Samsung TV Plus offers 200+ free channels.

Q: Can I connect my phone to this TV?
A: Yes, Android users can use NFC for quick music/audio mirroring. Screen mirroring also supported.

Q: What voice assistants does it support?
A: Alexa, Google Assistant, and Samsung’s Bixby are built-in.

Q: How is this different from Samsung’s Frame TV?
A: The Serif is freestanding and furniture-like, while The Frame is designed to mount flush on a wall. Serif includes built-in art mode content for free.

Q: Does the remote use batteries?
A: No standard batteries needed—it uses solar power and can also charge via USB.

Q: How’s the software experience?
A: Mixed. Users praise the design and basic functions, but note occasional bugs, slow menus, and a learning curve with app navigation.
    """
    test_question = "I live in a big 3000 sqft house, is this TV good for my high celling living room?"
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