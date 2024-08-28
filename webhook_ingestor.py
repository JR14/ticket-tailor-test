from csv import DictReader
from webhook import Webhook


def _parse_row(row: dict) -> Webhook:
    return Webhook(
        url=row["URL"].strip(),
        order_id=row["ORDER ID"],
        name=row["NAME"],
        event=row["EVENT"],
    )


def get_webhooks(filename: str) -> list[Webhook]:
    webhooks = []
    with open(filename, "r") as file:
        reader = DictReader(file, skipinitialspace=True)
        for row in reader:
            webhooks.append(_parse_row(row))
    return webhooks
