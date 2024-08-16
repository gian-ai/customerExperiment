import streamlit as st
import pandas as pd
import requests
import pages.helpers.auth as auth

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

if ('variables' not in st.session_state) or (type(st.session_state.variables) is pd.DataFrame):
    st.session_state.variables = list()

if 'variableOptions' not in st.session_state:
    st.session_state.variableOptions = list()

if 'experiments' not in st.session_state:
    st.session_state.experiments = list()
if 'experimentOptions' not in st.session_state:
    st.session_state.experimentOptions = list()
    
backend_url = "https://backend-auth-vmazoy5ygq-uc.a.run.app"

st.set_page_config(page_title="Outbound Experiment", page_icon="📈")


def getVariableGenerators():
    url = f"{backend_url}/variablegenerators"
    payload = {"ownerEmail":st.session_state.username}
    
    token = auth.get_auth_idtoken()
    headers = {"Authorization": f"Bearer {token}"}
    
    req = requests.get(url=url, params=payload, headers=headers)
    st.write("Variables Retrieved from API:", req)
    return req


def getExperimentGenerators():
    url = f"{backend_url}/experimentgenerators"
    payload = {"ownerEmail":st.session_state.username}
    
    token = auth.get_auth_idtoken()
    headers = {"Authorization": f"Bearer {token}"}

    full_url = requests.Request('GET', url=url, params=payload).prepare().url
    
    req = requests.get(url=url, params=payload, headers=headers)
    st.write("Experiments Retrieved from API:", req)
    return req



def viewExperimentDetails():
    url = f"{backend_url}/experiments"
    payload = {
        "ownerEmail":st.session_state.username,
        "experimentGeneratorIDs":"-".join(st.session_state.experiments),
    }
    
    token = auth.get_auth_idtoken()
    headers = {"Authorization": f"Bearer {token}"}
    req = requests.get(url=url, params=payload, headers=headers)
    
    st.write("Experiment Details API:", req)
    return req


def exportContacts():
    url = f"{backend_url}/experiments/contacts"
    payload = {
        "experimentGeneratorIDs":"-".join(st.session_state.experiments),
    }
    
    token = auth.get_auth_idtoken()
    headers = {"Authorization": f"Bearer {token}"}    
    req = requests.get(url=url, params=payload, headers=headers)
    
    st.write("Export Contacts API:", req)
    return req


def submitExperiments(platform, numExperiments, trials, country):
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
    st.write("Submit Experiment API:", req)
    if req.text == "Internal Server Error":
        st.write("Error: Upload customers")
    return req




# Display login or main content based on login status
if not st.session_state.logged_in:
    auth.login()
else:
    st.sidebar.button("Logout", on_click=auth.logout)
     
    #################################################
    
    st.title("Check Experiment Details")
    
    if st.button("Get Experiment Options"):
        expGenData = getExperimentGenerators()
        expGenData = expGenData.json()
        if len(expGenData["experimentGenerators"])>0:
            expGenDF = pd.DataFrame(expGenData["experimentGenerators"])
            
            st.session_state.experimentOptions = list(expGenDF["experimentGeneratorID"].sort_values().astype(str).values)

            expGenDF = expGenDF.rename(columns={
                "variableGeneratorID_1":"Variable 1",
                "variableGeneratorID_2":"Variable 2",
                "variableGeneratorID_3":"Variable 3",
                "variableGeneratorID_4":"Variable 4",
                "variableGeneratorID_5":"Variable 5",
                "experimentGeneratorID":"Experiment",
                "platform":"Platform"
            }).set_index(["Platform","Experiment"],drop=True).sort_values(by=["Experiment"]).drop("ownerEmail",axis=1)

            expGenDF_cols = sorted(list(expGenDF.columns))            
            st.write(expGenDF[expGenDF_cols])
            
        else:
            st.write(f"{st.session_state.username} has not created any experiments.")
            st.session_state.experimentOptions = list()
            st.session_state.experiments = list()

    
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
                "experimentID":"Variation",
                "experimentGeneratorID":"Experiment"
            }).set_index("Experiment").sort_values(by=["Experiment","Variation"])
    
            dropColumns = experimentDetails.columns[experimentDetails.columns.str.contains("variable", case=False)]
            experimentDetails = experimentDetails.drop(columns=dropColumns)
    
            st.write(experimentDetails)
        except:
            st.write(f"Error: API returned {req.text}")
    
    if st.button("Export Outbound Content"):
        st.session_state.experiments = selectedExperiments
        experimentDetails = pd.DataFrame(exportContacts().json())
        cols = sorted(list(experimentDetails.columns))
        st.write(experimentDetails[cols])
    
    ############################################
    
    st.title("Create an Experiment")

    if st.button("Get Variable Options"):
        varGenData = getVariableGenerators().json()
        if len(varGenData["variableGenerators"])>0:
            varGenDF = pd.DataFrame(varGenData["variableGenerators"])
            st.session_state.variableOptions = list(varGenDF["variableGeneratorID"].sort_values().astype(str).values)
            varGenDF = varGenDF.rename(columns={
                "variableGeneratorID":"Variable",
                "versionID":"Version"
            }).set_index(
                "Variable", 
                drop=True
            ).sort_values(
                by=["Variable","Version"],
                ascending=[True,False]
            ).loc[:,["ownerEmail","platform","product","phase","Version"]]
            st.write(varGenDF)
        else:
            st.write(f"{st.session_state.username} has not created any variables.")
            st.session_state.variableOptions = list()
            st.session_state.variables = list()

    selected_vars = st.multiselect(
        "Select variables for the experiment",
        st.session_state.variableOptions,
        default=list(),
        # default=st.session_state.variables,
        key='varsMultiselect'
    )
    with st.form("Setup_Experiments"):
        platform = st.selectbox(
            "Which platform are you sending messages to?",
            ("LinkedIn", "Email", "Phone")
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
            req= submitExperiments(platform, numExperiments, trials, country)


        

    