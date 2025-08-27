from fastapi import FastAPI, Form, Response, status
import re
import uuid

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
                        "message": "The 'To' phone number '+123' is not a valid phone number.",
                    }
                }
            },
        },
        429: {
            "description": "Too Many Requests - Specific number triggered rate limit 429 111 1111",
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
            "description": "Internal Server Error - Specific number triggered server error 500 111 1111",
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
    to_number: str = Form(..., alias="To"),
    from_number: str = Form(..., alias="From"),
    body: str = Form(..., alias="Body"),
):
    # Clean the 'To' number to easily check for special cases
    cleaned_to_number = re.sub(r'\D', '', to_number)

    # Return 429 Too Many Requests for a specific number
    if cleaned_to_number.endswith('4291111111'):
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return {"status": "error", "message": "Too many requests"}

    # Return 500 Internal Server Error for a specific number
    if cleaned_to_number.endswith('5001111111'):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "error", "message": "Internal Server Error"}

    # Validate phone numbers for proper format
    if not is_valid_phone_number(to_number):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": "error",
            "message": f"The 'To' phone number '{to_number}' is not a valid phone number.",
        }

    if not is_valid_phone_number(from_number):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "status": "error",
            "message": f"The 'From' phone number '{from_number}' is not a valid phone number.",
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
