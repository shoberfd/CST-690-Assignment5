import logging
import logging.handlers
import json
import time
import random
import requests
from prometheus_client import start_http_server, Summary, Counter
import os

# --- Logging Configuration ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
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
    if not os.path.exists('logs'):
        os.makedirs('logs')

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
REQUEST_LATENCY = Summary('inventory_batch_duration_seconds', 'Inventory batch duration in seconds')
TRANSACTIONS_PROCESSED = Counter('inventory_transactions_total', 'Total number of inventory items processed', ['outcome'])

# --- Core Bot Logic with Error Recovery ---
def process_inventory_item(item):
    if random.random() < 0.2:
        # A simulated API failure using the imported requests library
        raise requests.exceptions.RequestException("Simulated API failure")
    return {"status": "success", "item_id": item}

def robust_process_item(item, max_retries=5):
    logger = logging.getLogger()
    retries = 0
    while retries < max_retries:
        try:
            result = process_inventory_item(item)
            logger.info("Transaction processed successfully.", extra={'transaction_id': f"TX-{item}", 'duration_ms': 100, 'outcome': 'success'})
            TRANSACTIONS_PROCESSED.labels(outcome='success').inc()
            return result
        except requests.exceptions.RequestException as e:
            retries += 1
            delay = 2 ** retries
            logger.warning(f"Error processing item {item}: {e}. Retrying in {delay} seconds...", extra={'transaction_id': f"TX-{item}", 'outcome': 'retry'})
            time.sleep(delay)
    
    logger.error(f"Failed to process item {item} after {max_retries} attempts. Sending to dead-letter queue.", extra={'transaction_id': f"TX-{item}", 'outcome': 'failed'})
    TRANSACTIONS_PROCESSED.labels(outcome='failed').inc()
    return {"status": "failed", "item_id": item}

@REQUEST_LATENCY.time()
def process_inventory_batch():
    logger = logging.getLogger()
    item_ids = [f"SKU-{random.randint(1000, 9999)}" for _ in range(5)]
    for item in item_ids:
        robust_process_item(item)
    print("Batch processed.")
    logger.info("Batch of inventory items processed.")

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        print("Starting script...")
        setup_logging()
        print("Logging is set up.")
        start_http_server(9100)
        print("Prometheus metrics server started on port 9100.")
        print("Bot is now processing inventory batches...")
        
        while True:
            process_inventory_batch()
            time.sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")