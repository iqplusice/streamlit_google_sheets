import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Vendor Management Portal")
st.markdown("Enter the details of the new vendor below:")

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="Vendors", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how='all')

# List of Business Types and Products
BUSINESS_TYPES = [
    "Manufacturer",
    "Distributor",
    "Wholesaler",
    "Retailer",
    "Service Provider",
    "Consultant",
]

PRODUCTS = [
    "Electronics",
    "Apparel",
    "Groceries",
    "Software",
    "Hardware",
    "Other",
]

# Onboarding New Vendor Form
with st.form(key="vendor_form"):
    company_name = st.text_input(label="Company Name*")
    business_type = st.selectbox(label="Business Type*", options=BUSINESS_TYPES, index=None)
    products = st.multiselect(label="Products Offered", options=PRODUCTS, default=None)
    years_in_business = st.slider(label="Years in Business", min_value=0, max_value=50, value=5)
    onboarding_date = st.date_input(label="Onboarding Date", value=pd.to_datetime("today"))
    additional_info = st.text_area(label="Additional Notes")

    # Mark mandatory fields
    st.markdown("**required*")

    submit_button = st.form_submit_button(label="Submit Vendor Details")

    # If the submit button is pressed
    if submit_button:
        # Check if all mandatory fields are filled
        if not company_name or not business_type:
            st.warning("Ensure all mandatory fields are filled")
            st.stop()
        elif existing_data['CompanyName'].str.contains(company_name).any():
            st.warning(f"A Vendor with '{company_name}' already exists.")
            st.stop()
        else:
            # Create a new row of vendor data
            vendor_data = pd.DataFrame(
                [
                    {
                        "CompanyName": company_name,
                        "BusinessType": business_type,
                        "Products": ", ".join(products) if products else None,
                        "YearsInBusiness": years_in_business,
                        "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                        "AdditionalInfo": additional_info,
                    }
                ]
            )

            # Add the new vendor data to the existing data
            updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)

            # Update Google Sheets with the new vendor data
            conn.update(worksheet="Vendors", data=updated_df)

            st.success(f"Vendor '{company_name}' has been successfully submitted!")