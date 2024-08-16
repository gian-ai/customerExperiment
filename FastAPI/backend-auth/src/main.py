from fastapi import FastAPI, Request
from pydantic import BaseModel
from google.cloud import firestore
from google.oauth2 import service_account
import src.helpers.mdpFirestore as mdp
import src.helpers.auth as auth
import pandas as pd
from urllib.error import HTTPError
import json

path1 = "secrets/bigQuery.json"
with open(path1) as jsonFile:
    gcp_cred = json.load(jsonFile)

path2 = "secrets/projectSpecs.json"
with open(path2) as jsonFile:
    projectSpecs = json.load(jsonFile)

credentials = service_account.Credentials.from_service_account_info(gcp_cred)
db = firestore.Client(project=projectSpecs["projectID"], credentials=credentials)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Ciao bella."}


@app.get("/users")
async def checkUser(email: str, password: str):
    """
    Check if a user with the provided email and password exists in the Firestore database.

    Parameters:
    - email: User's email address.
    - password: User's password.

    Returns:
    - User details if the user exists; otherwise, an appropriate response indicating the user does not exist.
    """
    check = auth.checkUser(db, email, password)
    return check


@app.post("/users")
async def createUser(email: str, password: str):
    """
    Create a new user in the Firestore database using the provided email and password.

    Parameters:
    - email: Email address for the new user.
    - password: Password for the new user.

    Returns:
    - Details of the newly created user.
    """
    newUser = auth.createUser(db, email, password)
    return newUser


@app.get("/customers")
async def getCustomers(inactiveOnly: str = "False", platform: str | None = None, country: str | None = None, custRole: str | None = None):
    """
    Retrieve customer data from the Firestore database based on various filters.

    Parameters:
    - inactiveOnly: Filter to include only inactive customers.
    - platform: Filter by platform.
    - country: Filter by country.
    - custRole: Filter by customer role.

    Returns:
    - A list of customers that match the provided filters.
    """
    cust = mdp.getCustomers(db, inactiveOnly=inactiveOnly, custRole=custRole, platform=platform, country=country)
    return cust


@app.get("/variablegenerators")
async def getVarGens(ownerEmail: str, platform: str | None = None, phase: str | None = None):
    """
    Retrieve variable generators from the Firestore database based on the owner's email and optional filters.

    Parameters:
    - ownerEmail: The email of the owner of the variable generators.
    - platform: Optional filter by platform.
    - phase: Optional filter by phase.

    Returns:
    - Data related to the variable generators that match the provided filters.
    """
    try:
        data = mdp.getVariableGenerators(db, ownerEmail, platform, phase)
        return data
    except Exception as e:
        return f"Import failed: {e}"


@app.get("/agenda")
async def getAgenda(ownerEmail: str, platform: str | None = None):
    """
    Retrieve agenda items from the Firestore database based on the owner's email and optional platform filter.

    Parameters:
    - ownerEmail: The email of the owner of the agenda items.
    - platform: Optional filter by platform.

    Returns:
    - Data related to the agenda items that match the provided filters.
    """
    try:
        data = mdp.getAgenda(db, ownerEmail, platform)
        return data
    except Exception as e:
        return f"Import failed: {e}"


@app.get("/variables")
async def lookupVariablesByVarGen(variableGeneratorID: int):
    """
    Lookup variables by variable generator ID.

    Parameters:
    - variableGeneratorID: The ID of the variable generator.

    Returns:
    - A dictionary containing the variables associated with the variable generator.
    """
    variables = mdp.lookupVariablesByVarGen(db, variableGeneratorID)
    return {"variables": variables}


@app.get("/experimentgenerators")
async def getExpGenerators(ownerEmail: str, platform: str | None = None):
    """
    Retrieve experiment generators based on the owner's email and optional platform filter.

    Parameters:
    - ownerEmail: The email of the owner of the experiment generators.
    - platform: Optional filter by platform.

    Returns:
    - Data related to the experiment generators that match the provided filters.
    """
    print("At the first step in the endpoint:", ownerEmail, platform)
    if platform is not None:
        print("Platform is not None.")
        expGens = mdp.getExperimentGenerators(db, ownerEmail, platform)
    else:
        expGens = mdp.getExperimentGenerators(db, ownerEmail)
    return expGens


@app.get("/experiments")
async def getExperiments(ownerEmail: str, experimentGeneratorIDs: str):
    """
    Retrieve experiments based on the owner's email and a list of experiment generator IDs.

    Parameters:
    - ownerEmail: The email of the owner of the experiments.
    - experimentGeneratorIDs: A hyphen-separated string of experiment generator IDs.

    Returns:
    - Data related to the experiments that match the provided IDs.
    """
    print("At the first step in the endpoint:", experimentGeneratorIDs)
    expGenIDs = experimentGeneratorIDs.split("-")
    experiments = mdp.getExperiments(db, ownerEmail, expGenIDs)
    return experiments


@app.get("/experiments/contacts")
async def getOutboundContacts(experimentGeneratorIDs: str):
    """
    Retrieve outbound contacts based on a list of experiment generator IDs.

    Parameters:
    - experimentGeneratorIDs: A hyphen-separated string of experiment generator IDs.

    Returns:
    - Data related to the outbound contacts that match the provided IDs.
    """
    expGenIDs = experimentGeneratorIDs.split("-")
    print("At the first step in the endpoint:", expGenIDs)
    experiments = mdp.extractAllOutboundContacts(db, expGenIDs)
    return experiments


@app.get("/events")
async def getEvents():
    """
    Retrieve events from the Firestore database.

    Returns:
    - Data related to the events.
    """
    data = mdp.getEvents(db)
    return data


@app.get("/statistics")
async def getRaw(collection: str):
    """
    Retrieve raw data from a specified Firestore collection.

    Parameters:
    - collection: The name of the Firestore collection to retrieve data from.

    Returns:
    - Data from the specified Firestore collection.
    """
    data = mdp.getCollection(db, collection)
    return data


@app.post("/variables")
async def uploadVariables(rawData: dict | None = None):
    """
    Upload variables data to the Firestore database.

    Parameters:
    - rawData: A dictionary containing the raw data, platform, product, and owner email.

    Returns:
    - Success or failure message based on the operation outcome.
    """
    if rawData:
        try:
            mdp.variableImport(db, rawData["rawData"], rawData["Platform"], rawData["Product"], rawData["OwnerEmail"])
        except Exception as e:
            return f"Import failed: {e}"


@app.post("/customers")
async def uploadCustomers(rawData: dict | None = None):
    """
    Upload customer data to the Firestore database.

    Parameters:
    - rawData: A dictionary containing the raw data, platform, title, and country.

    Returns:
    - Success or failure message based on the operation outcome.
    """
    if rawData:
        try:
            print(rawData["Platform"], rawData["Title"], rawData["Country"])
            mdp.customerImport(db, rawData["rawData"], rawData["Platform"], rawData["Title"], rawData["Country"])
        except Exception as e:
            return f"Import failed: {e}"


@app.post("/experiments")
async def setupExperiments(rawData: dict | None = None):
    """
    Set up experiments based on provided data.

    Parameters:
    - rawData: A dictionary containing the variable generator IDs, trials, number of experiments, platform, country, and owner email.

    Returns:
    - Success or failure message based on the operation outcome.
    """
    resp = "Error: format input data correctly."
    
    if rawData:
        print(type(rawData["varGenIDs"]))
        if type(rawData["varGenIDs"][0]) != list:
            vGenIDs = [int(vGen) for vGen in rawData["varGenIDs"]]
            try:
                resp = mdp.fullExperimentalSetup(db, vGenIDs, rawData["trials"], rawData["numExperiments"], rawData["platform"], rawData["country"], rawData["ownerEmail"])
            except Exception as e:
                raise e
        else:
            raise ValueError("No script is selected.")


@app.post("/replaceNaN")
async def replaceNaN(collection: str):
    """
    Replace NaN values in the specified Firestore collection.

    Parameters:
    - collection: The name of the Firestore collection to replace NaN values in.

    Returns:
    - "Done" upon successful completion of the operation.
    """
    mdp.replaceNaN_db(db, [collection])
    return "Done"


@app.post("/agenda")
async def completeTask(event: dict | None = None):
    """
    Mark an agenda task as complete.

    Parameters:
    - event: A dictionary containing event details, including ownerEmail, platform, phoneNumber, email, and sequence_idx.

    Returns:
    - Data related to the completed task, or an error message if the operation fails.
    """
    event = event.get("event")
    event = json.loads(event)
    try:
        batch = db.batch()
        data = mdp.completeTask(db, batch, event.get("ownerEmail"), event.get("platform"), event.get("phoneNumber"), event.get("email"), event.get("sequence_idx"))
        if event is not None:
            eventSubmission = mdp.submitEvent(db, batch, event)
        batch.commit()
        return data
    except Exception as e:
        return f"Import failed: {e}"
