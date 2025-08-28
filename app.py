from fastapi import FastAPI, Form, Response, status
from fastapi.openapi.utils import get_openapi
import re
import uuid
import os # Import the os module to access environment variables

app = FastAPI(title="Mock SMS Service", version="1.0.0")


def is_valid_phone_number(phone_number: str) -> bool:
    """A simple validator for phone numbers.
    Strips non-digit characters and checks for a plausible length.
    """
    cleaned_number = re.sub(r'\D', '', phone_number)
    # Common US phone numbers are 10 digits, or 11 with a country code.
    return 10 <= len(cleaned_number) <= 11


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
            "description": "Too Many Requests - Any number starting with 429 will trigger this error.",
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
            "description": "Internal Server Error - Any number starting with 500 will trigger this error.",
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
    enable_error_behavior = os.getenv("MOCK_ERROR_BEHAVIOR", "enabled").lower() == "enabled"

    # Clean the 'To' number to easily check for special cases
    cleaned_to_number = re.sub(r'\D', '', to_number)

    if enable_error_behavior:
        # Return 429 Too Many Requests for any number starting with 429
        if cleaned_to_number.startswith('429'):
            response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
            return {"status": "error", "message": "Too many requests"}

        # Return 500 Internal Server Error for any number starting with 500
        if cleaned_to_number.startswith('500'):
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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    enable_error_behavior = os.getenv("MOCK_ERROR_BEHAVIOR", "enabled").lower() == "enabled"

    if not enable_error_behavior:
        path = "/sms/send"
        if path in openapi_schema["paths"] and "post" in openapi_schema["paths"][path]:
            openapi_schema["paths"][path]["post"]["responses"].pop("429", None)
            openapi_schema["paths"][path]["post"]["responses"].pop("500", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
