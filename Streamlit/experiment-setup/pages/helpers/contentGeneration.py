import pandas as pd
from itertools import product
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import pandas as pd
import time
import streamlit as st
import pages.helpers.auth as auth
import numpy as np
import requests

# Initialize backend URL and service account file
backend_url = auth.get_backendURL()
SERVICE_ACCOUNT_FILE = 'pages/helpers/secrets/key.json'

# Function to generate the prompt and task (labor) for addressing a pain point
def body_painpoint(phase: str, product: str, target_audience: str, target_industry: str, features: list, language: str, characterLimit: str) -> (str, str):
    """
    Generates the prompt and task description for addressing a pain point in customer communication.

    Args:
        phase (str): The phase of communication (e.g., Phase 1, Phase 2).
        product (str): The product being discussed.
        target_audience (str): The target audience for the communication.
        target_industry (str): The target industry of the audience.
        features (list): A list of product features.
        language (str): The language in which the message should be written.
        characterLimit (str): The character limit for the message.

    Returns:
        tuple: A tuple containing the prompt and task description.
    """
    prompt = f"You are a professional and experienced customer service representative that introduces customers to technology.\
             You are specialized in the {product}, which has the following features: {features}.\
             You speak {language} natively, write in your native language. If the language is gendered, reference the product and brand in the masculine. DONT USE HASHTAGS NOR EMOJIS"

    if phase == "Phase 1":
        labor = f"Task: Tell the customer that right now, this pain point may be a part of their day-to-day operations. Then, assert what having the pain point implies about the way they think, in a positive way.\
                Do ONLY THIS without PROVIDING A SOLUTION, using hashtags or emojis, by WRITING 2 WARM AND PROFESSIONAL SENTENCES WITH A MAXIMUM 20 WORD LIMIT."
    elif phase == "Phase 2":
        labor = f"Task: Ask a question to find out if the customer shares the pain point in their position in {target_industry}. Then, assert what having the pain point implies about the way they think, in a positive way\
                Do ONLY THIS without PROVIDING A SOLUTION, using hashtags or emojis, by WRITING 2 WARM AND PROFESSIONAL SENTENCES."
    elif phase == "Phase 3":
        labor = f"Task: Ask a question to find out if the customer shares the pain point in their position in {target_industry}. Then, complement why the industry still does it that way, in a positive light.\
                Do ONLY THIS without PROVIDING A SOLUTION, using hashtags or emojis, by WRITING 2 WARM AND PROFESSIONAL SENTENCES WITH A MAXIMUM 20 WORD LIMIT."
    elif phase == "Phase 4" or phase == "Phase 5":
        labor = f"First: State you are just following up because you want to help {target_audience} professionals in {target_industry} evolve out of ***input pain point here***.\
                  Second: Quickly remind the customer that if they are struggling with this pain point and dive deeper into the implications of the pain point.\
                  GUIDELINES: Do ONLY THIS WITHOUT PROVIDING A SOLUTION, DONT USE hashtags or emojis, WRITE A WARM AND PROFESSIONAL SENTENCE WITH A MAXIMUM 20 WORD LIMIT."

    return prompt, labor

# Function to generate the prompt and task (labor) for providing a solution
def body_solution(phase: str, product: str, target_audience: str, target_industry: str, features: list, language: str, characterLimit: str) -> (str, str):
    """
    Generates the prompt and task description for providing a solution in customer communication.

    Args:
        phase (str): The phase of communication (e.g., Phase 1, Phase 2).
        product (str): The product being discussed.
        target_audience (str): The target audience for the communication.
        target_industry (str): The target industry of the audience.
        features (list): A list of product features.
        language (str): The language in which the message should be written.
        characterLimit (str): The character limit for the message.

    Returns:
        tuple: A tuple containing the prompt and task description.
    """
    prompt = f"You are a professional and experienced customer service representative that introduces {target_audience} professionals to technology.\
             You are specialized in the {product}, which has the following features: {features}.\
             WRITE THE MESSAGE IN {language}. If the language is gendered, reference the product and brand in the masculine."
    
    if phase == "Phase 1" or phase == "Phase 2" or phase == "Phase 3":
        labor = f"First (15 WORD LIMIT): Using 'however' or 'instead' or 'on the other hand', Make an observation of how the pain point affects 3 of the key metrics impacting {target_audience} professionals in the {target_industry} industry."
    elif phase == "Phase 4" or phase == "Phase 5":
        labor = f"TASK: Quickly remind the customer that we have helped {target_audience} professionals in {target_industry} struggling with this pain point and dive deeper into the implications of the solution.\
                GUIDELINES: YOU MUST ADHERE TO THE MAX 20 WORD LIMIT FOR THE ENTIRE MESSAGE WITHOUT A GREETING NOR CALL TO ACTION AND WRITE IT CONVERSATIONALLY."

    return prompt, labor

# Function to generate the prompt and task (labor) for a call to action
def callToAction(phase: str, product: str, target_audience: str, target_industry: str, features: list, language: str, characterLimit: str, callToAction: list) -> str:
    """
    Generates the prompt and task description for a call to action in customer communication.

    Args:
        phase (str): The phase of communication (e.g., Phase 1, Phase 2).
        product (str): The product being discussed.
        target_audience (str): The target audience for the communication.
        target_industry (str): The target industry of the audience.
        features (list): A list of product features.
        language (str): The language in which the message should be written.
        characterLimit (str): The character limit for the message.
        callToAction (list): A list of call-to-action links and descriptions.

    Returns:
        tuple: A tuple containing the prompt and task description.
    """
    prompt = f"You are a professional and experienced customer service representative that introduces customers to technology.\
             You are specialized in the {product}, which has the following features: {features}. WRITE IN A FRIENDLY AND CONVERSATIONAL TONE.\
             WRITE THE MESSAGE IN {language}. If the language is gendered, reference the product and brand in the masculine. The URL link and description pairs that you have available to use are: {callToAction}."

    if phase == "Phase 1":
        labor = f"TASK: Find out if the customer has looked into automating the process. This is the only task\
                GUIDELINES: YOU MUST USE UP TO A MAXIMUM OF 8 WORDS FOR THE ENTIRE MESSAGE. DO NOT GREET THE CUSTOMER."
    elif phase == "Phase 2":
        labor = f"TASK: Find out if the customer has looked into approaching the pain point with software. This is the only task\
                GUIDELINES:YOU MUST USE UP TO A MAXIMUM OF 8 WORDS FOR THE ENTIRE MESSAGE. DO NOT GREET THE CUSTOMER."
    elif phase == "Phase 3" or phase == "Phase 4":
        labor = f"TASK: Find out if the customer would like to learn more about how to automate the process. This is the only task\
                GUIDELINES:YOU MUST USE UP TO A MAXIMUM OF 8 WORDS FOR THE ENTIRE MESSAGE. DO NOT GREET THE CUSTOMER."
    elif phase == "Phase 5":
        labor = f"TASK: State to the customer to let you know if there is someone else you can reach out to to solve the pain point. THIS IS THE ONLY TASK.\
                Example FOR TONE AND CONTENT: If there is someone else in your organization responsible for addressing this pain point, please let me know, and I’d be happy to reach out to them directly. GUIDELINES: YOU MUST USE UP TO A MAXIMUM OF 30 WORDS FOR THE ENTIRE MESSAGE. DO NOT GREET THE CUSTOMER."

    return prompt, labor

# Function to generate the prompt and task (labor) for a subject line
def subjectLine(phase: str, product: str, target_audience: str, target_industry: str, features: list, language: str, characterLimit: str) -> str:
    """
    Generates the prompt and task description for creating a subject line in customer communication.

    Args:
        phase (str): The phase of communication (e.g., Phase 1, Phase 2).
        product (str): The product being discussed.
        target_audience (str): The target audience for the communication.
        target_industry (str): The target industry of the audience.
        features (list): A list of product features.
        language (str): The language in which the message should be written.
        characterLimit (str): The character limit for the message.

    Returns:
        tuple: A tuple containing the prompt and task description.
    """
    prompt = f"You are a professional and experienced customer service representative that introduces customers to technology.\
             You are specialized in the {product}, which has the following features: {features}.\
             WRITE THE MESSAGE IN {language}. If the language is gendered, reference the product and brand in the masculine."
    
    if phase == "Phase 1":
        labor = f"First: Use 4 Words to Greet the Customer, rephrasing Hi NAME: Meet BRAND.\
                  YOU MUST ADHERE TO THE MAXIMUM OF 8 WORDS FOR THE ENTIRE MESSAGE."
    elif phase == "Phase 2" or phase == "Phase 3":
        labor = f"First: Use 4 Words to Greet the Customer, rephrasing Hi NAME: Meet BRAND, Just Following Up.\
                  YOU MUST ADHERE TO THE MAXIMUM OF 8 WORDS FOR THE ENTIRE MESSAGE."
    elif phase == "Phase 4":
        labor = f"First: Use 4 Words to Greet the Customer, rephrasing Hi NAME: Meet BRAND, Just Following Up.\
                  YOU MUST ADHERE TO THE MAXIMUM OF 8 WORDS FOR THE ENTIRE MESSAGE."
    elif phase == "Phase 5":
        labor = f"First: Use 4 Words to Greet the Customer, rephrasing Hi NAME: Meet BRAND, Just Following Up.\
                  YOU MUST ADHERE TO THE MAXIMUM OF 8 WORDS FOR THE ENTIRE MESSAGE."
    
    return prompt, labor

# Function to generate the prompt and task (labor) for a greeting
def greeting(phase: str, product: str, target_audience: str, target_industry: str, features: list, language: str, characterLimit: str) -> str:
    """
    Generates the prompt and task description for creating a greeting in customer communication.

    Args:
        phase (str): The phase of communication (e.g., Phase 1, Phase 2).
        product (str): The product being discussed.
        target_audience (str): The target audience for the communication.
        target_industry (str): The target industry of the audience.
        features (list): A list of product features.
        language (str): The language in which the message should be written.
        characterLimit (str): The character limit for the message.

    Returns:
        tuple: A tuple containing the prompt and task description.
    """
    prompt = f"You are a professional and experienced customer service representative that introduces customers to technology.\
         You are specialized in the {product}, which has the following features: {features}.\
         GUIDELINE: WRITE THE MESSAGE IN {language}. If the language is gendered, reference the product and brand in the masculine."

    labor = f"TASK: Greet the customer using 1 word. Thats the only task."
    
    return prompt, labor

# Function to generate the output message using the OpenAI API
def chatOutput(client, prompt: str, labor: str, pain: str = None) -> str:
    """
    Generates an output from GPT-4 with a predefined prompt, task (labor), and optional pain point.

    Args:
        client: OpenAI client object.
        prompt (str): The prompt describing the situation.
        labor (str): The specific task to generate the message.
        pain (str, optional): The pain point to address in the message.

    Returns:
        str: The generated output message.
    """
    if pain is not None:
        painPointText = f"PainPoint: {pain}"
        messages = [
          {"role": "system", "content": f"{prompt}\n{labor}"},
          {"role": "user", "content": f"\n{painPointText}\n"}
        ]
    else:
        messages = [
          {"role": "system", "content": f"{prompt}\n{labor}"}
        ]
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    
    output = response.choices[0].message.content
    return output

# Function to send data to an external API and stream the results
def ask_llm(data):
    """
    Prepares data and calls OpenAI API for generating content based on the provided data.

    Args:
        data (dict): A dictionary containing all the necessary parameters for generating content.

    Returns:
        str: The generated content from the LLM.
    """
    key_location = "pages/helpers/secrets/OpenAI.json"
    client = OpenAI(api_key=auth.get_openai_key(key_location))

    if data["flag"] == "PainPoint":
        prompt, labor = body_painpoint(
            data["phase"], 
            data["product_name"], 
            data["target_audience"],
            data["target_industry"],
            data["features"],
            data["language"],
            data["character_limit"]
        )
    elif data["flag"] == "Solution":
        prompt, labor = body_solution(
            data["phase"], 
            data["product_name"], 
            data["target_audience"],
            data["target_industry"],
            data["features"],
            data["language"],
            data["character_limit"]
        )
    elif data["flag"] == "Subject":
        prompt, labor = subjectLine(
            data["phase"], 
            data["product_name"], 
            data["target_audience"],
            data["target_industry"],
            data["features"],
            data["language"],
            data["character_limit"]
        )
    elif data["flag"] == "CallToAction":
        prompt, labor = callToAction(
            data["phase"], 
            data["product_name"], 
            data["target_audience"],
            data["target_industry"],
            data["features"],
            data["language"],
            data["character_limit"],
            data["call_to_actions"]
        )
    elif data["flag"] == "Greeting":
        prompt, labor = greeting(
            data["phase"], 
            data["product_name"], 
            data["target_audience"],
            data["target_industry"],
            data["features"],
            data["language"],
            data["character_limit"]
        )
    
    return chatOutput(client, prompt, labor, data["pain_point"])

# Function to handle the submission of a pain point and phase for LLM content generation
def handle_submission(pain_point, phase, flag):
    """
    Handles the submission of data for generating content using the LLM based on the specified phase, pain point, and content type.

    Args:
        pain_point (str): The pain point to address.
        phase (str): The communication phase (e.g., Phase 1, Phase 2).
        flag (str): The content type flag (e.g., contentA for PainPoint, contentB for Solution).

    Returns:
        str: The generated content.
    """
    content_map = {
        "contentA": "PainPoint",
        "contentB": "Solution",
        "contentC": "Subject",
        "contentD": "CallToAction",
        "contentE": "Greeting",
    }
    
    data = {
        "product_name": st.session_state.product_name,
        "pain_point": pain_point,
        "phase": phase,
        "platform": st.session_state.platform,
        "language": st.session_state.language,
        "flag": content_map[flag],
        "features": st.session_state.features,
        "call_to_actions": st.session_state.call_to_actions,
        "character_limit": st.session_state.char_limit,
        "target_industry": st.session_state.target_industry,
        "target_audience": st.session_state.target_audience
    }

    with st.spinner(f"Generating content for {pain_point} - {phase}..."):
        response_stream = ask_llm(data)
        result = ""
        for line in response_stream:
            result += line
        return result

# Function to update the product name in session state
def submit_product_name():
    """
    Updates the product name in the session state with the temporary product name.
    """
    st.session_state.product_name = st.session_state.temp_product_name

# Function to add a call to action link and description to the session state
def add_call_to_action():
    """
    Adds a new call to action link and description to the session state.
    """
    cta_input = st.session_state.temp_call_to_action
    if cta_input:
        link = st.session_state.temp_call_to_action
        desc = st.session_state.temp_call_to_action_desc
        st.session_state.call_to_actions.append((link, desc))
        st.session_state.temp_call_to_action = ""
        st.session_state.temp_call_to_action_desc = ""

# Function to add a pain point to the session state
def add_pain_point():
    """
    Adds a new pain point to the session state.
    """
    pain_point_input = st.session_state.temp_pain_point
    if pain_point_input:
        st.session_state.pain_points.append(pain_point_input)
        st.session_state.temp_pain_point = ""

# Function to add a target audience to the session state
def add_target_audience():
    """
    Adds a new target audience to the session state.
    """
    target_audience_input = st.session_state.temp_target_audience
    if target_audience_input:
        st.session_state.target_audience = target_audience_input

# Function to add a target industry to the session state
def add_target_industry():
    """
    Adds a new target industry to the session state.
    """
    target_industry_input = st.session_state.temp_target_industry
    if target_industry_input:
        st.session_state.target_industry = target_industry_input

# Function to add a product feature to the session state
def add_feature():
    """
    Adds a new product feature to the session state.
    """
    feature_input = st.session_state.temp_feature
    if feature_input:
        st.session_state.features.append(feature_input)
        st.session_state.temp_feature = ""

# Function to clear all call-to-action links from the session state
def clear_call_to_actions():
    """
    Clears all call-to-action links from the session state.
    """
    st.session_state.call_to_actions = []

# Function to clear all pain points from the session state
def clear_pain_points():
    """
    Clears all pain points from the session state.
    """
    st.session_state.pain_points = []

# Function to clear all product features from the session state
def clear_features():
    """
    Clears all product features from the session state.
    """
    st.session_state.features = []

# Function to generate content for each phase of the campaign
def generate_phase_content():
    """
    Generates content for each selected phase based on the session state configurations.
    """
    if st.session_state.current_phase < len(st.session_state.selected_phases):
        phase = st.session_state.selected_phases[st.session_state.current_phase]
        st.header(f"Phase: {phase}")
        
        content_map = {
            "contentA": "PainPoint",
            "contentB": "Solution",
            "contentC": "Subject",
            "contentD": "CallToAction",
            "contentE": "Greeting",
        }

        def update_content(content_key):
            parts = content_key.split('_')
            pain_point = '_'.join(parts[:-3])
            flag = parts[-3]
            phase = parts[-2]
            idx = parts[-1]
            st.write(pain_point, flag, phase, idx)
            st.session_state.content[phase][content_key] = st.session_state[content_key]

        for idx, pain_point in enumerate(st.session_state.pain_points):
            st.subheader(f"Pain Point: {pain_point}")
            selected_flags = [flag for flag in ['contentC', 'contentE', 'contentA', 'contentB', 'contentD'] if st.session_state.get(flag)]
            content_keys = []

            button_col1, button_col2 = st.columns(2)
            with button_col1:
                if st.button(f"Generate Content", key=f"gen_all_{phase}_{pain_point}_{idx}"):
                    with st.spinner(f"Generating content ..."):
                        for flag in selected_flags:
                            content_key = f"{pain_point}_{flag}_{phase}_{idx}"
                            st.session_state.content.setdefault(phase, {})[content_key] = handle_submission(pain_point, phase, flag)
                        st.session_state[f"generated_{phase}_{pain_point}_{idx}"] = True
            with button_col2:
                if st.button(f"Update Content", key=f"sub_all_{phase}_{pain_point}_{idx}"):
                    for flag in selected_flags:
                        content_key = f"{pain_point}_{flag}_{phase}_{idx}"
                        st.session_state.content.setdefault(phase, {})[content_key] = st.session_state.get(content_key, "")
                    st.session_state[f"submitted_{phase}_{pain_point}_{idx}"] = True

            for flag in selected_flags:
                if phase not in st.session_state.content:
                    st.session_state.content[phase] = {}
                content_key = f"{pain_point}_{flag}_{phase}_{idx}"
                content_keys.append(content_key)
                if content_key not in st.session_state.content[phase]:
                    st.session_state.content[phase][content_key] = ""
                is_content_generated = st.session_state.get(f"generated_{phase}_{pain_point}_{idx}", False)

                st.text_area(
                    f"{content_map[flag]}",
                    value=st.session_state.content[phase].get(content_key, ""),
                    height=100,
                    key=content_key,
                    max_chars=500,
                    disabled=not is_content_generated,
                    on_change=update_content,
                    args=(content_key,)
                )

        st.markdown("---")
        phase_col1, phase_col2 = st.columns(2)
        with phase_col1:
            st.button(f"Submit {phase}", key=f"submit_phase_{phase}", on_click=submit_phase, args=[phase])
    else:
        st.success("All phases submitted successfully!")

# Function to submit the current phase of content generation
def submit_phase(phase):
    """
    Submits the current phase of generated content and proceeds to the next phase.
    """
    st.session_state.current_phase += 1
    if not st.session_state.current_phase < len(st.session_state.selected_phases):
        submit_campaign()
        st.session_state.generated = False

# Function to send the campaign data to the backend for processing
def submit_campaign_data(campaignData):
    """
    Sends the compiled campaign data to the backend API for storage.

    Args:
        campaignData (dict): A dictionary containing the campaign data to be submitted.

    Returns:
        requests.Response: The response from the API.
    """
    req = requests.post(url=f"{backend_url}/variables", json=campaignData, headers={"Authorization": f"Bearer {auth.get_auth_idtoken()}"})
    st.write("Upload Request Submitted to API:", req)
    st.write(req.text)

    return req

# Function to submit the entire campaign after all phases are completed
def submit_campaign():
    """
    Submits the entire campaign to the backend after all phases are completed.
    """
    cleaned_content = []

    for phase, phase_content in st.session_state.content.items():
        for key, value in phase_content.items():
            if value:
                parts = key.split('_')
                pain_point_key = parts[0]
                cleaned_content.append({"Phase": phase, "Pain Point": pain_point_key, parts[1]: value})
    
    clean_df = pd.DataFrame(cleaned_content).replace({np.nan: ""}).groupby(["Phase", "Pain Point"]).agg(lambda col: "".join(col)).reset_index()

    campaign_data = {        
        "Product": st.session_state.product_name,
        "Platform": st.session_state.platform,
        "OwnerEmail": st.session_state.username,
        "rawData": clean_df.to_dict()
    }

    submit_campaign_data(campaign_data)
    st.write(clean_df)

    st.session_state.content = {}
    st.session_state.current_phase = 0
    st.session_state.generated = False
