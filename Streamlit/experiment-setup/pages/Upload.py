import streamlit as st
import pandas as pd
import numpy as np
import requests
import pages.helpers.auth as auth

# Initialize session state for login and username
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # Track if the user is logged in
if 'username' not in st.session_state:
    st.session_state.username = ""  # Store the logged-in user's username

# Define the location of the service account file and backend URL
SERVICE_ACCOUNT_FILE = 'pages/helpers/secrets/key.json'
backend_url = auth.get_backendURL()  # Get the backend URL from the auth module

def submitCustomers(**kwargs):
    """
    Submits customer data to the backend API.

    Args:
        **kwargs: Arbitrary keyword arguments containing the customer data to be submitted.

    Returns:
        Response object from the API indicating the success or failure of the submission.
    """
    st.session_state.customers = None  # Clear any existing customer data in session state
    if kwargs.get("rawData"):
        req = requests.post(
            url=f"{backend_url}/customers", 
            json=kwargs, 
            headers={"Authorization": f"Bearer {auth.get_auth_idtoken()}"}
        )
        st.write("Upload Request Submitted to API:", req)  # Display the API response in the app
        return req  # Return the API response

def submitVariables(**kwargs):
    """
    Submits variable data to the backend API.

    Args:
        **kwargs: Arbitrary keyword arguments containing the variable data to be submitted.

    Returns:
        Response object from the API indicating the success or failure of the submission.
    """
    st.session_state.variables = None  # Clear any existing variable data in session state
    req = requests.post(
        url=f"{backend_url}/variables", 
        json=kwargs, 
        headers={"Authorization": f"Bearer {auth.get_auth_idtoken()}"}
    )
    st.write("Upload Request Submitted to API:", req)  # Display the API response in the app
    return req  # Return the API response

# Set the page title and icon for Streamlit
st.set_page_config(page_title="File Uploader", page_icon="📈")

# Initialize session state for customers and variables if not present
if 'customers' not in st.session_state:
    st.session_state.customers = None
if 'variables' not in st.session_state:
    st.session_state.variables = None

# Display login or main content based on login status
if not st.session_state.logged_in:
    auth.login()  # Display the login form if the user is not logged in
else:
    st.sidebar.write(f"Logged in: {st.session_state.username}")  # Display the logged-in user's username
    st.sidebar.button("Logout", on_click=auth.logout)  # Provide a logout button in the sidebar
    
    # Section for uploading customer data
    st.title("Upload Customers")
    with st.form("Upload_Customers"):
        platform = st.selectbox(
            "Which platform are you sending messages to?",
            ("LinkedIn", "Email", "Phone")
        )
        title = st.text_input(
            "What is the role that are you targeting?",
        )
        country = st.selectbox(
            "What country is this for?",
            ("United States", "Mexico")
        )
        
        params = {"Platform": platform, "Title": title, "Country": country}  # Collect input parameters
        
        uploaded_file = st.file_uploader(label="Upload your customers:")  # File uploader for customer data
        if uploaded_file:
            uploaded_df = pd.read_csv(uploaded_file).replace({np.nan: None})  # Read the uploaded CSV file
            if 'Unnamed: 0' in uploaded_df.columns:
                uploaded_df = uploaded_df.drop('Unnamed: 0', axis=1)  # Remove any unnamed index columns
            st.session_state.customers = uploaded_df  # Store the uploaded data in session state
            st.write(st.session_state.customers.head(5))  # Display the first 5 rows of the uploaded data
            params.update({"rawData": st.session_state.customers.to_dict()})  # Add the customer data to parameters
            
        # Submit button for uploading customer data
        submitted = st.form_submit_button(label="Submit", on_click=submitCustomers, kwargs=params)
    
    # Section for uploading variable data
    st.title("Upload Variables")
    with st.form("Upload Variables"):
        platform = st.selectbox(
            "Which platform are you sending messages to?",
            ("LinkedIn", "Email", "Phone")
        )
        product = st.selectbox(
            "What product is this for?",
            ("FT-1", "SpiroScout", "DS-20")
        )
    
        params = {"Platform": platform, "Product": product, "OwnerEmail": st.session_state.username}  # Collect input parameters
        
        uploaded_file = st.file_uploader(label="Upload your variables:")  # File uploader for variable data
        if uploaded_file:
            uploaded_df = pd.read_csv(uploaded_file).replace({np.nan: None})  # Read the uploaded CSV file
            if 'Unnamed: 0' in uploaded_df.columns:
                uploaded_df = uploaded_df.drop('Unnamed: 0', axis=1)  # Remove any unnamed index columns
            st.session_state.variables = uploaded_df  # Store the uploaded data in session state
            st.write(st.session_state.variables.head(5))  # Display the first 5 rows of the uploaded data
            params.update({"rawData": st.session_state.variables.to_dict()})  # Add the variable data to parameters
    
        # Submit button for uploading variable data
        submitted = st.form_submit_button(label="Submit", on_click=submitVariables, kwargs=params)
