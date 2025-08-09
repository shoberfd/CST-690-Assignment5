import logging
import logging.handlers
import json
import time
import random
import requests
from prometheus_client import start_http_server, Summary
import os

# --- Logging Configuration ---
class JsonFormatter(logging.Formatter):
    """A custom formatter to output log records as JSON."""
    def format(self, record):
        # Create a dictionary for the log record with custom fields
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "transaction_id": getattr(record, 'transaction_id', 'N/A'),
            "duration_ms": getattr(record, 'duration_ms', 0),
            "outcome": getattr(record, 'outcome', 'N/A')
        }
        return json.dumps(log_record)

def setup_logging():
    """Sets up a timed rotating file handler with JSON formatting."""
    # Ensure logs directory exists before writing to it
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Use a timed handler to rotate log files daily
    handler = logging.handlers.TimedRotatingFileHandler(
        filename="logs/inventory.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8"
    )
    handler.setFormatter(JsonFormatter())
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

# --- Prometheus Metrics Instrumentation ---
# Create a metric to track how long a batch takes to process
REQUEST_LATENCY = Summary('inventory_batch_duration_seconds', 'Inventory batch duration in seconds')

# --- Core Bot Logic with Error Recovery ---
def process_inventory_item(item):
    """Simulates a function that might fail due to a temporary error."""
    # Simulate a 20% chance of a request failing
    if random.random() < 0.2:
        raise requests.exceptions.RequestException("Simulated API failure")
    return {"status": "success", "item_id": item}

def robust_process_item(item, max_retries=5):
    """Processes an item with retries and increasing wait times."""
    logger = logging.getLogger()
    retries = 0
    while retries < max_retries:
        try:
            result = process_inventory_item(item)
            logger.info("Transaction processed successfully.", extra={'transaction_id': f"TX-{item}", 'duration_ms': 100, 'outcome': 'success'})
            return result
        except requests.exceptions.RequestException as e:
            retries += 1
            delay = 2 ** retries  # Wait longer with each retry (e.g., 2, 4, 8 seconds)
            logger.warning(f"Error processing item {item}: {e}. Retrying in {delay} seconds...", extra={'transaction_id': f"TX-{item}", 'outcome': 'retry'})
            time.sleep(delay)
    
    # If all retries fail, log the final failure
    logger.error(f"Failed to process item {item} after {max_retries} attempts. Sending to dead-letter queue.", extra={'transaction_id': f"TX-{item}", 'outcome': 'failed'})
    return {"status": "failed", "item_id": item}

@REQUEST_LATENCY.time()
def process_inventory_batch():
    """Simulates processing a batch of inventory items and records the time."""
    logger = logging.getLogger()
    item_ids = [f"SKU-{random.randint(1000, 9999)}" for _ in range(5)]
    for item in item_ids:
        robust_process_item(item)
    logger.info("Batch of inventory items processed.")

# --- Main Execution Block ---
if __name__ == "__main__":
    setup_logging()
    
    # Start the web server to expose metrics for a Prometheus scraper
    start_http_server(9100)
    print("Prometheus metrics server started on port 9100.")
    print("Bot is now processing inventory batches...")
    
    # Run the bot logic continuously
    while True:
        process_inventory_batch()
        # Wait a random amount of time before the next batch
        time.sleep(random.uniform(1, 3))