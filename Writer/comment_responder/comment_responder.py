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

class CommentResponder:
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

    def generate_command_response(self, product_dict, question, time):
        product_details = product_dict["product_details"]
        product_pros_cons = product_dict["product_pros_cons"]
        product_sentiment = product_dict["product_sentiment"]
        prompt = f"""
        You are a comment responder, your job is to give customer accurate response based on their question and the following product details.
        Try to make the context fun and appealing, but if the question is about product features, be accurate.
        You have product details {product_details}, pros and cons {product_pros_cons}, sentiment analysis {product_sentiment}.
        Answer the question {question} based on the above information. Generate a {time} long answer.
        Don't repeat on the same information in product details.
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

def main(product_dict, question, time):
    responder = CommentResponder() 
    return responder.generate_command_response(product_dict, question, time)


if __name__ == "__main__":
    main("") 