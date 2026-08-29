Glow Salon AI Booking Assistant

A Streamlit-based AI assistant for Glow Salon.

The application can answer salon questions from a PDF and help customers make bookings.

MAIN FEATURES

PDF-based RAG
Gemini LLM
Gemini embeddings
FAISS vector search
Conversational booking
Short-term chat memory
Booking details collection
Booking validation
Booking summary
YES/NO confirmation
SQLite database
Booking ID generation
Gmail confirmation email
Admin dashboard
Search and filters


TECHNOLOGIES USED

Python
Streamlit
Google GenAI
FAISS
NumPy
Pandas
pypdf
SQLite
Gmail SMTP


PROJECT STRUCTURE

AI_UseCase

config
    __init__.py
    config.py

models
    __init__.py
    embeddings.py
    llm.py

utils
    __init__.py
    database.py
    rag.py
    booking.py
    email.py

docs
    salon_info.pdf

app.py
admin_dashboard.py
requirements.txt
README.md
.gitignore
bookings.db


HOW RAG WORKS

The salon PDF is processed using the following process:

PDF
Text Extraction
Text Chunking
Gemini Embeddings
FAISS Vector Store
Similarity Search
Relevant Information
Gemini
Final Answer

The assistant uses information retrieved from the salon PDF to answer salon-related questions.


BOOKING FLOW

Normal Chat
Booking Request
Collect Missing Details
Validate Details
Show Booking Summary
Ask for YES or NO

If the user says YES:
The booking is saved to SQLite.
A booking ID is generated.
A confirmation email is sent.

If the user says NO:
The booking is cancelled.


REQUIRED BOOKING DETAILS

Name
Email
Phone
Service
Date
Time


SHORT-TERM MEMORY

The application stores recent chat messages using Streamlit session state.

The latest 25 messages are retained as short-term conversation context.


DATABASE

SQLite is used for storing customer and booking information.

Customers table stores:

Customer ID
Name
Email
Phone

Bookings table stores:

Booking ID
Customer ID
Service
Date
Time
Status
Created time

The database file is bookings.db.


EMAIL CONFIRMATION

After a successful booking, the application sends a confirmation email using Gmail SMTP.

The email contains:

Customer name
Booking ID
Service
Date
Time

A Gmail App Password is used instead of the normal Gmail password.


ADMIN DASHBOARD

The admin dashboard is available in admin_dashboard.py.

It provides:

Total bookings
Confirmed bookings
Customer information
Booking information
Search by customer name or email
Status filter
Service filter


INSTALLATION

Activate the virtual environment:

source venv/bin/activate

Install the required packages:

pip install -r requirements.txt


CONFIGURATION

Create the following file:

.streamlit/secrets.toml

Add the required Gemini and Gmail settings:

GEMINI_API_KEY = "your_gemini_api_key"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your_gmail@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"

Never share or commit these credentials.


RUN THE CUSTOMER APPLICATION

Run:

streamlit run app.py


RUN THE ADMIN DASHBOARD

Run:

streamlit run admin_dashboard.py


EXAMPLE RAG QUESTIONS

What services do you offer?

How much is a haircut?

What are your opening hours?

What is the cancellation policy?


EXAMPLE BOOKING

User: I want a haircut.

Assistant: Sure! May I know your name?

User: Rahul

Assistant: What's your email address?

User: rahul@gmail.com

Assistant: What's your phone number?

User: 8477737383

Assistant: Which service would you like to book?

User: Haircut

Assistant: What date would you prefer?

User: 2026-08-30

Assistant: What time would you prefer?

User: 17:00

The assistant displays the booking summary and asks for confirmation.

User: yes

The booking is saved to SQLite, a booking ID is generated, and a confirmation email is sent.


ERROR HANDLING

The application handles:

PDF processing errors
Empty PDF text
Gemini failures
Missing booking details
Invalid booking details
Database errors
Email errors
Empty RAG queries


PURPOSE

This project demonstrates how an AI assistant can combine a large language model, RAG, FAISS, conversational memory, a database, and email to create a practical AI-powered salon booking system.
