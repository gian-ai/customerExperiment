import streamlit as st
import pandas as pd
import numpy as np
import requests
import pages.helpers.auth as auth

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

SERVICE_ACCOUNT_FILE = 'pages/helpers/secrets/key.json'
backend_url = "https://backend-auth-vmazoy5ygq-uc.a.run.app"


def submitCustomers(**kwargs):
    st.session_state.customers = None
    req = requests.post(
        url=f"{backend_url}/customers", 
        json=kwargs, 
        headers={"Authorization": f"Bearer {auth.get_auth_idtoken()}"}
    )
    st.write("Upload Request Submitted to API:", req)
    return req

def submitVariables(**kwargs):
    st.session_state.variables = None
    req = requests.post(url=f"{backend_url}/variables", json=kwargs, headers={"Authorization": f"Bearer {auth.get_auth_idtoken()}"})
    st.write("Upload Request Submitted to API:", req)
    return req

st.set_page_config(page_title="File Uploader", page_icon="📈")

# Initialize session state if not present
if 'customers' not in st.session_state:
    st.session_state.customers = None
if 'variables' not in st.session_state:
    st.session_state.variables = None

# Display login or main content based on login status
if not st.session_state.logged_in:
    auth.login()
else:
    st.sidebar.write(f"Logged in: {st.session_state.username}")
    st.sidebar.button("Logout", on_click=auth.logout)
    
    st.title("Upload Customers")
    with st.form("Upload_Customers"):
        platform = st.selectbox(
            "Which platform are you sending messages to?",
            ("LinkedIn", "Email", "Phone")
        )
        title = st.selectbox(
            "What is the target profile that are you targeting?",
            ("Cardiologist", "Pulmonologist", "Internal Medicine", "Office Manager")
        )
        country = st.selectbox(
            "What country is this for?",
            ("United States", "Mexico")
        )
        
        params = {"Platform": platform, "Title": title, "Country": country}
        
        uploaded_file = st.file_uploader(label="Upload your customers:")
        if uploaded_file:
            uploaded_df = pd.read_csv(uploaded_file).replace({np.nan: None})
            if 'Unnamed: 0' in uploaded_df.columns:
                uploaded_df = uploaded_df.drop('Unnamed: 0', axis=1)
            st.session_state.customers = uploaded_df
            st.write(st.session_state.customers.head(5))
            params.update({"rawData": st.session_state.customers.to_dict()})
            
        submitted = st.form_submit_button(label="Submit", on_click=submitCustomers, kwargs=params)
    
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
    
        params = {"Platform": platform, "Product": product, "OwnerEmail": st.session_state.username}
        
        uploaded_file = st.file_uploader(label="Upload your variables:")
        if uploaded_file:
            uploaded_df = pd.read_csv(uploaded_file).replace({np.nan: None})
            if 'Unnamed: 0' in uploaded_df.columns:
                uploaded_df = uploaded_df.drop('Unnamed: 0', axis=1)
            st.session_state.variables = uploaded_df
            st.write(st.session_state.variables.head(5))
            params.update({"rawData": st.session_state.variables.to_dict()})
    
        submitted = st.form_submit_button(label="Submit", on_click=submitVariables, kwargs=params)