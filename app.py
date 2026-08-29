import streamlit as st

from models.llm import generate_response

from utils.rag import (
    extract_text_from_pdf,
    split_text,
    create_vector_store,
    generate_rag_answer
)

from utils.booking import (
    create_empty_booking,
    extract_booking_details,
    get_missing_fields,
    is_valid_email,
    is_valid_phone,
    is_valid_date,
    is_valid_time,
    create_booking_summary,
    booking_persistence_tool
)

from utils.email import send_booking_confirmation


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Glow Salon AI Assistant",
    page_icon="💇",
    layout="centered"
)


st.title("💇 Glow Salon AI Assistant")

st.caption(
    "Ask about services, prices, opening hours, or make a booking."
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


if "booking" not in st.session_state:

    st.session_state.booking = create_empty_booking()


if "booking_active" not in st.session_state:

    st.session_state.booking_active = False


if "awaiting_confirmation" not in st.session_state:

    st.session_state.awaiting_confirmation = False


if "vector_index" not in st.session_state:

    st.session_state.vector_index = None


if "document_chunks" not in st.session_state:

    st.session_state.document_chunks = []


if "pdf_processed" not in st.session_state:

    st.session_state.pdf_processed = False


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("📄 Salon Knowledge Base")

    uploaded_file = st.file_uploader(
        "Upload salon information PDF",
        type=["pdf"]
    )


    if uploaded_file is not None:

        if st.button("Process PDF"):

            try:

                with st.spinner(
                    "Processing PDF..."
                ):

                    text = extract_text_from_pdf(
                        uploaded_file
                    )

                    if not text.strip():

                        st.error(
                            "The PDF does not contain readable text."
                        )

                    else:

                        chunks = split_text(text)

                        index, chunks = create_vector_store(
                            chunks
                        )

                        st.session_state.vector_index = index

                        st.session_state.document_chunks = chunks

                        st.session_state.pdf_processed = True

                        st.success(
                            "✅ PDF processed!"
                        )

                        st.write(
                            f"Chunks created: {len(chunks)}"
                        )

            except Exception as e:

                st.error(
                    "Could not process the PDF."
                )

                st.exception(e)


    st.divider()

    st.header("📊 Status")


    if st.session_state.pdf_processed:

        st.success(
            "RAG knowledge base ready"
        )

    else:

        st.warning(
            "Upload and process a PDF"
        )

    st.divider()

    st.header("💡 How to use")

    st.markdown(
        """
        **Ask questions**

        Try:
        - What services do you offer?
        - What are your opening hours?
        - How much is a haircut?

        **Make a booking**

        Say:
        - I want to book a haircut.

        I will ask only for the details
        that are still missing.
        """
    )


# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

if not st.session_state.messages:

    st.info(
        "👋 Welcome to Glow Salon! "
        "Ask me about our services or start a booking."
    )


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def add_message(role, content):

    st.session_state.messages.append(
        {
            "role": role,
            "content": content
        }
    )

    # Keep only the latest 25 messages
    st.session_state.messages = (
        st.session_state.messages[-25:]
    )


def get_conversation_context():

    recent_messages = (
        st.session_state.messages[-25:]
    )

    context = ""

    for message in recent_messages:

        context += (
            f'{message["role"]}: '
            f'{message["content"]}\n'
        )

    return context


# --------------------------------------------------
# BOOKING FIELD UPDATE
# --------------------------------------------------

def update_booking_from_extraction(extracted):
    """
    Update only valid, useful booking values.

    Invalid email/phone/date/time values are not stored, so
    the assistant will continue asking for that field.
    """

    booking = st.session_state.booking

    # Name
    name = extracted.get("name")
    if name and isinstance(name, str) and name.strip():
        booking["name"] = name.strip()

    # Email
    email = extracted.get("email")
    if email and isinstance(email, str):
        email = email.strip()
        if is_valid_email(email):
            booking["email"] = email

    # Phone
    phone = extracted.get("phone")
    if phone and is_valid_phone(phone):
        booking["phone"] = str(phone).strip()

    # Service
    booking_type = extracted.get("booking_type")
    if booking_type and isinstance(booking_type, str):
        booking["booking_type"] = booking_type.strip()

    # Date
    date = extracted.get("date")
    if date and isinstance(date, str):
        date = date.strip()
        if is_valid_date(date):
            booking["date"] = date

    # Time
    time = extracted.get("time")
    if time and isinstance(time, str):
        time = time.strip()
        if is_valid_time(time):
            booking["time"] = time

    st.session_state.booking = booking



# --------------------------------------------------
# VALIDATE BOOKING
# --------------------------------------------------

def validate_booking():

    booking = st.session_state.booking

    errors = []


    if not booking["name"]:

        errors.append(
            "I still need your name."
        )


    if not is_valid_email(
        booking["email"]
    ):

        errors.append(
            "Please provide a valid email address."
        )


    if not is_valid_phone(
        booking["phone"]
    ):

        errors.append(
            "Please provide a valid phone number."
        )


    if not is_valid_date(
        booking["date"]
    ):

        errors.append(
            "Please enter the date as YYYY-MM-DD."
        )


    if not is_valid_time(
        booking["time"]
    ):

        errors.append(
            "Please enter the time as HH:MM."
        )


    return errors


# --------------------------------------------------
# DETERMINE NEXT QUESTION
# --------------------------------------------------

def get_next_booking_question():

    booking = st.session_state.booking

    if not booking["name"]:

        return "Sure! May I know your name?"


    if not booking["email"]:

        return "What's your email address?"


    if not booking["phone"]:

        return "What's your phone number?"


    if not booking["booking_type"]:

        return (
            "Which service would you like to book? "
            "For example: Haircut, Facial, Hair Spa, "
            "Manicure, or Hair Coloring."
        )


    if not booking["date"]:

        return (
            "What date would you prefer? "
            "Please use YYYY-MM-DD."
        )


    if not booking["time"]:

        return (
            "What time would you prefer? "
            "Please use HH:MM."
        )


    return None


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

user_input = st.chat_input(
    "Type your message..."
)

if user_input is not None:
    user_input = user_input.strip()

if user_input:

    # ----------------------------------------------
    # Display user message
    # ----------------------------------------------

    add_message(
        "user",
        user_input
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # ----------------------------------------------
    # 1. CONFIRMATION STATE
    # ----------------------------------------------

    if st.session_state.awaiting_confirmation:

        lower_input = user_input.lower().strip()

        if lower_input in [
            "yes",
            "y",
            "confirm",
            "confirmed",
            "yes please"
        ]:

            # Final validation before database insertion
            errors = validate_booking()

            if errors:

                response = "\n\n".join(errors)

            else:

                result = booking_persistence_tool(
                    st.session_state.booking
                )

                if result["success"]:

                    booking_id = result["booking_id"]

                    response = (
                        "✅ Your booking has been confirmed!\n\n"
                        f"**Booking ID:** #{booking_id}\n\n"
                        f"**Name:** {st.session_state.booking['name']}\n"
                        f"**Service:** {st.session_state.booking['booking_type']}\n"
                        f"**Date:** {st.session_state.booking['date']}\n"
                        f"**Time:** {st.session_state.booking['time']}"
                    )

                    # Send email confirmation after successful database save.
                    email_result = send_booking_confirmation(
                        customer_email=st.session_state.booking["email"],
                        booking_id=booking_id,
                        name=st.session_state.booking["name"],
                        service=st.session_state.booking["booking_type"],
                        date=st.session_state.booking["date"],
                        time=st.session_state.booking["time"]
                    )

                    if email_result["success"]:
                        response += "\n\n📧 A confirmation email has been sent."
                    else:
                        response += (
                            "\n\n⚠️ Booking was saved successfully, "
                            "but the confirmation email could not be sent."
                        )
                        print(
                            f"Email confirmation failed: "
                            f"{email_result['error']}"
                        )

                    # Reset booking state after successful save
                    st.session_state.booking = (
                        create_empty_booking()
                    )

                    st.session_state.booking_active = False
                    st.session_state.awaiting_confirmation = False

                else:

                    response = (
                        "❌ I couldn't save your booking.\n\n"
                        f"Database error: {result['error']}"
                    )

        elif lower_input in [
            "no",
            "n",
            "cancel"
        ]:

            st.session_state.booking = (
                create_empty_booking()
            )

            st.session_state.booking_active = False
            st.session_state.awaiting_confirmation = False

            response = (
                "No problem. I cancelled "
                "the booking request."
            )

        else:

            response = (
                "Please reply with **yes** "
                "to confirm or **no** to cancel."
            )

    # ----------------------------------------------
    # 2. ACTIVE BOOKING STATE
    # ----------------------------------------------

    elif st.session_state.booking_active:

        extracted = extract_booking_details(
            user_input
        )

        update_booking_from_extraction(
            extracted
        )

        missing = get_missing_fields(
            st.session_state.booking
        )

        if missing:

            response = get_next_booking_question()

        else:

            errors = validate_booking()

            if errors:

                response = "\n\n".join(errors)

            else:

                response = create_booking_summary(
                    st.session_state.booking
                )

                # All details collected.
                # Wait for explicit YES before saving.
                st.session_state.booking_active = False
                st.session_state.awaiting_confirmation = True

    # ----------------------------------------------
    # 3. NORMAL MESSAGE / NEW BOOKING
    # ----------------------------------------------

    else:

        extracted = extract_booking_details(
            user_input
        )

        if extracted.get("is_booking", False):

            # Always start a completely fresh booking
            st.session_state.booking = (
                create_empty_booking()
            )

            st.session_state.booking_active = True
            st.session_state.awaiting_confirmation = False

            update_booking_from_extraction(
                extracted
            )

            missing = get_missing_fields(
                st.session_state.booking
            )

            if missing:

                response = get_next_booking_question()

            else:

                errors = validate_booking()

                if errors:

                    response = "\n\n".join(errors)

                else:

                    response = create_booking_summary(
                        st.session_state.booking
                    )

                    st.session_state.booking_active = False
                    st.session_state.awaiting_confirmation = True

        else:

            # --------------------------------------
            # NORMAL RAG QUESTION
            # --------------------------------------

            if (
                st.session_state.vector_index
                is None
            ):

                response = (
                    "Please upload and process "
                    "the salon PDF first so I can "
                    "answer questions about the salon."
                )

            else:

                response = generate_rag_answer(
                    query=user_input,
                    index=st.session_state.vector_index,
                    chunks=st.session_state.document_chunks,
                    generate_response=generate_response
                )

    # ----------------------------------------------
    # Display assistant response
    # ----------------------------------------------

    add_message(
        "assistant",
        response
    )

    with st.chat_message("assistant"):

        st.markdown(response)
