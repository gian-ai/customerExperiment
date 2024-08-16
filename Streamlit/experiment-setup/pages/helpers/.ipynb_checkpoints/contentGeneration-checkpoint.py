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

backend_url = 'https://backend-auth-vmazoy5ygq-uc.a.run.app'
# backend_url = "http://127.0.0.1:8000"

SERVICE_ACCOUNT_FILE = 'pages/helpers/secrets/key.json'

def body_painpoint(phase:str, product:str, target_audience:str, target_industry:str, features:list, language:str, characterLimit:str) -> (str, str):
    """
    Get chat parameters for a product of interest with features as defined.
    Features should be a list of strings
    Product should be a single string
    """

    prompt = f"You are a professional and experienced customer service representative that introduces customers to technology.\
             You are specialized in the {product}, which has the following features: {features}.\
             You speak {language} natively, write in your native language. If the language is gendered, reference the product and brand in the masculine. DONT USE HASHTAGS NOR EMOJIS"

    if phase == "Phase 1":
        labor = f"Task: Tell the customer that right now, this pain point may be a part of their day-to-day operations. Then, assert what having the pain point implies about the way they think, in a positive way.\
                Do ONLY THIS without PROVIDING A SOLUTION, using hashtags or emojis, by WRITING 2 WARM AND PROFESSIONAL SENTENCE WITH A MAXIMUM 20 WORD LIMIT."

    elif phase == "Phase 2":
        labor = f"Task: Ask a question to find out if the customer shares the pain point in their position in {target_industry}. Then, assert what having the pain point implies about the way they think, in a positive way\
                Do ONLY THIS without PROVIDING A SOLUTION, using hashtags or emojis, by WRITING 2 WARM AND PROFESSIONAL SENTENCES."

    elif phase == "Phase 3":
        labor = f"Task: Ask a question to find out if the customer shares the pain point in their position in {target_industry}. Then, complement why the industry still does it that way, in a positive light.\
                Do ONLY THIS without PROVIDING A SOLUTION, using hashtags or emojis, by WRITING 2 WARM AND PROFESSIONAL SENTENCE WITH A MAXIMUM 20 WORD LIMIT."
    
    elif phase == "Phase 4" or phase == "Phase 5":
        labor = f"First: State you are just following up because you want to help {target_audience} professionals in  {target_industry} evolve out of ***input pain point here***.\
                  Second: Quickly remind the customer that if they are struggling with this pain point and dive deeper into the implications of the pain point.\
                  GUIDELINES: Do ONLY THIS WITHOUT PROVIDING A SOLUTION, DONT USE hashtags or emojis, WRITE A WARM AND PROFESSIONAL SENTENCE WITH A MAXIMUM 20 WORD LIMIT."

    # elif phase == "Phase 4" or phase == "Phase 5":
    #     labor = f"Second: Use a persuasive and assertive tone to aggressively state the impact that the pain point has on {target_audience} professionals in the {target_industry} industry.\
    #               GUIDELINES: Do ONLY THIS WITHOUT PROVIDING A SOLUTION, DONT USE hashtags or emojis, WRITE A WARM AND PROFESSIONAL SENTENCE WITH A MAXIMUM 20 WORD LIMIT."
                
    return prompt, labor


def body_solution(phase:str, product:str, target_audience:str, target_industry:str, features:list, language:str, characterLimit:str) -> (str, str):
    """
    Get chat parameters for a product of interest with features as defined.
    Features should be a list of strings
    Product should be a single string
    """

    prompt = f"You are a professional and experienced customer service representative that introduces {target_audience} professionals to technology.\
             You are specialized in the {product}, which has the following features: {features}.\
             WRITE THE MESSAGE IN {language}. If the language is gendered, reference the product and brand in the masculine."
    
    if phase == "Phase 1" or phase == "Phase 2" or phase == "Phase 3":
        labor = f"First (15 WORD LIMIT): Using 'however' or 'instead' or 'on the other hand', Make an observation of how the pain point affects 3 of the key metrics impacting {target_audience} professionals in the {target_industry} industry."

    elif phase == "Phase 4" or phase == "Phase 5":
        labor = f"TASK: Quickly remind the customer that we have helped {target_audience} professionals in {target_industry}  struggling with this pain point and dive deeper into the implications of the solution.\
                GUIDELINES: YOU MUST ADHERE TO THE MAX 20 WORD LIMIT FOR THE ENTIRE MESSAGE WITHOUT A GREETING NOR CALL TO ACTION AND WRITE IT CONVERSATIONALLY."

    return prompt, labor


def callToAction(phase:str, product:str, target_audience:str, target_industry:str, features:list, language:str, characterLimit:str, callToAction:list) -> str:
    """
    Get chat parameters for a product of interest with features as defined.
    Features should be a list of strings
    Product should be a single string
    """
    # Phase 1 (intro) should contain:
        # A warm welcome message.
        # Brief introduction to your service or product.
        # Key value proposition.
        # Clear call-to-action (CTA) for a simple action (e.g., visit the website, sign up for more information).
        # Tone: Friendly, inviting, and engaging.

    # Phase 2 and 3 should contain:
        # Objective: Provide valuable information and build trust.
        # Content: Educational content relevant to the recipient’s interests (articles, guides, tutorials).
        # Insights about how your product/service can solve a problem.
        # Social proof (testimonials, case studies, reviews).
        # Soft CTAs (e.g., read more, learn how, download a resource).
        # Tone: Informative and helpful.

    # Phase 4 and 5. Later Messages: Conversion and Commitment
        # Objective: Drive conversion and commitment.
        # Content:
        # Strong value propositions and benefits.
        # Detailed product/service information.
        # Limited-time offers or urgency-driven messages.
        # Clear, direct CTAs (e.g., purchase now, sign up, start free trial).
        # Tone: Persuasive and assertive.

    prompt = f"You are a professional and experienced customer service representative that introduces customers to technology.\
             You are specialized in the {product}, which has the following features: {features}. WRITE IN A FRIENDLY AND CONVERSATIONAL TONE.\
             WRITE THE MESSAGE IN {language}. If the language is gendered, reference the product and brand in the masculine. The URL link and description pairs that you have available to use are: {callToAction}."

    if phase == "Phase 1":
        labor = f"TASK: Find out if the customer has looked into automating the process. This is the only task\
                GUIDELINES: YOU MUST USE UP TO MAXIMUM OF 8 WORDS LIMIT FOR THE ENTIRE MESSAGE. DO NOT GREET THE CUSTOMER."

    elif phase == "Phase 2" :
        labor = f"TASK: Find out if the customer has looked into approaching the pain point with software. This is the only task\
                GUIDELINES:YOU MUST USE UP TO MAXIMUM OF 8 WORDS LIMIT FOR THE ENTIRE MESSAGE. DO NOT GREET THE CUSTOMER."

    elif phase == "Phase 3" or phase == "Phase 4":
        labor = f"TASK: Find out if the customer would like to learn more about how to automate the process. This is the only task\
                GUIDELINES:YOU MUST USE UP TO MAXIMUM OF 8 WORDS LIMIT FOR THE ENTIRE MESSAGE. DO NOT GREETTHE CUSTOMER."

    elif phase == "Phase 5":
        labor = f"TASK: State to the customer to let you know if there is someone else you can reach out to to solve the pain point. THIS IS THE ONLY TASK.\
                Example FOR TONE AND CONTENT: If there is someone else in your organization responsible for addressing this pain point, please let me know, and I’d be happy to reach out to them directly. GUIDELINES:YOU MUST USE UP TO MAXIMUM OF 30 WORDS LIMIT FOR THE ENTIRE MESSAGE. DO NOT GREET THE CUSTOMER."

    return prompt, labor


def subjectLine(phase:str, product:str, target_audience:str, target_industry:str, features:list, language:str, characterLimit:str) -> str:
    # Phase 2 and 3 should contain:
        # Objective: Provide valuable information and build trust.
        # Content: Educational content relevant to the recipient’s interests (articles, guides, tutorials).
        # Insights about how your product/service can solve a problem.
        # Social proof (testimonials, case studies, reviews).
        # Soft CTAs (e.g., read more, learn how, download a resource).
        # Tone: Informative and helpful.

    # Phase 4 and 5. Later Messages: Conversion and Commitment
        # Objective: Drive conversion and commitment.
        # Content:
        # Strong value propositions and benefits.
        # Detailed product/service information.
        # Limited-time offers or urgency-driven messages.
        # Clear, direct CTAs (e.g., purchase now, sign up, start free trial).
        # Tone: Persuasive and assertive.
    
    prompt = f"You are a professional and experienced customer service representative that introduces customers to technology.\
             You are specialized in the {product}, which has the following features: {features}.\
             WRITE THE MESSAGE IN {language}. If the language is gendered, reference the product and brand in the masculine."
    
    if phase == "Phase 1":
        labor = f"First: Use 4 Words to Greet the Customer, rephrasing Hi NAME: Meet BRAND \
                  YOU MUST ADHERE TO THE MAXIMUM OF 8 WORDS LIMIT FOR THE ENTIRE MESSAGE."

    elif phase == "Phase 2" or phase == "Phase 3":
        labor = f"First: Use 4 Words to Greet the Customer, rephrasing Hi NAME: Meet BRAND, Just Following Up \
                  YOU MUST ADHERE TO THE MAXIMUM OF 8 WORDS LIMIT FOR THE ENTIRE MESSAGE."

    elif phase == "Phase 4":
        labor = f"First: Use 4 Words to Greet the Customer, rephrasing Hi NAME: Meet BRAND, Just Following Up \
                  YOU MUST ADHERE TO THE MAXIMUM OF 8 WORDS LIMIT FOR THE ENTIRE MESSAGE."

    elif phase == "Phase 5":
        labor = f"First: Use 4 Words to Greet the Customer, rephrasing Hi NAME: Meet BRAND, Just Following Up \
                  YOU MUST ADHERE TO THE MAXIMUM OF 8 WORDS LIMIT FOR THE ENTIRE MESSAGE."
    
    return prompt, labor


def greeting(phase:str, product:str, target_audience:str, target_industry:str, features:list, language:str, characterLimit:str) -> str:
    # Phase 1 (intro) should contain:
        # A warm welcome message.
        # Brief introduction to your service or product.
        # Key value proposition.
        # Clear call-to-action (CTA) for a simple action (e.g., visit the website, sign up for more information).
        # Tone: Friendly, inviting, and engaging.

    # Phase 2 and 3 should contain:
        # Objective: Provide valuable information and build trust.
        # Content: Educational content relevant to the recipient’s interests (articles, guides, tutorials).
        # Insights about how your product/service can solve a problem.
        # Social proof (testimonials, case studies, reviews).
        # Soft CTAs (e.g., read more, learn how, download a resource).
        # Tone: Informative and helpful.

    # Phase 4 and 5. Later Messages: Conversion and Commitment
        # Objective: Drive conversion and commitment.
        # Content:
        # Strong value propositions and benefits.
        # Detailed product/service information.
        # Limited-time offers or urgency-driven messages.
        # Clear, direct CTAs (e.g., purchase now, sign up, start free trial).
        # Tone: Persuasive and assertive.

    prompt = f"You are a professional and experienced customer service representative that introduces customers to technology.\
         You are specialized in the {product}, which has the following features: {features}.\
         GUIDELINE: WRITE THE MESSAGE IN {language}. If the language is gendered, reference the product and brand in the masculine."

    if phase == "Phase 1" or phase == "Phase 2" or phase == "Phase 3" or phase == "Phase 4" or phase == "Phase 5":
        labor = f"TASK: Greet the customer using 1 word. Thats the only task."
    
    # elif phase == "Phase 4":
    #     labor = f"TASK: State how intent you are on helping {target_audience} solve the pain point. Use 1 sentence and a maximum of 15 words. DO NOT PROVIDE ANY SOLUTION NOR MENTION THE PRODUCT. That's the only task. "

    # elif phase == "Phase 5":
    #     labor = f"TASK: Acknowledge how busy {target_audience} professionals in the {target_industry} industry are. State that this is the final follow up. Use 2 sentences and a Maximum of 15 words. DO NOT PROVIDE ANY SOLUTION NOR MENTION THE PRODUCT. That's the only task. "
    
    return prompt, labor


def chatOutput(client, prompt:str, labor:str, pain:str=None) -> str:
    """
    Generates an output from GPT4 with a predefined prompt, labor and pain.
    All of these will be pregenerated by extractPointsHooks and getChatParams.
    """
    if pain is not None:
        painPointText = f"PainPoint: {pain}"
        messages=[
          {"role": "system", "content": f"{prompt}\n{labor}"},
          {"role": "user", "content": f"\n{painPointText}\n"}
        ]
        
    else:
        messages=[
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

# Function to call LLM and stream results
def handle_submission(pain_point, phase, flag):
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
        "language":st.session_state.language,
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
            # result += line.decode('utf-8') + "\n"
        return result

# Product name input in the first column
def submit_product_name():
    st.session_state.product_name = st.session_state.temp_product_name

# Call to action links input in the second column
def add_call_to_action():
    cta_input = st.session_state.temp_call_to_action
    if cta_input:
        link = st.session_state.temp_call_to_action
        desc = st.session_state.temp_call_to_action_desc
        st.session_state.call_to_actions.append((link, desc))
        st.session_state.temp_call_to_action = ""
        st.session_state.temp_call_to_action_desc = ""
        
def add_pain_point():
    pain_point_input = st.session_state.temp_pain_point
    if pain_point_input:
        st.session_state.pain_points.append(pain_point_input)
        st.session_state.temp_pain_point = ""

def add_target_audience():
    target_audience_input = st.session_state.temp_target_audience
    if target_audience_input:
        st.session_state.target_audience = target_audience_input
        # st.session_state.temp_target_audience = ""

def add_target_industry():
    target_industry_input = st.session_state.temp_target_industry
    if target_industry_input:
        st.session_state.target_industry = target_industry_input
        # st.session_state.temp_target_industry = ""

def add_feature():
    feature_input = st.session_state.temp_feature
    if feature_input:
        st.session_state.features.append(feature_input)
        st.session_state.temp_feature = ""

def clear_call_to_actions():
    st.session_state.call_to_actions = []

def clear_pain_points():
    st.session_state.pain_points = []

def clear_features():
    st.session_state.features = []

def generate_phase_content():
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
            # Parse the content_key to extract phase, pain_point, and flag
            parts = content_key.split('_')
            pain_point = '_'.join(parts[:-3])  # Assuming pain_point can contain underscores
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

                # Create the text area and pass the callback function
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

def submit_phase(phase):
    st.session_state.current_phase += 1
    if not st.session_state.current_phase < len(st.session_state.selected_phases):
        submit_campaign()
        st.session_state.generated = False


# Function to send campaign to Back end
def submit_campaign_data(campaignData):
    req = requests.post(url=f"{backend_url}/variables", json=campaignData, headers={"Authorization": f"Bearer {auth.get_auth_idtoken()}"})
    st.write("Upload Request Submitted to API:", req)
    st.write(req.text)

    return req

def submit_campaign():
    cleaned_content = []

    for phase, phase_content in st.session_state.content.items():
        for key, value in phase_content.items():
            if value:
                parts = key.split('_')
                pain_point_key = parts[0]
                cleaned_content.append({"Phase":phase, "Pain Point":pain_point_key, parts[1]: value})
    
    clean_df = pd.DataFrame(cleaned_content
        ).replace({np.nan:""}
        ).groupby(["Phase","Pain Point"]
        ).agg(lambda col: "".join(col)
        ).reset_index()

    
    campaign_data = {        
        "Product": st.session_state.product_name,
        "Platform": st.session_state.platform,
        "OwnerEmail":st.session_state.username,
        "rawData":clean_df.to_dict()
    }

    submit_campaign_data(campaign_data)

    st.write(clean_df)

    st.session_state.content = {}
    st.session_state.current_phase = 0
    st.session_state.generated = False
