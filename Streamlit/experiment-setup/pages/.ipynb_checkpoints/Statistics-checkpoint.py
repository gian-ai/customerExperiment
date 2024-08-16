import streamlit as st
import pandas as pd
import requests
import pages.helpers.auth as auth
import numpy as np

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

backend_url = "https://backend-auth-vmazoy5ygq-uc.a.run.app"
SERVICE_ACCOUNT_FILE = 'pages/helpers/secrets/key.json'

st.set_page_config(page_title="Statistics", page_icon="📈")

def viewRaw(collection:str):
    token = auth.get_auth_idtoken()
    url = f"{backend_url}/statistics"
    payload = {"collection": collection}
    headers = {"Authorization": f"Bearer {token}"}
    
    req = requests.get(url=url, params=payload, headers=headers)
    # st.write(req.text)
    return pd.DataFrame(req.json()[collection])

# Display login or main content based on login status
if not st.session_state.logged_in:
    auth.login()
else:
    st.sidebar.write(f"Logged in: {st.session_state.username}")
    st.sidebar.button("Logout", on_click=auth.logout)
    
    collection = st.selectbox(
        "Choose which collection to extract:",
        options=["events", "customers", "experiments"]
    )
    
    if st.button("Get Statistics"):
        st.write(viewRaw(collection).replace(np.nan,None))
    

