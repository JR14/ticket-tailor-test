# Ticket Tailor Test

## Setup
To run this project, download all files and run the following commands in the project root of the terminal/command line:
```
pip install -r requirements.txt
python main.py
```

## Tests
To do tests run the following command in the project root of the terminal/command line:
`python test.py`

## Design Decisions
### webhook.py
This contains the dataclasses, which is a pythonic way of introducing OOP concepts. The webhook is a straightforward object offering a bit more type safety than a dict, used internally and then easily converted to and from for I/O. Only notable field is url having type ParseResult for some added type safety on the url. The prioritized webhook is seperate as it contains a bit more logic and is only relevant for the implementation of the priority queue in webhook_processor, as it enables a simple ordering on the webhooks without changing the core behaviour of the webhook class.

### webhook_ingestor.py
Mainly for convenience, although the idea being that it could be expanded for multiple data streams in the future, and keeping that logic in its own class is neat. Currently only works on very specific CSV input data.

### webhook_processor.py
Most important file, handles the main logic of the application. WebhookProcessor is an object so that the class constants can be changed, mainly useful for testing purposes - being able to divide the wait times by 100. process_webhooks() uses a priority queue to handle the webhooks in order to reduce downtime, with more time / access to libraries (such as aiohttp) an async solution would be better, but given the constraints it was decided a single threaded priority queue would be used so that less time is wasted waiting for the backoff to complete. The program works on the assumption that unless it's waiting all operations happen instantly, which is not true in practice and especially for large datasets this would become an issue - by the time every webhook has been requested once the initial backoff time might well have expired - but this likely isn't too big of an assumption to make, especially if the delay is greater than a second it would take ~50,000 requests to make this an issue, and being slightly late for the backoff is also likely not a problem. The code for setting up the initial queue is a little weird - having the initial delay being divided by the factor, this was done to make the rest of the code neater though might be contentious. Because it's using a priority queue, the current_prioritized_webhook is always the one with the smallest next_retry_time, meaning the if next_retry_time is after the current_time the program has nothing to do but wait for that to elapse.

### test.py
The tests are relatively threadbare but cover the basics - ensuring the backoff procedure works, that endpoints are blacklisted, and a happy path with a high throughput - the large number of webhooks for this one was to ensure there were no hidden waits, but kept low enough they complete within less than 0.2s. 

## Security
Overall the application is quite insecure, urls are not sanitized, nor are the payloads. This is deliberate as it's being treated as a proof of concept, but would be relatively easy to implement by extending sanitization for the Webhooks dataclass. 
