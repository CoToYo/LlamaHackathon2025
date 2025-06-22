#!/usr/bin/env python3
"""
Simple Orchestrator - Periodically calls AWS service and feeds response to Llama API
"""

import time
import logging
import json
import os
from typing import Dict, Any, Optional
from aws_client import create_aws_client
from llama_client import create_llama_client

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Temporarily set to DEBUG to see response structure
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("orchestrator.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator that manages periodic API calls to AWS and Llama"""

    def __init__(self, config: Dict[str, Any]):
        self.interval = config.get("interval", 60)  # seconds
        self.aws_client = create_aws_client(config)
        self.llama_client = create_llama_client(config)

    def process_workflow(self) -> bool:
        """Process the complete workflow: AWS API -> Llama API"""
        try:
            # Step 1: Call AWS API
            logger.info("=== Starting AWS API Call ===")
            aws_success = self.aws_client.call_api()

            if not aws_success:
                logger.error("AWS API call failed, skipping Llama processing")
                return False

            # Step 2: Process AWS response with Llama
            if self.llama_client:
                logger.info("=== Starting Llama Processing ===")
                aws_response_text = self.aws_client.get_last_response_text()

                if aws_response_text:
                    llama_response = self.llama_client.process_aws_response(
                        aws_response_text
                    )

                    if llama_response:
                        logger.info("=== Llama Processing Complete ===")
                        logger.info(f"Llama Analysis: {llama_response}")
                        return True
                    else:
                        logger.error("Llama processing failed")
                        return False
                else:
                    logger.error("No AWS response text available for Llama processing")
                    return False
            else:
                logger.warning("Llama client not available, skipping Llama processing")
                return True  # Still consider AWS success as workflow success

        except Exception as e:
            logger.error(f"Error in workflow processing: {e}")
            return False

    def run(self):
        """Main orchestrator loop"""
        logger.info("Starting Orchestrator service")
        logger.info(f"AWS API URL: {self.aws_client.api_url}")
        logger.info(f"Interval: {self.interval} seconds")
        logger.info(f"Timeout: {self.aws_client.timeout} seconds")

        if self.llama_client:
            model_info = self.llama_client.get_model_info()
            logger.info(f"Llama Model: {model_info['model']}")
            logger.info(f"Llama Max Tokens: {model_info['max_tokens']}")
            logger.info(f"Llama Temperature: {model_info['temperature']}")
        else:
            logger.warning(
                "Llama client not configured - will only process AWS API calls"
            )

        while True:
            try:
                success = self.process_workflow()
                if success:
                    logger.info("Workflow completed successfully")
                else:
                    logger.warning("Workflow failed, will retry on next interval")

                logger.info(f"Waiting {self.interval} seconds before next call...")
                time.sleep(self.interval)

            except KeyboardInterrupt:
                logger.info("Orchestrator stopped by user")
                break
            except Exception as e:
                logger.error(f"Critical error in main loop: {e}")
                logger.info("Waiting 10 seconds before retrying...")
                time.sleep(10)


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment variables"""
    config = {
        "api_url": os.getenv(
            "ORCHESTRATOR_API_URL", "https://api.example.com/endpoint"
        ),
        "interval": int(os.getenv("ORCHESTRATOR_INTERVAL", "60")),
        "timeout": int(os.getenv("ORCHESTRATOR_TIMEOUT", "10")),
        # Llama configuration
    }

    # Try to load from config file if it exists
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r") as f:
                file_config = json.load(f)
                config.update(file_config)
    except Exception as e:
        logger.warning(f"Could not load config file: {e}")

    return config


def main():
    """Main entry point"""
    try:
        config = load_config()
        orchestrator = Orchestrator(config)
        orchestrator.run()
    except Exception as e:
        logger.error(f"Failed to start orchestrator: {e}")
        exit(1)


if __name__ == "__main__":
    main()
