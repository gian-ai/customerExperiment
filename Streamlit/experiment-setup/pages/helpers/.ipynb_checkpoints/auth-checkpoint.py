import streamlit as st
from google.oauth2 import service_account
import requests
import json
import os
from google.auth.transport.requests import Request


SERVICE_ACCOUNT_FILE = 'pages/helpers/secrets/key.json'
BACKEND_URL = 'https://backend-auth-vmazoy5ygq-uc.a.run.app'

def get_openai_key(keyFile_path):
    with open(keyFile_path) as key:        
        credentials = json.load(key)
        return credentials["api_key"]

def get_auth_idtoken():
    # Path to your service account key file    
    # Load the service account credentials
    credentials = service_account.IDTokenCredentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        target_audience=BACKEND_URL
    )
        # Refresh the token to get a valid ID token
    request = Request()
    credentials.refresh(request)
    id_token = credentials.token
    return id_token

# Function to check credentials
def check_credentials(email, password):
    if email and password:
        if "@" in email:
            req = requests.get(
                url=f"{BACKEND_URL}/users", 
                params={"email":email, "password":password}, 
                headers={"Authorization": f"Bearer {get_auth_idtoken()}"}
            )
            st.write("Upload Request Submitted to API:", req)
            return req.text
    return "false"

def signup(email, password):
    if email and password:
        if "@" in email:
            req = requests.post(
                url=f"{BACKEND_URL}/users", 
                params={"email":email, "password":password}, 
                headers={"Authorization": f"Bearer {get_auth_idtoken()}"}
            )
            st.write("Upload Request Submitted to API:", req)
            return req.text
    return "false"
    

# Function to handle login
def login():
    st.session_state.logged_in = False
    with st.form("Login"):
        st.write("Please login")
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        st1, st2 =  st.columns(2, gap="small")
        with st1:
            login_button = st.form_submit_button("Login")
        with st2:
            signup_button = st.form_submit_button("Sign Up")
        
        if login_button:
            req = check_credentials(username, password)
            
            if req=="true":        
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun() #redirect
            else:
                st.error("Invalid username or password")

        if signup_button:
            req= signup(username,password)
            if req == "true":    
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun() #redirect
            else:
                st.error("User already exists. Please log in.")


# Function to handle logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
