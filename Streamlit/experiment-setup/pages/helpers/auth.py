import streamlit as st
from google.oauth2 import service_account
import requests
import json
import os
from google.auth.transport.requests import Request

# File paths for the service account key and backend URL configuration
SERVICE_ACCOUNT_FILE = 'pages/helpers/secrets/key.json'
BACKEND_URL_FILE = 'pages/helpers/secrets/backend.json'

# Load the backend URL from a configuration file
with open(BACKEND_URL_FILE) as jsonFile:
    BACKEND_URL = json.load(jsonFile)["BACKEND_URL"]

# Function to retrieve the backend URL
def get_backendURL():
    """
    Returns the backend URL loaded from the configuration file.
    """
    return BACKEND_URL

# Function to retrieve the OpenAI API key
def get_openai_key(keyFile_path):
    """
    Retrieves the OpenAI API key from a specified JSON file.

    Args:
        keyFile_path (str): Path to the JSON file containing the OpenAI API key.

    Returns:
        str: The OpenAI API key.
    """
    with open(keyFile_path) as key:        
        credentials = json.load(key)
        return credentials["api_key"]

# Function to obtain an ID token for authentication
def get_auth_idtoken():
    """
    Generates an ID token using the service account credentials for authentication.

    Returns:
        str: A valid ID token for the service account.
    """
    # Load the service account credentials
    credentials = service_account.IDTokenCredentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        target_audience=get_backendURL()
    )
    # Refresh the token to get a valid ID token
    request = Request()
    credentials.refresh(request)
    id_token = credentials.token
    return id_token

# Function to check user credentials against the backend
def check_credentials(email, password):
    """
    Checks if the provided email and password are valid.

    Args:
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        str: "true" if the credentials are valid, otherwise "false".
    """
    if email and password:
        if "@" in email:
            req = requests.get(
                url=f"{get_backendURL()}/users", 
                params={"email": email, "password": password}, 
                headers={"Authorization": f"Bearer {get_auth_idtoken()}"}
            )
            st.write("Upload Request Submitted to API:", req)
            return req.text
    return "false"

# Function to sign up a new user
def signup(email, password):
    """
    Signs up a new user with the provided email and password.

    Args:
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        str: "true" if the signup is successful, otherwise "false".
    """
    if email and password:
        if "@" in email:
            req = requests.post(
                url=f"{get_backendURL()}/users", 
                params={"email": email, "password": password}, 
                headers={"Authorization": f"Bearer {get_auth_idtoken()}"}
            )
            st.write("Upload Request Submitted to API:", req)
            return req.text
    return "false"

# Function to handle user login
def login():
    """
    Handles the user login process. Prompts for email and password, checks credentials,
    and sets the session state based on the login outcome.
    """
    st.session_state.logged_in = False
    with st.form("Login"):
        st.write("Please login")
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        st1, st2 = st.columns(2, gap="small")
        with st1:
            login_button = st.form_submit_button("Login")
        with st2:
            signup_button = st.form_submit_button("Sign Up")
        
        if login_button:
            req = check_credentials(username, password)
            if req == "true":        
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun()  # Redirect to reload the page after login
            else:
                st.error("Invalid username or password")

        if signup_button:
            req = signup(username, password)
            if req == "true":    
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun()  # Redirect to reload the page after signup
            else:
                st.error("User already exists. Please log in.")

# Function to handle user logout
def logout():
    """
    Handles the user logout process by resetting session state variables.
    """
    st.session_state.logged_in = False
    st.session_state.username = ""
