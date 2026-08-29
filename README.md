Pasted code(1).py
Python
RuntimeError: Both Gemini models are temporarily unavailable. Please try again in a moment.

File "/Users/vedanth/Downloads/AI Engineer Use Case/AI Engineer Use Case/AI_UseCase/venv/lib/python3.14/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
File "/Users/vedanth/Downloads/AI Engineer Use Case/AI Engineer Use Case/AI_UseCase/venv/lib/python3.14/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 837, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^
File "/Users/vedanth/Downloads/AI Engineer Use Case/AI Engineer Use Case/AI_UseCase/app.py", line 463, in <module>
    extracted = extract_booking_details(
        user_input
    )
File "/Users/vedanth/Downloads/AI Engineer Use Case/AI Engineer Use Case/AI_UseCase/utils/booking.py", line 227, in extract_booking_details
    response = generate_response(prompt)
File "/Users/vedanth/Downloads/AI Engineer Use Case/AI Engineer Use Case/AI_UseCase/models/llm.py", line 65, in generate_response
    raise RuntimeError(
    ...<2 lines>...
    ) from fallback_error
NOW what should we do next 
Pasted code(2).py
Python

Perfect. ✅ If you see the expected project files, the structure is ready.

STEP 31 — Check the README

Now we're at the documentation stage.

Open:

AI_UseCase/README.md

Since this is your final assignment, I want to replace the README with a proper one that explains:

Project overview
Features
Architecture
RAG pipeline
Booking workflow
Gemini usage
FAISS
SQLite
Email confirmation
Admin dashboard
Installation
How to run the application
How to run the admin dashboard
Project structure
Example booking flow

Don't edit it yet.

Send me the current contents of README.md here. If it's empty, just tell me "empty".

empty

Perfect. Since your README.md is empty, I created a complete project README based on the functionality we've actually built and tested.

Download the completed README.md

It covers:

Project overview
Features
Full architecture
RAG pipeline
Booking state flow
Short-term memory
Gemini + FAISS
SQLite database
Gmail confirmation
Admin dashboard
Project structure
Installation
Configuration
Running both applications
Example booking conversation
Example RAG questions
Error handling
Explanation of each Python module
STEP 31A — Replace README
Open:
AI_UseCase/README.md
Replace everything with the downloaded README_final.md.
Rename it to:
README.md
Save it.

Don't run anything yet.

Tell me once you've saved it. Then we'll do the final submission-readiness check before we prepare your demo/explanation. 

README_final.md
Document
make it simple because when we see the preview things collapse 

Yes — I agree. The previous README was too detailed for a project preview and made it feel cluttered.

I made a much simpler version with:

Short sections
No huge explanations
Simple architecture
Simple booking flow
Simple setup instructions
Simple project structure
Easy-to-read examples

Download the simpler README.md

STEP 31B

Replace your current:

AI_UseCase/README.md

with this version and save it.

Then don't run anything yet.

Tell me "done", and we'll move to the final project check. 

README_simple.md
Document

Library
/
README_simple.md
Glow Salon AI Booking Assistant

A Streamlit-based AI assistant for Glow Salon.

The application can answer salon questions from a PDF and help customers make bookings.

Main Features
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
Technologies Used
Python
Streamlit
Google GenAI
FAISS
NumPy
pandas
pypdf
SQLite
Gmail SMTP
Project Structure
AI_UseCase/
├── config/
│   ├── __init__.py
│   └── config.py
├── models/
│   ├── __init__.py
│   ├── embeddings.py
│   └── llm.py
├── utils/
│   ├── __init__.py
│   ├── database.py
│   ├── rag.py
│   ├── booking.py
│   └── email.py
├── docs/
│   └── salon_info.pdf
├── app.py
├── admin_dashboard.py
├── requirements.txt
├── README.md
├── .gitignore
└── bookings.db
How RAG Works

The salon PDF is processed like this:

PDF
↓
Text Extraction
↓
Text Chunking
↓
Gemini Embeddings
↓
FAISS Vector Store
↓
Similarity Search
↓
Relevant Information
↓
Gemini
↓
Answer

The assistant uses the retrieved PDF information to answer salon-related questions.

Booking Flow
Normal Chat
↓
Booking Request
↓
Collect Missing Details
↓
Validate Details
↓
Show Summary
↓
YES / NO
↓
YES → SQLite → Booking ID → Email
NO  → Cancel

The required booking details are:

Name
Email
Phone
Service
Date
Time

The booking is saved only after the user explicitly confirms with YES.

Short-Term Memory

The application stores recent chat messages using Streamlit session state.

The latest 25 messages are retained as short-term conversation context.

Database

SQLite is used for persistence.

Customers

Stores:

Customer ID
Name
Email
Phone
Bookings

Stores:

Booking ID
Customer ID
Service
Date
Time
Status
Created time

Database file:

bookings.db
Email Confirmation

After a successful booking, the application sends a confirmation email using Gmail SMTP.

The email contains:

Customer name
Booking ID
Service
Date
Time

A Gmail App Password is used instead of the normal Gmail password.

Admin Dashboard

Run:

streamlit run admin_dashboard.py

The dashboard shows:

Total bookings
Confirmed bookings
Customer information
Booking information
Search by name or email
Status filter
Service filter
Installation

Create and activate the virtual environment:

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt
Configuration

Create:

.streamlit/secrets.toml

Add:

GEMINI_API_KEY = "your_gemini_api_key"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your_gmail@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"

Do not share or commit these credentials.

Run the Customer App
streamlit run app.py
Example Questions

You can ask:

What services do you offer?
How much is a haircut?
What are your opening hours?
What is the cancellation policy?
Example Booking
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

The assistant then displays a summary and asks for confirmation.

User: yes

The booking is saved to SQLite, a booking ID is generated, and a confirmation email is sent.

Error Handling

The application handles:

PDF processing errors
Empty PDF text
Gemini failures
Missing booking details
Invalid booking details
Database errors
Email errors
Empty RAG queries
Purpose

This project demonstrates how an AI assistant can combine:

LLM + RAG + FAISS + conversational memory + database + email

to create a practical AI-powered salon booking system.