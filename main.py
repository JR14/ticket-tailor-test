from webhook_ingestor import get_webhooks
from webhook_processor import WebhookProcessor
import logging

if __name__ == '__main__': 
    logging.basicConfig(level=logging.INFO)

    webhooks = get_webhooks('webhooks.txt')
    processor = WebhookProcessor()
    processor.process_webhooks(webhooks)


