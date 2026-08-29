import streamlit as st
import pandas as pd

from utils.database import get_all_bookings


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Glow Salon Admin Dashboard",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.title("📊 Glow Salon Admin Dashboard")

st.caption(
    "View and manage salon bookings and customer information."
)


# --------------------------------------------------
# LOAD BOOKINGS
# --------------------------------------------------

try:

    bookings = get_all_bookings()

    columns = [
        "booking_id",
        "name",
        "email",
        "phone",
        "service",
        "date",
        "time",
        "status",
        "created_at"
    ]

    bookings_df = pd.DataFrame(
        bookings,
        columns=columns
    )

except Exception as e:

    st.error(
        "Could not load bookings from the database."
    )

    st.exception(e)

    st.stop()


# --------------------------------------------------
# STATISTICS
# --------------------------------------------------

total_bookings = len(bookings_df)

confirmed_bookings = len(
    bookings_df[
        bookings_df["status"] == "confirmed"
    ]
)


st.subheader("Booking Overview")


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Total Bookings",
        total_bookings
    )


with col2:

    st.metric(
        "Confirmed Bookings",
        confirmed_bookings
    )


st.divider()


# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.subheader("🔎 Search and Filter")


filter_col1, filter_col2, filter_col3 = st.columns(3)


with filter_col1:

    search_text = st.text_input(
        "Search customer",
        placeholder="Name or email..."
    )


with filter_col2:

    if bookings_df.empty:

        status_options = ["All"]

    else:

        status_options = [
            "All"
        ] + sorted(
            bookings_df["status"].dropna().unique().tolist()
        )

    selected_status = st.selectbox(
        "Status",
        status_options
    )


with filter_col3:

    if bookings_df.empty:

        service_options = ["All"]

    else:

        service_options = [
            "All"
        ] + sorted(
            bookings_df["service"].dropna().unique().tolist()
        )

    selected_service = st.selectbox(
        "Service",
        service_options
    )


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_bookings = bookings_df.copy()


if search_text:

    search_text = search_text.lower().strip()

    filtered_bookings = filtered_bookings[
        filtered_bookings["name"]
        .fillna("")
        .str.lower()
        .str.contains(
            search_text,
            regex=False
        )
        |
        filtered_bookings["email"]
        .fillna("")
        .str.lower()
        .str.contains(
            search_text,
            regex=False
        )
    ]


if selected_status != "All":

    filtered_bookings = filtered_bookings[
        filtered_bookings["status"]
        == selected_status
    ]


if selected_service != "All":

    filtered_bookings = filtered_bookings[
        filtered_bookings["service"]
        == selected_service
    ]


# --------------------------------------------------
# BOOKINGS TABLE
# --------------------------------------------------

st.subheader("📋 All Bookings")


if filtered_bookings.empty:

    if bookings_df.empty:

        st.info(
            "No bookings found."
        )

    else:

        st.info(
            "No bookings match the selected filters."
        )

else:

    st.dataframe(
        filtered_bookings,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Showing {len(filtered_bookings)} "
        f"of {len(bookings_df)} bookings."
    )
