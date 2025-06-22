#!/usr/bin/env python3
"""
AWS API Client - Simple GET requests to AWS services
"""

import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AWSClient:
    """Simple AWS API client using GET requests without authentication"""

    def __init__(self, api_url: str, timeout: int = 10):
        self.api_url = api_url
        self.timeout = timeout
        self.last_response = None
        self.last_response_text = None

    def call_api(self) -> bool:
        """Make simple GET request to AWS service"""
        try:
            logger.info(f"Calling AWS service: {self.api_url}")
            response = requests.get(self.api_url, timeout=self.timeout)

            if response.status_code == 200:
                logger.info(f"API call successful: {response.status_code}")
                logger.info(f"Response: {response.text}")

                # Store the response for Llama processing
                self.last_response = response
                self.last_response_text = response.text

                return True
            else:
                logger.error(
                    f"API call failed: {response.status_code} - {response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

    def get_last_response_text(self) -> Optional[str]:
        """Get the text from the last successful response"""
        return self.last_response_text


def create_aws_client(config: Dict[str, Any]) -> AWSClient:
    """Create a simple AWS client"""
    api_url = config.get("api_url", "https://api.example.com/endpoint")
    timeout = config.get("timeout", 10)

    logger.info("Using simple GET request (no authentication)")
    return AWSClient(api_url, timeout)
