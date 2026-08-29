import re
import json
from datetime import datetime

from models.llm import generate_response
from utils.database import add_customer, add_booking


# --------------------------------------------------
# BOOKING FIELDS
# --------------------------------------------------

BOOKING_FIELDS = [
    "name",
    "email",
    "phone",
    "booking_type",
    "date",
    "time"
]


# --------------------------------------------------
# CREATE EMPTY BOOKING
# --------------------------------------------------

def create_empty_booking():
    """Create an empty booking dictionary."""

    return {
        "name": None,
        "email": None,
        "phone": None,
        "booking_type": None,
        "date": None,
        "time": None
    }


# --------------------------------------------------
# CHECK EMAIL
# --------------------------------------------------

def is_valid_email(email):
    """Check whether an email address is valid."""

    if not email or not isinstance(email, str):
        return False

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(pattern, email.strip()) is not None


# --------------------------------------------------
# CHECK PHONE
# --------------------------------------------------

def is_valid_phone(phone):
    """Check whether a phone number is valid."""

    if not phone:
        return False

    digits = re.sub(r"\D", "", str(phone))

    return 10 <= len(digits) <= 15


# --------------------------------------------------
# CHECK DATE
# --------------------------------------------------

def is_valid_date(date_string):
    """Check whether the date follows YYYY-MM-DD."""

    if not date_string or not isinstance(date_string, str):
        return False

    try:

        datetime.strptime(
            date_string.strip(),
            "%Y-%m-%d"
        )

        return True

    except (ValueError, TypeError):

        return False


# --------------------------------------------------
# CHECK TIME
# --------------------------------------------------

def is_valid_time(time_string):
    """Check whether the time follows HH:MM."""

    if not time_string or not isinstance(time_string, str):
        return False

    try:

        datetime.strptime(
            time_string.strip(),
            "%H:%M"
        )

        return True

    except (ValueError, TypeError):

        return False


# --------------------------------------------------
# FIND MISSING FIELDS
# --------------------------------------------------

def get_missing_fields(booking):
    """Return the booking fields that are still missing."""

    missing = []

    for field in BOOKING_FIELDS:

        if not booking.get(field):
            missing.append(field)

    return missing


# --------------------------------------------------
# CHECK WHETHER BOOKING IS COMPLETE
# --------------------------------------------------

def is_booking_complete(booking):
    """Return True when all required fields are present."""

    return len(get_missing_fields(booking)) == 0


# --------------------------------------------------
# UPDATE BOOKING
# --------------------------------------------------

def update_booking(
    booking,
    field,
    value
):
    """Update one booking field."""

    if field in BOOKING_FIELDS:
        booking[field] = value

    return booking


# --------------------------------------------------
# BOOKING SUMMARY
# --------------------------------------------------

def create_booking_summary(booking):
    """Create a readable booking confirmation."""

    return f"""
Please confirm your booking:

Name: {booking["name"]}

Email: {booking["email"]}

Phone: {booking["phone"]}

Service: {booking["booking_type"]}

Date: {booking["date"]}

Time: {booking["time"]}

Would you like me to confirm this booking?

"""


# --------------------------------------------------
# DETERMINISTIC BOOKING EXTRACTION
# --------------------------------------------------

def _extract_without_llm(user_message):
    """
    Extract obvious booking details without Gemini.

    This is used as a safety fallback when Gemini is
    unavailable or when the message is a simple answer
    such as a name, email, phone, date, or time.
    """

    message = str(user_message).strip()

    result = {
        "is_booking": False,
        "name": None,
        "email": None,
        "phone": None,
        "booking_type": None,
        "date": None,
        "time": None
    }

    if not message:
        return result

    lower_message = message.lower()

    # ----------------------------------------------
    # EMAIL
    # ----------------------------------------------

    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        message
    )

    if email_match:

        result["email"] = email_match.group(0)

        result["is_booking"] = True


    # ----------------------------------------------
    # PHONE
    # ----------------------------------------------

    phone_match = re.search(
        r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)",
        message
    )

    if phone_match:

        phone_value = phone_match.group(0).strip()

        if is_valid_phone(phone_value):

            result["phone"] = phone_value

            result["is_booking"] = True


    # ----------------------------------------------
    # DATE
    # ----------------------------------------------

    date_match = re.search(
        r"\b\d{4}-\d{2}-\d{2}\b",
        message
    )

    if date_match:

        date_value = date_match.group(0)

        if is_valid_date(date_value):

            result["date"] = date_value

            result["is_booking"] = True


    # ----------------------------------------------
    # TIME
    # ----------------------------------------------

    time_match = re.search(
        r"\b(?:[01]\d|2[0-3]):[0-5]\d\b",
        message
    )

    if time_match:

        result["time"] = time_match.group(0)

        result["is_booking"] = True


    # ----------------------------------------------
    # SALON SERVICES
    # ----------------------------------------------

    services = {
        "haircut": "Haircut",
        "hair spa": "Hair Spa",
        "facial": "Facial",
        "manicure": "Manicure",
        "hair coloring": "Hair Coloring",
        "hair colour": "Hair Coloring",
        "hair color": "Hair Coloring"
    }

    for service_key, service_name in services.items():

        if service_key in lower_message:

            result["booking_type"] = service_name

            result["is_booking"] = True

            break


    # ----------------------------------------------
    # SIMPLE NAME ANSWER
    # ----------------------------------------------

    # A short alphabetic response such as "Rahul" is
    # very likely the name when answering a booking question.
    if (
        result["email"] is None
        and result["phone"] is None
        and result["date"] is None
        and result["time"] is None
        and result["booking_type"] is None
        and re.fullmatch(
            r"[A-Za-z][A-Za-z .'-]{1,49}",
            message
        )
    ):

        result["name"] = message.strip()

        result["is_booking"] = True


    return result


# --------------------------------------------------
# EXTRACT BOOKING INFORMATION
# --------------------------------------------------

def extract_booking_details(user_message):
    """
    Ask Gemini to identify booking intent and extract
    booking information.

    If Gemini is temporarily unavailable or returns
    invalid JSON, use deterministic extraction so that
    simple booking replies can still be processed.
    """

    if user_message is None:
        return _extract_without_llm("")

    user_message = str(user_message).strip()

    if not user_message:
        return _extract_without_llm("")


    prompt = f"""
You are a booking assistant for Glow Salon.

Analyze the user's message.

Determine whether the user wants to make a booking.

If the user wants to make a booking, extract any
booking information that is present.

Return ONLY valid JSON.

Use exactly these keys:

{{
    "is_booking": true or false,
    "name": null or string,
    "email": null or string,
    "phone": null or string,
    "booking_type": null or string,
    "date": null or string,
    "time": null or string
}}

Important rules:

1. Do not invent information.
2. Use null when information is not provided.
3. Date must use YYYY-MM-DD when possible.
4. Time must use HH:MM in 24-hour format when possible.
5. The booking_type should be the salon service.
6. If the user is only asking a general question,
   set is_booking to false.
7. If the user gives a short name such as "Rahul",
   treat it as the name.
8. If the user gives an email address, extract it exactly.
9. If the user gives a phone number, extract it exactly.

Today's date is 2026-08-29.

USER MESSAGE:

{user_message}
"""

    try:

        response = generate_response(prompt)

        response = response.strip()

        # Remove possible markdown code fences
        if response.startswith("```"):

            response = response.replace("```json", "")
            response = response.replace("```", "")

        response = response.strip()

        data = json.loads(response)

        # Make sure all expected keys exist
        result = {
            "is_booking": bool(data.get("is_booking", False)),
            "name": data.get("name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "booking_type": data.get("booking_type"),
            "date": data.get("date"),
            "time": data.get("time")
        }

        # Deterministic extraction is used to recover
        # simple values Gemini may have missed.
        fallback_data = _extract_without_llm(user_message)

        for field in BOOKING_FIELDS:

            if not result[field] and fallback_data[field]:

                result[field] = fallback_data[field]

        if fallback_data["is_booking"]:

            result["is_booking"] = True

        return result

    except Exception as error:

        print(
            f"Gemini booking extraction failed: {error}"
        )

        return _extract_without_llm(user_message)


# --------------------------------------------------
# BOOKING PERSISTENCE TOOL
# --------------------------------------------------

def booking_persistence_tool(booking):
    """
    Save a confirmed booking to the database.

    Returns:
        success: True/False
        booking_id: generated database ID
        error: error message if something fails
    """

    try:

        # ------------------------------------------
        # Final safety validation
        # ------------------------------------------

        if not is_booking_complete(booking):

            missing = get_missing_fields(booking)

            return {
                "success": False,
                "booking_id": None,
                "error": (
                    "Cannot save booking. Missing fields: "
                    + ", ".join(missing)
                )
            }

        if not is_valid_email(booking["email"]):

            return {
                "success": False,
                "booking_id": None,
                "error": "Invalid email address."
            }

        if not is_valid_phone(booking["phone"]):

            return {
                "success": False,
                "booking_id": None,
                "error": "Invalid phone number."
            }

        if not is_valid_date(booking["date"]):

            return {
                "success": False,
                "booking_id": None,
                "error": "Invalid booking date."
            }

        if not is_valid_time(booking["time"]):

            return {
                "success": False,
                "booking_id": None,
                "error": "Invalid booking time."
            }


        # ------------------------------------------
        # Save customer
        # ------------------------------------------

        customer_id = add_customer(
            name=booking["name"],
            email=booking["email"],
            phone=booking["phone"]
        )


        # ------------------------------------------
        # Save booking
        # ------------------------------------------

        booking_id = add_booking(
            customer_id=customer_id,
            booking_type=booking["booking_type"],
            booking_date=booking["date"],
            booking_time=booking["time"],
            status="confirmed"
        )


        return {
            "success": True,
            "booking_id": booking_id,
            "error": None
        }


    except Exception as e:

        return {
            "success": False,
            "booking_id": None,
            "error": str(e)
        }


# --------------------------------------------------
# RESET BOOKING
# --------------------------------------------------

def reset_booking(booking):
    """
    Reset all booking fields to empty values.
    """

    for field in BOOKING_FIELDS:

        booking[field] = None

    return booking
