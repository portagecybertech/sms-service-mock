# Mock SMS Service

This is a mock SMS service that mimics the Twilio API for sending SMS messages. It's intended for local development and testing.

## Prerequisites

- Docker and Docker Compose installed on your machine.

## How to Run

This project uses Docker Compose to run two instances of the mock server simultaneously, each with a different configuration.

1.  **Build and run the containers:**

    Open a terminal in the project root and run:
    ```bash
    docker-compose up --build
    ```
    This will start two containers:
    -   **Instance 1 (Error Behavior Enabled):** Available at `http://localhost:8000`. This instance will return `429` and `500` errors for specific numbers.
    -   **Instance 2 (Error Behavior Disabled):** Available at `http://localhost:8001`. This instance will *not* return `429` or `500` errors.

2.  **To stop the services**, press `Ctrl+C` in the terminal, then run:
    ```bash
    docker-compose down
    ```

## API Endpoint

-   **Endpoint:** `POST /sms/send`
-   **Content-Type:** `application/x-www-form-urlencoded`

### Form Parameters

-   `to_number`: The recipient's phone number.
-   `from_number`: The sender's phone number.
-   `body`: The text of the message.

### Example Usage with cURL

You can test the service with a `cURL` command.

**To test the success case (either instance):**
```bash
curl -X POST 'http://localhost:8000/sms/send' \
--data-urlencode "to_number=+15558675309" \
--data-urlencode "from_number=+15017122661" \
--data-urlencode "body=Hi there!"
```

**To trigger a `429` error (on port 8000):**
```bash
curl -X POST 'http://localhost:8000/sms/send' \
--data-urlencode "to_number=+14298675309" \
--data-urlencode "from_number=+15017122661" \
--data-urlencode "body=Hi there!"
```

The server will log the received message to the console and return a JSON response. 