import streamlit as st
import pages.helpers.auth as auth
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Next-Generation A/B Experimentation Platform",
    page_icon=":rocket:"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# Display login or main content based on login status
if not st.session_state.logged_in:
   auth.login()
else:
    st.sidebar.write(f"Logged in: {st.session_state.username}")
    st.sidebar.button("Logout", on_click=auth.logout)

    # Main content
    st.title("Welcome to the Next-Generation A/B Experimentation Platform")
    # st.image(hero_image, use_column_width=True)
    st.subheader("Empower Your Decisions with Data-Driven Insights")
    
    st.markdown("""
        ## Features
        - **Easy Setup**: Get started quickly with our intuitive interface.
        - **Real-Time Results**: Monitor your experiments in real-time.
        - **Advanced Analytics**: Gain deep insights with advanced statistical tools.
        - **Customizable Reports**: Create and share reports tailored to your needs.
        
        ## How It Works
        1. **Define Your Experiment**: Set up your A/B test by defining the variables and goals.
        2. **Run the Experiment**: Launch your test and track progress with real-time updates.
        3. **Analyze the Results**: Use our powerful analytics tools to understand the outcomes.
        4. **Make Data-Driven Decisions**: Leverage insights to make informed business decisions.
        
        ## Get Started
        Ready to take your experimentation to the next level? Start optimizing your strategies today!
        """)
    
