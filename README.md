# Mock SMS Service

This is a mock SMS service that mimics the Twilio API for sending SMS messages. It's intended for local development and testing, allowing services that depend on Twilio to be developed without sending actual SMS messages.

## Prerequisites

- Docker installed on your machine.

## How to Run

1.  **Build the Docker image:**

    Open a terminal in the project root directory and run the following command to build the Docker image:

    ```bash
    docker build -t mock-sms .
    ```

2.  **Run the Docker container:**

    After the image is built, you can run the service in a Docker container with this command:

    ```bash
    docker run -d -p 8000:8000 --name mock-sms mock-sms
    ```

    - `-d` runs the container in detached mode.
    - `-p 8000:8000` maps port 8000 of the container to port 8000 on your local machine.
    - `--name mock-sms` gives the container a memorable name.

## API Endpoint

The mock service exposes one endpoint to simulate sending an SMS:

-   **Endpoint:** `POST /sms/send`
-   **Host:** `http://localhost:8000`
-   **Content-Type:** `application/x-www-form-urlencoded`

### Form Parameters

-   `To`: The recipient's phone number.
-   `From`: The sender's phone number.
-   `Body`: The text of the message.

### Example Usage with cURL

You can test the running service with a `cURL` command like this:

```bash
curl -X POST 'http://localhost:8000/sms/send' \
--data-urlencode "To=+15558675309" \
--data-urlencode "From=+15017122661" \
--data-urlencode "Body=Hi there!"
```

The server will log the received message to the console and return a JSON response. 