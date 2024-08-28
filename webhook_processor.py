import logging
import time
import heapq
from urllib.parse import ParseResult
from typing import Dict, List, Set
import requests

from webhook import Webhook, PrioritizedWebhook

logger = logging.getLogger(__name__)


class WebhookProcessor:
    def __init__(
        self,
        max_delay_time: int = 60,
        initial_delay_time: int = 1,
        exponential_backoff_factor: int = 2,
        max_url_failure: int = 5,
        response_timeout: int = 2,
    ):
        self.max_delay_time = max_delay_time
        self.initial_delay_time = initial_delay_time
        self.exponential_backoff_factor = exponential_backoff_factor
        self.max_url_failure = max_url_failure
        self.response_timeout = response_timeout

    def _send_webhook(self, webhook: Webhook) -> bool:
        try:
            response = requests.post(
                webhook.url,
                json={
                    "id": webhook.order_id,
                    "event": webhook.event,
                    "name": webhook.name,
                },
                timeout=self.response_timeout,
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.warning(
                "Webhook %s to %s failed: %s", webhook.order_id, webhook.url, e
            )
            return False

    def _handle_failed_send(
        self,
        prioritized_webhook: PrioritizedWebhook,
        queue: List[PrioritizedWebhook],
        failure_tracker: Dict[ParseResult, int],
    ) -> None:
        new_delay = (
            prioritized_webhook.seconds_until_next_attempt
            * self.exponential_backoff_factor
        )
        webhook = prioritized_webhook.webhook

        if new_delay > self.max_delay_time:
            failure_tracker[webhook.url] = failure_tracker.get(webhook.url, 0) + 1
            logger.warning(
                "Webhook %s to %s failed after reaching max delay. Total failures for this URL: %s",
                webhook.order_id,
                webhook.url,
                failure_tracker[webhook.url],
            )
        else:
            logger.info(
                "Retrying webhook %s in %.2f seconds", webhook.order_id, new_delay
            )
            heapq.heappush(
                queue, PrioritizedWebhook(time.time() + new_delay, new_delay, webhook)
            )

    def process_webhooks(self, webhooks: Set[Webhook]) -> None:
        failure_tracker: Dict[ParseResult, int] = {}
        queue: List[PrioritizedWebhook] = []

        for webhook in webhooks:
            heapq.heappush(
                queue,
                PrioritizedWebhook(
                    time.time(),
                    self.initial_delay_time / self.exponential_backoff_factor,
                    webhook,
                ),
            )

        while queue:
            current_prioritized_webhook = heapq.heappop(queue)
            webhook = current_prioritized_webhook.webhook

            if failure_tracker.get(webhook.url, 0) >= self.max_url_failure:
                logger.warning(
                    "Skipping webhook %s as URL %s has reached the maximum number of failures.",
                    webhook.order_id,
                    webhook.url,
                )
                continue

            current_time = time.time()

            if current_time < current_prioritized_webhook.next_retry_time:
                logger.info(current_time)
                logger.info(current_prioritized_webhook.next_retry_time)
                time.sleep(current_prioritized_webhook.next_retry_time - current_time)

            if self._send_webhook(webhook):
                logger.info(
                    "Webhook %s successfully sent to %s", webhook.order_id, webhook.url
                )
            else:
                self._handle_failed_send(
                    current_prioritized_webhook, queue, failure_tracker
                )

        logger.info("Finished processing all webhooks.")
