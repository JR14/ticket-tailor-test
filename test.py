import unittest
from unittest.mock import patch
from webhook import Webhook
from webhook_processor import WebhookProcessor


class TestWebhookProcessor(unittest.TestCase):

    @patch("webhook_processor.WebhookProcessor._send_webhook", return_value=False)
    def test_process_webhooks_correct_number_failed_calls(self, mock_send_webhook):
        webhook = Webhook(
            order_id=1, event="test_event", name="Test", url="https://example.com"
        )
        processor = WebhookProcessor(
            max_delay_time=0.05, initial_delay_time=0.01, exponential_backoff_factor=3
        )

        processor.process_webhooks([webhook])

        # Assert _send_webhook called 3 times - after 0, 0.01, 0.03 seconds
        self.assertEqual(mock_send_webhook.call_count, 3)

    @patch("webhook_processor.WebhookProcessor._send_webhook", return_value=False)
    def test_process_webhooks_ignores_url(self, mock_send_webhook):
        webhook_1 = Webhook(
            order_id=1, event="test_event", name="Test", url="https://example.com"
        )
        webhook_2 = Webhook(
            order_id=2, event="test_event", name="Test", url="https://example.com"
        )
        processor = WebhookProcessor(max_url_failure=1, max_delay_time=0)

        processor.process_webhooks([webhook_1, webhook_2])

        self.assertEqual(mock_send_webhook.call_count, 1)

    @patch("webhook_processor.WebhookProcessor._send_webhook", return_value=True)
    def test_process_webhooks_correct_success_response(self, mock_send_webhook):
        webhooks = []
        max_webhooks = 10**4
        for i in range(0, max_webhooks):
            webhooks.append(
                Webhook(
                    order_id=i,
                    event="test_event",
                    name="Test",
                    url="https://example.com",
                )
            )
        processor = WebhookProcessor()

        processor.process_webhooks(webhooks)

        self.assertEqual(mock_send_webhook.call_count, max_webhooks)


if __name__ == "__main__":
    unittest.main()
