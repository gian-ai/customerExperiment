import streamlit as st
import pandas as pd
import requests
import json
import numpy as np
from copy import deepcopy
import pages.helpers.auth as auth

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # Track if the user is logged in
if 'username' not in st.session_state:
    st.session_state.username = ""  # Store the logged-in user's username

# Initialize session state for variables and options related to the script and agenda
if ('variable' not in st.session_state) or (type(st.session_state.variable) is pd.DataFrame):
    st.session_state.variable = 0  # Store the selected variable generator ID

if 'variableOptions' not in st.session_state:
    st.session_state.variableOptions = list()  # Options for variable selection

if 'prospectOptions' not in st.session_state:
    st.session_state.prospectOptions = list()  # Options for the number of prospects

if 'phase' not in st.session_state:
    st.session_state.phase = list()  # Track the selected phase

if 'agenda' not in st.session_state:
    st.session_state.agenda = pd.DataFrame()  # Store the call agenda as a DataFrame

if 'task' not in st.session_state:
    st.session_state.task = pd.Series()  # Store the current task

if 'trials' not in st.session_state:
    st.session_state.trials = 5  # Default number of trials per experiment

if 'experiment' not in st.session_state:
    st.session_state.experiment = list()  # Store selected experiment details

if 'experimentOptions' not in st.session_state:
    st.session_state.experimentOptions = list()  # Options for experiment selection

if 'callSession' not in st.session_state:
    st.session_state.callSession = list()  # Track if a call session is active

# Initialize additional session state variables for customer interactions
if 'customers' not in st.session_state:
    st.session_state.customers = None

if 'callStatus' not in st.session_state:
    st.session_state.callStatus = ""  # Track the status of the current call
    
if 'notes' not in st.session_state:
    st.session_state.notes = ""  # Store notes for the current call

# Track progress through different parts of the call script
if 'progressA' not in st.session_state:
    st.session_state.progressA = False

if 'progressB' not in st.session_state:
    st.session_state.progressB = False

if 'progressC' not in st.session_state:
    st.session_state.progressC = False

if 'progressD' not in st.session_state:
    st.session_state.progressD = False

if 'progressE' not in st.session_state:
    st.session_state.progressE = False

# Set the page title and icon for Streamlit
st.set_page_config(page_title="Woops Assistant", page_icon="📈")

# Define the location of the service account file and backend URL
SERVICE_ACCOUNT_FILE = 'pages/helpers/secrets/key.json'
backend_url = auth.get_backendURL()

# Function to get available scripts for a given phase and platform
def getScripts():
    """
    Retrieves available scripts (variable generators) for the specified phase and platform.
    
    Returns:
        A list of variable generator options.
    """
    url = f"{backend_url}/variablegenerators"
    payload = {
        "ownerEmail": st.session_state.username,
        "platform": "Phone",
        "phase": f"Phase {st.session_state.phase}"
    }
    
    token = auth.get_auth_idtoken()  # Get the authentication token
    headers = {"Authorization": f"Bearer {token}"}  # Authorization header
    req = requests.get(url=url, params=payload, headers=headers)  # Make the GET request
    experiment_options = req.json()["variableGenerators"]  # Extract the variable generator options

    return experiment_options  # Return the list of options

# Function to view details of the selected script
def viewScriptDetails():
    """
    Retrieves and displays the details of the selected script (variable).
    
    Returns:
        A dictionary containing the detailed content of the script.
    """
    content_map = {
        "contentC": "Subject",        
        "contentE": "Greeting",
        "contentA": "Hook",
        "contentB": "Solution",
        "contentD": "CallToAction",
    }
        
    url = f"{backend_url}/variables"
    payload = {"variableGeneratorID": st.session_state.variable}  # Payload with the selected variable ID
    token = auth.get_auth_idtoken()  # Get the authentication token
    headers = {"Authorization": f"Bearer {token}"}  # Authorization header
    req = requests.get(url=url, params=payload, headers=headers)  # Make the GET request
    data = pd.DataFrame(req.json()["variables"])  # Convert the response to a DataFrame
    key_filter = data.keys().str.contains("content")  # Filter keys that contain "content"
    
    content_keys = data.keys()[key_filter]
    content_dict = {}

    maxComponents = 0
    for c in content_keys:
        component = content_map.get(c)  # Map content keys to their respective components
        for i, v in enumerate(data[c].values):
            content_dict.update({f"{component} {i}": v})  # Populate the content dictionary
            maxComponents = max(maxComponents, i)

    # Display the script details in the Streamlit app
    for i in range(maxComponents + 1):
        st.write(f"***Version {i+1}***")
        with st.container(border=True):
            for key, value in content_map.items():
                if content_dict.get(f"{value} {i}"):
                    st.write(f"{value}: {content_dict.get(f'{value} {i}')}")

    return content_dict  # Return the content dictionary

# Function to submit an experiment to the backend
def submitExperiments():
    """
    Submits the selected script (variable) as an experiment to the backend API.
    
    Returns:
        Response object indicating the success or failure of the submission.
    """
    params = {
        "platform": "Phone",
        "numExperiments": 1,  # Only one script per submission
        "trials": st.session_state.trials,
        "country": "United States",
        "varGenIDs": [st.session_state.variable],
        "ownerEmail": st.session_state.username
    }

    req = requests.post(url=f"{backend_url}/experiments", 
                        json=params, 
                        headers={"Authorization": f"Bearer {auth.get_auth_idtoken()}"})
    st.write("Submit Experiment API:", req)  # Display the response in the app
    if req.text == "Internal Server Error":
        st.write("Error: Upload customers")

    st.session_state.variableOptions = []
    st.session_state.variable = []
    st.session_state.prospectOptions = []
    
    return req  # Return the response

# Function to retrieve the call agenda from the backend
def getCallAgenda():
    """
    Retrieves the call agenda for the logged-in user from the backend API.
    
    Returns:
        DataFrame containing the call agenda.
    """
    url = f"{backend_url}/agenda"
    payload = {
        "ownerEmail": st.session_state.username,
        "platform": "Phone"
    }
    token = auth.get_auth_idtoken()  # Get the authentication token
    headers = {"Authorization": f"Bearer {token}"}  # Authorization header
    req = requests.get(url=url, params=payload, headers=headers)  # Make the GET request
    
    callAgenda = req.json()["Tasks"]  # Extract the tasks from the response

    if len(callAgenda) > 0:
        callAgenda = pd.DataFrame(callAgenda).fillna(np.nan).replace([np.nan], [None])
        st.session_state.agenda = callAgenda  # Store the agenda in session state

        return st.session_state.agenda  # Return the agenda DataFrame
    else:
        st.write("Upload more customers.")

# Function to get the next task from the call agenda
def getTask():
    """
    Retrieves the next task from the call agenda.
    
    Returns:
        Series containing the next task.
    """
    retries = 2
    while st.session_state.agenda.empty and retries > 0:
        getCallAgenda()  # Try to fetch the agenda if it's empty
        retries -= 1
    if not st.session_state.agenda.empty:
        st.session_state.task = st.session_state.agenda.iloc[0, :].fillna(np.nan).replace([np.nan], [None])
        return st.session_state.task  # Return the next task
    return None

# Function to complete the current task and submit the event to the backend
def completeTask():
    """
    Completes the current task and submits the completion event to the backend API.
    
    Returns:
        Response object indicating the success or failure of the task completion.
    """
    st.session_state.agenda = st.session_state.agenda.iloc[1:, :]  # Remove the completed task from the agenda
    
    taskInfo = deepcopy(st.session_state.task.to_dict())  # Deep copy of the task info

    taskInfo.update({
        "notes": st.session_state.notes,
        "callStatus": st.session_state.callStatus,
        "progressA": st.session_state.progressA,
        "progressB": st.session_state.progressB,
        "progressC": st.session_state.progressC,
        "progressD": st.session_state.progressD,
        "progressE": st.session_state.progressE
    })

    url = f"{backend_url}/agenda"
    payload = {"event": json.dumps(taskInfo)}  # Payload with the task completion info
    
    token = auth.get_auth_idtoken()  # Get the authentication token
    headers = {"Authorization": f"Bearer {token}"}  # Authorization header
    req = requests.post(url=url, json=payload, headers=headers)  # Submit the task completion to the backend

    return req  # Return the response

# Function to reset the call session state variables
def resetCallSession():
    """
    Resets the session state variables related to the current call session.
    """
    st.session_state.callStatus = ""
    st.session_state.notes = ""
    st.session_state.progressA = False
    st.session_state.progressB = False
    st.session_state.progressC = False
    st.session_state.progressD = False
    st.session_state.progressE = False

# Function to count the number of tasks completed (currently not implemented)
def countTasksCompleted():
    """
    Placeholder function to count the number of completed tasks.
    """
    pass

# New columns for Customers (commented out)
# 1) call_Notes:str
# 2) call_convertStatus(No/Active/Yes):str
# 3) call_count:str
# 4) call_nextActionDate:str 
# 5) call_experimentID

# Display login or main content based on login status
if not st.session_state.logged_in:
    auth.login()  # Display the login form if the user is not logged in
else:
    st.sidebar.button("Logout", on_click=auth.logout)  # Provide a logout button in the sidebar

    quota = 25  # Daily quota for calls
    status = 0  # Status of completed calls

    column_size = 15
    column_margins = 1

    tab1, tab2 = st.tabs(["Phone Assistant", "Call Scheduler"])  # Two tabs for different functionalities

    with tab1:
        # Display the daily quota, scheduled, and completed call status
        with st.container(border=True):
            quotaCol, scheduledCol, completedCol = st.columns(3)
            with quotaCol:
                st.write(f"***Daily Quota:*** {quota}")
            with scheduledCol:
                st.write(f"***Scheduled:*** {status}")
            with completedCol:
                st.write(f"***Completed:*** {status}")
            
        # Main call session interface
        with st.container(border=True):
            st1, _, st2 = st.columns([column_size, column_margins, column_size], 
                                    vertical_alignment="top")

            if not st.session_state.callSession:
                st.button("Start", use_container_width=True, on_click=getCallAgenda)  # Start the call session
                if not st.session_state.agenda.empty:
                    st.session_state.callSession = True  # Activate call session if agenda is available

            else:
                try:
                    task = getTask().fillna(np.nan).replace([np.nan], [None])  # Get the next task

                    # Display prospect details
                    with st1:
                        st.header("Prospect")
                        st.write(f"Name: {task.loc['name']}")
                        st.write(f"Company: {task.loc['company']}")
                        st.write(f"Role: {task.loc['role']}")
                        st.write(f"Phone #: {task.loc['phoneNumber']}")
                        st.write(f"Email: {task.loc['email']}")
                        st.divider()
                        no_convert, no_answer, convert = st.columns(3)
                        with no_answer:
                            if st.button("♺", help="Call prospect again."):
                                st.session_state.callStatus = "RETRY"
                        with no_convert:
                            if st.button("❌", help="Prospect is not interested."):
                                st.session_state.callStatus = "STOP"
                        with convert:
                            if st.button("✔️", help="Prospect is converted."):
                                st.session_state.callStatus = "CONVERT"

                        if st.session_state.callStatus != "":
                            if st.button("Complete Task", on_click=completeTask, 
                                    use_container_width=True):
                                    resetCallSession()  # Reset session after task completion
                                    st.rerun()  # Rerun the app to refresh the interface
                        
                    # Display the script content
                    with st2:
                        st.header("Script")

                        content = task[task.keys().str.contains("content")].dropna()

                        contentC = content.keys().str.contains("C")
                        if contentC.any():
                            st.checkbox(content[contentC].values[0], key="progressC")
                        contentE = content.keys().str.contains("E")
                        if contentE.any():
                            st.checkbox(content[contentE].values[0], key="progressE")
                        contentA = content.keys().str.contains("A")
                        if contentA.any():
                            st.checkbox(content[contentA].values[0], key="progressA")
                        contentB = content.keys().str.contains("B")
                        if contentB.any():
                            st.checkbox(content[contentB].values[0], key="progressB")
                        contentD = content.keys().str.contains("D")
                        if contentD.any():
                            st.checkbox(content[contentD].values[0], key="progressD")

                        st.text_input("Notes:", key="notes")  # Input for call notes

                except Exception as e:
                    st.header("Schedule more calls!")  # Display message if no calls are scheduled

    with tab2:        
        # Interface for scheduling more prospects into the agenda
        with st.container(border=True):
            st.header("Schedule more prospects into Agenda")
            
            phaseColumn, getColumn  = st.columns(2, vertical_alignment="bottom")
            
            with phaseColumn:
                st.session_state.phase = st.selectbox("Select Phase", options=[1,2,3,4,5])

            with getColumn:
                if st.button("Get Scripts"):
                    script_options = getScripts()
                    if len(script_options) == 0:
                        st.write("No scripts found for this phase.")
                        st.session_state.variableOptions = list()
                        st.session_state.prospectOptions = list()
                    else:
                        data = pd.DataFrame(script_options)
                        experiment_options = data["variableGeneratorID"]
                        st.session_state.variableOptions = dict(enumerate(experiment_options, 1))
                        st.session_state.prospectOptions = range(5, 26, 5)

            scriptColumn, trialColumn = st.columns(2)
            options = []
        
            with scriptColumn:
                temp_selection = st.selectbox("Select Script", 
                                              options=st.session_state.variableOptions)
                if temp_selection is not None:
                    if st.button("Show", use_container_width = True):
                        st.session_state.variable = st.session_state.variableOptions[temp_selection]

                        details = viewScriptDetails()

            with trialColumn:
                    temp_trials = st.selectbox("How many prospects?", 
                                               options=st.session_state.prospectOptions)
                    if st.session_state.variable != 0:
                        if st.button("Generate", use_container_width = True):
                            st.session_state.trials = temp_trials
                            trials = submitExperiments()

        # Interface for reviewing the current call agenda
        with st.container(border=True):
            st.header("Review Call Agenda")
            if not st.session_state.agenda.empty:
                data = st.session_state.agenda[["phoneNumber", "name", "role"]]
                data = data.drop_duplicates(keep="first").set_index("phoneNumber")
                st.write(data)
            if st.button("Refresh Agenda"):
                getCallAgenda()
                st.rerun()

