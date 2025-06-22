"""
Comment Responder Module for AI-Powered Livestream Agent

This module handles responding to livestream comments using intent detection,
context matching, and product knowledge to provide relevant and engaging replies.

Author: AI Livestream Agent Team
Date: 2025
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
import openai

# Import the API key manager
from config.api_keys import get_key, has_key

# TODO: Add support for real-time comment streaming
# TODO: Implement comment sentiment analysis
# TODO: Add response templates and customization
# TODO: Implement comment filtering and moderation


class CommentResponder:
    """
    Main class for responding to livestream comments intelligently.
    
    Features:
    - Intent detection for different types of comments
    - Context matching using sentence embeddings
    - Product knowledge integration
    - Personalized response generation
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the CommentResponder.
        
        Args:
            model_name: Sentence transformer model for embeddings
        """
        # Get OpenAI API key
        self.api_key = get_key('openai')
        if self.api_key:
            openai.api_key = self.api_key
            print("✅ OpenAI API configured for comment responses")
        else:
            print("⚠️  Warning: OpenAI API key not provided. Using template-based responses.")
        
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer(model_name)
            print(f"✅ Loaded embedding model: {model_name}")
        except Exception as e:
            print(f"⚠️  Warning: Could not load embedding model: {str(e)}")
            self.embedding_model = None
        
        self.product_knowledge = {}
        self.response_templates = self._load_response_templates()
        
        # Check available AI providers
        self._check_ai_providers()
        
    def _check_ai_providers(self):
        """Check and log available AI providers for comment responses."""
        available_providers = []
        
        if has_key('openai'):
            available_providers.append('OpenAI GPT')
        if has_key('anthropic'):
            available_providers.append('Anthropic Claude')
        if has_key('llama'):
            available_providers.append('Llama API')
        if has_key('gemini'):
            available_providers.append('Google Gemini')
        
        if available_providers:
            print(f"🤖 Available AI providers for responses: {', '.join(available_providers)}")
        else:
            print("⚠️  No AI provider keys found. Using template-based responses only.")
        
    def load_product_knowledge(self, filepath: str = "data/product_knowledge.json"):
        """
        Load product knowledge for context-aware responses.
        
        Args:
            filepath: Path to the product knowledge JSON file
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.product_knowledge = json.load(f)
            print(f"✅ Loaded product knowledge from {filepath}")
        except FileNotFoundError:
            print(f"❌ Product knowledge file not found: {filepath}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in product knowledge file: {filepath}")
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """
        Load response templates for different comment types.
        
        Returns:
            Dictionary of response templates by intent
        """
        return {
            'question': [
                "Great question! {answer}",
                "Thanks for asking! {answer}",
                "That's a really good point. {answer}"
            ],
            'compliment': [
                "Thank you so much! {response}",
                "That means a lot! {response}",
                "You're too kind! {response}"
            ],
            'concern': [
                "I understand your concern. {response}",
                "That's a valid point. {response}",
                "Let me address that for you. {response}"
            ],
            'purchase_intent': [
                "Awesome! {response}",
                "You won't regret it! {response}",
                "Great choice! {response}"
            ],
            'general': [
                "Thanks for your comment! {response}",
                "Appreciate you joining us! {response}",
                "Great to have you here! {response}"
            ]
        }
    
    def detect_intent(self, comment: str) -> Tuple[str, float]:
        """
        Detect the intent of a comment.
        
        Args:
            comment: The comment text to analyze
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        # TODO: Implement more sophisticated intent detection
        # TODO: Use NLP libraries like spaCy or NLTK
        
        comment_lower = comment.lower()
        
        # Simple keyword-based intent detection
        intent_keywords = {
            'question': ['what', 'how', 'why', 'when', 'where', '?', 'question'],
            'compliment': ['love', 'amazing', 'great', 'awesome', 'perfect', 'best'],
            'concern': ['worried', 'concerned', 'problem', 'issue', 'bad', 'terrible'],
            'purchase_intent': ['buy', 'purchase', 'order', 'get', 'want', 'need']
        }
        
        max_score = 0
        detected_intent = 'general'
        
        for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in comment_lower)
            if score > max_score:
                max_score = score
                detected_intent = intent
        
        confidence = min(max_score / len(intent_keywords[detected_intent]), 1.0) if max_score > 0 else 0.0
        
        return detected_intent, confidence
    
    def find_relevant_context(self, comment: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Find relevant product context for the comment using embeddings.
        
        Args:
            comment: The comment text
            top_k: Number of top relevant contexts to return
            
        Returns:
            List of relevant context items
        """
        if not self.embedding_model or not self.product_knowledge:
            return []
        
        try:
            # Get comment embedding
            comment_embedding = self.embedding_model.encode([comment])[0]
            
            # Prepare context items from product knowledge
            context_items = []
            
            # Add reviews
            for review in self.product_knowledge.get('reviews', []):
                context_items.append({
                    'text': f"{review.get('title', '')} {review.get('content', '')}",
                    'source': 'review',
                    'rating': review.get('rating', 0),
                    'username': review.get('username', ''),
                    'data': review
                })
            
            # Add pros and cons
            pros_cons = self.product_knowledge.get('pros_cons', {})
            for pro in pros_cons.get('pros', []):
                context_items.append({
                    'text': pro,
                    'source': 'pro',
                    'data': {'type': 'pro', 'content': pro}
                })
            
            for con in pros_cons.get('cons', []):
                context_items.append({
                    'text': con,
                    'source': 'con',
                    'data': {'type': 'con', 'content': con}
                })
            
            # Calculate similarities
            similarities = []
            for item in context_items:
                item_embedding = self.embedding_model.encode([item['text']])[0]
                similarity = np.dot(comment_embedding, item_embedding) / (
                    np.linalg.norm(comment_embedding) * np.linalg.norm(item_embedding)
                )
                similarities.append((similarity, item))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [item for _, item in similarities[:top_k]]
            
        except Exception as e:
            print(f"❌ Error finding relevant context: {str(e)}")
            return []
    
    def generate_response(self, 
                         comment: str,
                         username: str = "Viewer",
                         use_ai: bool = True) -> Dict[str, Any]:
        """
        Generate a response to a livestream comment.
        
        Args:
            comment: The comment text
            username: Username of the commenter
            use_ai: Whether to use AI for response generation
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Detect intent
        intent, confidence = self.detect_intent(comment)
        
        # Find relevant context
        relevant_context = self.find_relevant_context(comment)
        
        # Generate response
        if use_ai and self.api_key:
            response_text = self._generate_ai_response(comment, intent, relevant_context, username)
        else:
            response_text = self._generate_template_response(comment, intent, relevant_context, username)
        
        response_data = {
            'original_comment': comment,
            'username': username,
            'response': response_text,
            'intent': intent,
            'confidence': confidence,
            'relevant_context': relevant_context,
            'generated_at': datetime.now().isoformat(),
            'response_length': len(response_text)
        }
        
        return response_data
    
    def _generate_ai_response(self, 
                            comment: str,
                            intent: str,
                            relevant_context: List[Dict[str, Any]],
                            username: str) -> str:
        """
        Generate AI-powered response using OpenAI API.
        
        Args:
            comment: Original comment
            intent: Detected intent
            relevant_context: Relevant product context
            username: Commenter's username
            
        Returns:
            Generated response text
        """
        # TODO: Implement proper OpenAI API call
        # TODO: Add prompt engineering for better responses
        
        context_summary = ""
        if relevant_context:
            context_texts = [item['text'][:100] for item in relevant_context[:2]]
            context_summary = f"Relevant context: {'; '.join(context_texts)}"
        
        prompt = f"""
        You are a livestream host responding to a viewer comment.
        
        Comment: "{comment}"
        Username: {username}
        Intent: {intent}
        {context_summary}
        
        Generate a friendly, engaging response (max 100 words) that:
        1. Addresses the comment appropriately
        2. Uses the relevant product context if available
        3. Maintains the livestream's enthusiastic tone
        4. Encourages engagement
        
        Response:
        """
        
        # Placeholder for actual OpenAI API call
        responses = {
            'question': f"Great question, {username}! Based on our research, this product has amazing features that users love. The reviews show consistently high ratings and positive feedback.",
            'compliment': f"Thank you so much, {username}! We're thrilled you're enjoying the livestream. This product really is incredible!",
            'concern': f"I understand your concern, {username}. Let me address that - our research shows this product has excellent reliability and customer satisfaction.",
            'purchase_intent': f"Awesome, {username}! You're making a great choice. This product has received amazing reviews and users absolutely love it!",
            'general': f"Thanks for joining us, {username}! We're excited to share this amazing product with you!"
        }
        
        return responses.get(intent, responses['general'])
    
    def _generate_template_response(self, 
                                  comment: str,
                                  intent: str,
                                  relevant_context: List[Dict[str, Any]],
                                  username: str) -> str:
        """
        Generate response using templates and context.
        
        Args:
            comment: Original comment
            intent: Detected intent
            relevant_context: Relevant product context
            username: Commenter's username
            
        Returns:
            Generated response text
        """
        import random
        
        templates = self.response_templates.get(intent, self.response_templates['general'])
        template = random.choice(templates)
        
        # Generate context-based response
        if relevant_context:
            context_item = relevant_context[0]
            if context_item['source'] == 'review':
                response = f"According to user reviews, {context_item['data'].get('content', '')[:50]}..."
            elif context_item['source'] == 'pro':
                response = f"One of the best features is {context_item['data']['content']}!"
            elif context_item['source'] == 'con':
                response = f"While some mention {context_item['data']['content']}, the overall feedback is very positive!"
            else:
                response = "This product has received great feedback from our community!"
        else:
            response = "This is an amazing product that our community loves!"
        
        return template.format(response=response)
    
    def respond_to_comments(self, comments: List[Dict[str, str]], use_ai: bool = True) -> List[Dict[str, Any]]:
        """
        Respond to a batch of comments.
        
        Args:
            comments: List of comment dictionaries with 'text' and 'username' keys
            use_ai: Whether to use AI for response generation
            
        Returns:
            List of response dictionaries
        """
        responses = []
        
        for comment_data in comments:
            comment = comment_data.get('text', '')
            username = comment_data.get('username', 'Viewer')
            
            response = self.generate_response(comment, username, use_ai)
            responses.append(response)
            
            print(f"💬 {username}: {comment}")
            print(f"🤖 Response: {response['response']}")
            print("-" * 40)
        
        return responses
    
    def save_responses(self, responses: List[Dict[str, Any]], filepath: Optional[str] = None):
        """
        Save generated responses to file.
        
        Args:
            responses: List of response dictionaries
            filepath: Optional custom filepath
        """
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"responses/generated_responses_{timestamp}.json"
        
        # Ensure directory exists
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(responses, f, indent=2, ensure_ascii=False)
            print(f"✅ Responses saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving responses: {str(e)}")


def main():
    """Main function for testing the comment responder."""
    responder = CommentResponder()
    
    # Load product knowledge
    responder.load_product_knowledge()
    
    # Example comments
    test_comments = [
        {"text": "What's the battery life like?", "username": "TechFan123"},
        {"text": "This looks amazing! I love it!", "username": "ProductLover"},
        {"text": "Is it worth the price?", "username": "BudgetBuyer"},
        {"text": "I want to buy this!", "username": "ReadyToBuy"},
        {"text": "Thanks for the great review!", "username": "AppreciativeViewer"}
    ]
    
    # Generate responses
    responses = responder.respond_to_comments(test_comments, use_ai=False)
    
    # Save responses
    responder.save_responses(responses)


if __name__ == "__main__":
    main() 