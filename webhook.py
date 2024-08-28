from dataclasses import dataclass, field
from urllib.parse import ParseResult


@dataclass
class Webhook:
    url: ParseResult
    order_id: int
    name: str
    event: str


@dataclass(order=True)
class PrioritizedWebhook:
    next_retry_time: float
    seconds_until_next_attempt: float
    webhook: Webhook = field(compare=False)
