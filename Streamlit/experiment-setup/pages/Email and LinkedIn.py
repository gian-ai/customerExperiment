import streamlit as st
import pandas as pd
import requests
import pages.helpers.auth as auth

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False  # Track if the user is logged in
if 'username' not in st.session_state:
    st.session_state.username = ""  # Store the logged-in user's username

# Initialize session state for variables related to experiments
if ('variables' not in st.session_state) or (type(st.session_state.variables) is pd.DataFrame):
    st.session_state.variables = list()  # Store selected variables for experiments

if 'variableOptions' not in st.session_state:
    st.session_state.variableOptions = list()  # Options for variable selection

if 'experiments' not in st.session_state:
    st.session_state.experiments = list()  # Store selected experiments
if 'experimentOptions' not in st.session_state:
    st.session_state.experimentOptions = list()  # Options for experiment selection
    
backend_url = auth.get_backendURL()  # Get the backend URL from the auth module

st.set_page_config(page_title="Outbound Experiment", page_icon="📈")  # Set the page title and icon for Streamlit

# Function to retrieve variable generators from the backend API
def getVariableGenerators():
    """
    Retrieves the list of variable generators associated with the logged-in user from the backend API.
    
    Returns:
        Response object containing the data of variable generators.
    """
    url = f"{backend_url}/variablegenerators"
    payload = {"ownerEmail": st.session_state.username}  # Payload with the owner's email
    
    token = auth.get_auth_idtoken()  # Get the authentication token
    headers = {"Authorization": f"Bearer {token}"}  # Authorization header
    
    req = requests.get(url=url, params=payload, headers=headers)  # Make the GET request
    st.write("Variables Retrieved from API:", req)  # Display the response in the app
    return req  # Return the response

# Function to retrieve experiment generators from the backend API
def getExperimentGenerators():
    """
    Retrieves the list of experiment generators associated with the logged-in user from the backend API.
    
    Returns:
        Response object containing the data of experiment generators.
    """
    url = f"{backend_url}/experimentgenerators"
    payload = {"ownerEmail": st.session_state.username}  # Payload with the owner's email
    
    token = auth.get_auth_idtoken()  # Get the authentication token
    headers = {"Authorization": f"Bearer {token}"}  # Authorization header

    full_url = requests.Request('GET', url=url, params=payload).prepare().url  # Prepare the full URL for debugging
    
    req = requests.get(url=url, params=payload, headers=headers)  # Make the GET request
    st.write("Experiments Retrieved from API:", req)  # Display the response in the app
    return req  # Return the response

# Function to view details of selected experiments
def viewExperimentDetails():
    """
    Retrieves detailed information about the selected experiments from the backend API.
    
    Returns:
        Response object containing the experiment details.
    """
    url = f"{backend_url}/experiments"
    payload = {
        "ownerEmail": st.session_state.username,
        "experimentGeneratorIDs": "-".join(st.session_state.experiments),  # Join selected experiment IDs
    }
    
    token = auth.get_auth_idtoken()  # Get the authentication token
    headers = {"Authorization": f"Bearer {token}"}  # Authorization header
    req = requests.get(url=url, params=payload, headers=headers)  # Make the GET request
    
    st.write("Experiment Details API:", req)  # Display the response in the app
    return req  # Return the response

# Function to export contacts related to experiments
def exportContacts():
    """
    Exports the contacts related to the selected experiments from the backend API.
    
    Returns:
        Response object containing the contact details for the experiments.
    """
    url = f"{backend_url}/experiments/contacts"
    payload = {
        "experimentGeneratorIDs": "-".join(st.session_state.experiments),  # Join selected experiment IDs
    }
    
    token = auth.get_auth_idtoken()  # Get the authentication token
    headers = {"Authorization": f"Bearer {token}"}  # Authorization header    
    req = requests.get(url=url, params=payload, headers=headers)  # Make the GET request
    
    st.write("Export Contacts API:", req)  # Display the response in the app
    return req  # Return the response

# Function to submit experiments for processing
def submitExperiments(platform, numExperiments, trials, country):
    """
    Submits the experiment setup to the backend API to create the specified number of experiment variations.
    
    Args:
        platform (str): The platform (e.g., LinkedIn, Email) for the experiment.
        numExperiments (int): Number of experiment variations to generate.
        trials (int): Number of trials per experiment.
        country (str): The country the experiment is targeting.
    
    Returns:
        Response object indicating the success or failure of the submission.
    """
    params = {
        "platform": platform,
        "numExperiments": int(numExperiments),
        "trials": int(trials),
        "country": country,
        "varGenIDs": st.session_state.variables,
        "ownerEmail": st.session_state.username
    }
    req = requests.post(url=f"{backend_url}/experiments", 
                        json=params, 
                        headers={"Authorization": f"Bearer {auth.get_auth_idtoken()}"})
    st.write("Submit Experiment API:", req)  # Display the response in the app
    if req.text == "Internal Server Error":
        st.write("Error: Upload customers")
    return req  # Return the response

# Display login or main content based on login status
if not st.session_state.logged_in:
    auth.login()  # Display the login form if the user is not logged in
else:
    st.sidebar.button("Logout", on_click=auth.logout)  # Provide a logout button in the sidebar
     
    #################################################
    
    st.title("Check Experiment Details")
    
    # Retrieve and display experiment options
    if st.button("Get Experiment Options"):
        expGenData = getExperimentGenerators()  # Get experiment generators from the backend
        expGenData = expGenData.json()
        if len(expGenData["experimentGenerators"]) > 0:
            expGenDF = pd.DataFrame(expGenData["experimentGenerators"])
            
            st.session_state.experimentOptions = list(expGenDF["experimentGeneratorID"].sort_values().astype(str).values)

            expGenDF = expGenDF.rename(columns={
                "variableGeneratorID_1": "Variable 1",
                "variableGeneratorID_2": "Variable 2",
                "variableGeneratorID_3": "Variable 3",
                "variableGeneratorID_4": "Variable 4",
                "variableGeneratorID_5": "Variable 5",
                "experimentGeneratorID": "Experiment",
                "platform": "Platform"
            }).set_index(["Platform", "Experiment"], drop=True).sort_values(by=["Experiment"]).drop("ownerEmail", axis=1)

            expGenDF_cols = sorted(list(expGenDF.columns))            
            st.write(expGenDF[expGenDF_cols])
            
        else:
            st.write(f"{st.session_state.username} has not created any experiments.")
            st.session_state.experimentOptions = list()
            st.session_state.experiments = list()
  
    # Select and review experiment details
    selectedExperiments = st.selectbox(
        "Which experiment do you want to review?",
        st.session_state.experimentOptions,
        key="experimentSelect"
    )

    if st.button("Get Experiment Details"):
        st.session_state.experiments = selectedExperiments
        req = viewExperimentDetails()
        try:
            experimentDetails = pd.DataFrame(req.json())
            
            experimentDetails = experimentDetails.rename(columns={
                "experimentID": "Variation",
                "experimentGeneratorID": "Experiment"
            }).set_index("Experiment").sort_values(by=["Experiment", "Variation"])
    
            dropColumns = experimentDetails.columns[experimentDetails.columns.str.contains("variable", case=False)]
            experimentDetails = experimentDetails.drop(columns=dropColumns)
    
            st.write(experimentDetails)
        except:
            st.write(f"Error: API returned {req.text}")
    
    # Export outbound content related to the experiments
    if st.button("Export Outbound Content"):
        st.session_state.experiments = selectedExperiments
        experimentDetails = pd.DataFrame(exportContacts().json())
        cols = sorted(list(experimentDetails.columns))
        st.write(experimentDetails[cols])
    
    ############################################
    
    st.title("Create an Experiment")

    # Retrieve and display variable options
    if st.button("Get Variable Options"):
        varGenData = getVariableGenerators().json()
        if len(varGenData["variableGenerators"]) > 0:
            varGenDF = pd.DataFrame(varGenData["variableGenerators"])
            st.session_state.variableOptions = list(varGenDF["variableGeneratorID"].sort_values().astype(str).values)
            varGenDF = varGenDF.rename(columns={
                "variableGeneratorID": "Variable",
                "versionID": "Version"
            }).set_index(
                "Variable", 
                drop=True
            ).sort_values(
                by=["Variable", "Version"],
                ascending=[True, False]
            ).loc[:, ["ownerEmail", "platform", "product", "phase", "Version"]]
            st.write(varGenDF)
        else:
            st.write(f"{st.session_state.username} has not created any variables.")
            st.session_state.variableOptions = list()
            st.session_state.variables = list()

    # Multi-select box for selecting variables for the experiment
    selected_vars = st.multiselect(
        "Select variables for the experiment",
        st.session_state.variableOptions,
        default=list(),
        key='varsMultiselect'
    )
    
    # Form for submitting the experiment setup
    with st.form("Setup_Experiments"):
        platform = st.selectbox(
            "Which platform are you sending messages to?",
            ("LinkedIn", "Email")
        )
        numExperiments = st.selectbox(
            "How many variations would you like to generate?",
            (3, 5, 10, 15, 20, 25)
        )
        trials = st.selectbox(
            "How many trials would you like to perform per experiment?",
            (1, 10, 25, 50)
        )
        country = st.selectbox(
            "What country is this for?",
            ("United States", "Mexico")
        )

        submitted = st.form_submit_button(label="Submit")

        if submitted:
            # Update the session state variables before submission
            st.session_state.variables = selected_vars
            req = submitExperiments(platform, numExperiments, trials, country)
