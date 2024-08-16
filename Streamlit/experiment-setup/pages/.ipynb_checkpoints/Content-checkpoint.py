import streamlit as st
import pandas as pd
import requests
import pages.helpers.contentGeneration as cg
import pages.helpers.auth as auth
from io import BytesIO
from openai import OpenAI
import numpy as np

backend_url = "https://backend-auth-vmazoy5ygq-uc.a.run.app"
# backend_url = "http://127.0.0.1:8000"


st.set_page_config(page_title="Content Generation", page_icon="📈")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

if 'pain_points' not in st.session_state:
    st.session_state.pain_points = []
if 'features' not in st.session_state:
    st.session_state.features = []
if 'call_to_actions' not in st.session_state:
    st.session_state.call_to_actions = []
if 'content' not in st.session_state:
    st.session_state.content = {}
if 'char_limit' not in st.session_state:
    st.session_state.char_limit = 500
if 'generated' not in st.session_state:
    st.session_state.generated = False
if "language" not in st.session_state:
    st.session_state.language = "English"
if "platform" not in st.session_state:
    st.session_state.platform = ""
if "ownerEmail" not in st.session_state:
    st.session_state.ownerEmail = ""
    
if "target_audience" not in st.session_state:
    st.session_state.target_audience = ""
if "target_industry" not in st.session_state:
    st.session_state.target_industry = ""


if 'temp_target_audience' not in st.session_state:
    st.session_state.temp_target_audience = ""
if 'temp_target_industry' not in st.session_state:
    st.session_state.temp_target_industry = ""

if 'temp_pain_point' not in st.session_state:
    st.session_state.temp_pain_point = ""
if 'temp_feature' not in st.session_state:
    st.session_state.temp_feature = ""

if 'temp_call_to_action' not in st.session_state:
    st.session_state.temp_call_to_action = ""
if 'temp_call_to_action_desc' not in st.session_state:
    st.session_state.temp_call_to_action_desc = ""
if 'selected_phases' not in st.session_state:
    st.session_state.selected_phases = []
if 'product_name' not in st.session_state:
    st.session_state.product_name = ""
if 'current_phase' not in st.session_state:
    st.session_state.current_phase = 0

if not st.session_state.logged_in:
    auth.login()
else:
    st.sidebar.write(f"Logged in: {st.session_state.username}")
    st.sidebar.button("Logout", on_click=auth.logout)

    st.title("Setup Product Information")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Enter the Name of the Product", key="temp_product_name")
        st.button("Save Product Name", on_click=cg.submit_product_name)
    
        if st.session_state.product_name:
            st.markdown(f"Selected Product: {st.session_state.product_name}")
    
    with col2:
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            st.text_input("Enter CTA Link", key="temp_call_to_action")
        with subcol2:
            st.text_input("Enter CTA Description", key="temp_call_to_action_desc")
        st.button("Save Call to Action Link", on_click=cg.add_call_to_action)
    
        if st.session_state.call_to_actions:
            for i, (link, desc) in enumerate(st.session_state.call_to_actions, start=1):
                st.markdown(f"{i}. [{desc}]({link})")
            st.button("Clear", on_click=cg.clear_call_to_actions, key="clear_cta")
    
    col3, col4 = st.columns(2)
    with col3:
        st.text_input("Enter the Name of the Audience", key="temp_target_audience")
        st.button("Save Target Audience", on_click=cg.add_target_audience)
    
        if st.session_state.target_audience:
            st.markdown(f"Selected Audience: {st.session_state.target_audience}")
            
    with col4:
        st.text_input("Enter the Name of the Industry", key="temp_target_industry")
        st.button("Save Target Industry", on_click=cg.add_target_industry)
    
        if st.session_state.target_industry:
            st.markdown(f"Selected Industry: {st.session_state.target_industry}")
    
    col5, col6 = st.columns(2)
    with col5:
        st.text_input("Enter Pain Points for Target Audience", key="temp_pain_point")
        st.button("Save Pain Point", on_click=cg.add_pain_point)
        if st.session_state.pain_points:
            for i, pain_point in enumerate(st.session_state.pain_points, start=1):
                st.markdown(f"{i}. {pain_point}")
            
            st.button("Clear", on_click=cg.clear_pain_points, key="clear_pain_points")
    
    with col6:
        st.text_input("Enter Features for Product", key="temp_feature")
        st.button("Save Feature", on_click=cg.add_feature)
        if st.session_state.features:
            for i, feature in enumerate(st.session_state.features, start=1):
                st.markdown(f"{i}. {feature}")
                
            st.button("Clear", on_click=cg.clear_features, key="clear_features")
    
    st.markdown("---")
    
    st.title("Setup Message Sequence")
    
    col7, col8 = st.columns(2)
    with col7:      
        platform = st.selectbox("Platform", options=["LinkedIn", "Email", "Phone"])
        st.session_state.platform = platform
        
        language = st.selectbox("Language", options=["English", "Spanish"])
        st.session_state.language = language
    
        selected_phases = st.selectbox("Select Messages per Person", options=list(range(1, 6)))
        st.session_state.selected_phases = [f"Phase {i}" for i in range(1, selected_phases + 1)]
        
    with col8:
        st.write("Select Content")
        contentA = st.checkbox("Address Pain Point",            value=True, key="contentA")
        contentB = st.checkbox("Offer   Solution",              value=True, key="contentB")
        contentC = st.checkbox("Include Subject Line",          value=platform=="", key="contentC")
        contentD = st.checkbox("Offer   Call to Action",        value=True, key="contentD")
        contentE = st.checkbox("Greet   Customer",              value=True, key="contentE")
    
    if st.button("Generate Campaign"):
            st.session_state.content = {}
            st.session_state.generated = True
            st.session_state.current_phase = 0
    
    st.markdown("---")
    
    if st.session_state.generated:
        cg.generate_phase_content()
