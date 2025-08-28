from fastapi import FastAPI, Form, Response, status
from fastapi.openapi.utils import get_openapi
from email.parser import Parser as EmailParser
import re
import uuid
import os
import re

app = FastAPI(title="Mock SMS and Email Service", version="1.0.0")


def is_valid_phone_number(phone_number: str) -> bool:
    """Perform simple validatation of phone numbers.

    Strips non-digit characters and checks for a plausible length.
    """
    cleaned_number = re.sub(r"\D", "", phone_number)
    # Common US phone numbers are 10 digits, or 11 with a country code.
    return 10 <= len(cleaned_number) <= 11


def is_valid_email_address(email_addr: str) -> bool:
    """Perform simple validatation of email addresses."""
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_addr)


def parse_email_details(raw_email: str) -> dict:
    """Parse details of an incoming email."""
    try:
        email_msg = EmailParser().parsestr(raw_email, headersonly=True)
    except ValueError:
        return None
    return {
        "to_addrs": email_msg.get_all("To", []),
        "cc_addrs": email_msg.get_all("CC", []),
        "bcc_addrs": email_msg.get_all("BCC", []),
        "from_addr": email_msg.get("From", ""),
        "subject": email_msg.get("Subject", ""),
    }


@app.post(
    "/sms/send",
    responses={
        200: {
            "description": "Message sent successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message_id": "mock-123e4567-e89b-12d3-a456-426614174000",
                        "to_number": "+15558675309",
                        "from_number": "+15017122661",
                        "body": "Hi there!",
                    }
                }
            },
        },
        400: {
            "description": "Bad Request - Invalid phone number",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "The 'To' phone number '123' is not a valid phone number.",
                    }
                }
            },
        },
        429: {
            "description": "Too Many Requests - Any number ending with 4291111111 will trigger this error.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Too many requests",
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - Any number ending with 5001111111 will trigger this error.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal Server Error",
                    }
                }
            },
        },
    },
)
async def send_sms(
    response: Response,
    to_number: str = Form(...),
    from_number: str = Form(...),
    body: str = Form(...),
):
    # Determine if error behavior should be enabled based on environment variable
    enable_error_behavior = (
        os.getenv("MOCK_ERROR_BEHAVIOR", "enabled").lower() == "enabled"
    )

    # Clean the 'To' number to easily check for special cases
    cleaned_to_number = re.sub(r"\D", "", to_number)

    if enable_error_behavior:
        # Return 429 Too Many Requests for any number ending with 4291111111
        if cleaned_to_number.endswith("4291111111"):
            response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
            return {"status": "error", "message": "Too many requests"}

        # Return 500 Internal Server Error for any number ending with 5001111111
        if cleaned_to_number.endswith("5001111111"):
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "error", "message": "Internal Server Error"}

    # Validate phone numbers for proper format
    if not is_valid_phone_number(to_number):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": "error",
            "message": f"The 'To' phone number '{to_number}' is not a valid phone number.",
        }

    # If all checks pass, return a success response (200 OK)
    print(f"Mock SMS sent to {to_number} from {from_number}: {body}")
    response.status_code = status.HTTP_200_OK
    return {
        "status": "success",
        "message_id": f"mock-{uuid.uuid4()}",
        "to_number": to_number,
        "from_number": from_number,
        "body": body,
    }


@app.post(
    "/email/send",
    responses={
        200: {
            "description": "Message sent successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message_id": "mock-123e4567-e89b-12d3-a456-426614174000",
                        "to_number": "+15558675309",
                        "from_number": "+15017122661",
                        "body": "Hi there!",
                    }
                }
            },
        },
        400: {
            "description": "Bad Request - Invalid phone number",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "The 'To' phone number '123' is not a valid phone number.",
                    }
                }
            },
        },
        429: {
            "description": "Too Many Requests - Any number ending with 4291111111 will trigger this error.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Too many requests",
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error - Any number ending with 5001111111 will trigger this error.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Internal Server Error",
                    }
                }
            },
        },
    },
)
async def send_email(
    response: Response,
    message: str = Form(...),
):
    # Determine if error behavior should be enabled based on environment variable
    enable_error_behavior = (
        os.getenv("MOCK_ERROR_BEHAVIOR", "enabled").lower() == "enabled"
    )

    details = parse_email_details(message)
    if not details:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": "error",
            "message": "The email could not be parsed for headers.",
        }

    from_addr = details["from_addr"]
    if not is_valid_email_address(from_addr):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": "error",
            "message": f"The 'From' email address '{details['from_addr']}' is not a valid email address.",
        }

    to_addrs = details["to_addrs"]
    for addr in to_addrs:
        if not is_valid_email_address(addr):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                "status": "error",
                "message": f"The 'To' email address '{addr}' is not a valid email address.",
            }

    subject = details["subject"] if details["subject"] else "(No Subject)"

    if enable_error_behavior:
        # Return 429 Too Many Requests for any email ending with .ca
        if from_addr.endswith(".ca"):
            response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
            return {"status": "error", "message": "Too many requests"}

        # Return 500 Internal Server Error for any number ending with .gov
        if from_addr.endswith(".gov"):
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"status": "error", "message": "Internal Server Error"}

    # If all checks pass, return a success response (200 OK)
    print(f"Mock email sent to {to_addrs} from {from_addr}: {details['subject']}")
    response.status_code = status.HTTP_200_OK
    return {
        "status": "success",
        "message_id": f"mock-{uuid.uuid4()}",
        "to_addrs": to_addrs,
        "from_addr": from_addr,
        "subject": subject,
    }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    enable_error_behavior = (
        os.getenv("MOCK_ERROR_BEHAVIOR", "enabled").lower() == "enabled"
    )

    if not enable_error_behavior:
        for path in ["email/send", "/sms/send"]:
            if (
                path in openapi_schema["paths"]
                and "post" in openapi_schema["paths"][path]
            ):
                openapi_schema["paths"][path]["post"]["responses"].pop("429", None)
                openapi_schema["paths"][path]["post"]["responses"].pop("500", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
