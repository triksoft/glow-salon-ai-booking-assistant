import smtplib
from email.message import EmailMessage

import streamlit as st


def send_booking_confirmation(
    customer_email,
    booking_id,
    name,
    service,
    date,
    time
):
    """
    Send a booking confirmation email to the customer.

    Returns:
        {
            "success": True/False,
            "error": None or error message
        }
    """

    try:

        # ------------------------------------------
        # Read email settings from Streamlit secrets
        # ------------------------------------------

        smtp_server = st.secrets["SMTP_SERVER"]
        smtp_port = int(st.secrets["SMTP_PORT"])

        sender_email = st.secrets["EMAIL_ADDRESS"]
        sender_password = st.secrets["EMAIL_PASSWORD"]


        # ------------------------------------------
        # Create email
        # ------------------------------------------

        message = EmailMessage()

        message["Subject"] = (
            f"Glow Salon Booking Confirmation #{booking_id}"
        )

        message["From"] = sender_email
        message["To"] = customer_email


        message.set_content(
            f"""
Hello {name},

Your booking at Glow Salon has been confirmed!

Booking ID: #{booking_id}
Service: {service}
Date: {date}
Time: {time}

We look forward to seeing you at Glow Salon.

Thank you,
Glow Salon
"""
        )


        # ------------------------------------------
        # Connect to SMTP server
        # ------------------------------------------

        with smtplib.SMTP(
            smtp_server,
            smtp_port
        ) as server:

            server.starttls()

            server.login(
                sender_email,
                sender_password
            )

            server.send_message(message)


        return {
            "success": True,
            "error": None
        }


    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }