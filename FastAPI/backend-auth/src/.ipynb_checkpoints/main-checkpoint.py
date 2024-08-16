from fastapi import FastAPI, Request
from pydantic import BaseModel
from google.cloud import firestore
from google.oauth2 import service_account
import src.helpers.mdpFirestore as mdp
import src.helpers.auth as auth
import pandas as pd
import json

path="secrets/bigQuery.json"
with open(path) as jsonFile:
    gcp_cred = json.load(jsonFile)
credentials = service_account.Credentials.from_service_account_info(gcp_cred)
db = firestore.Client(project='spatial-thinker-360216', credentials=credentials)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Ciao bella."}

@app.get("/users")
async def checkUser(email:str, password:str):
    check = auth.checkUser(db, email, password)
    return check

@app.post("/users")
async def createUser(email:str, password:str):
    newUser = auth.createUser(db, email, password)
    return newUser

@app.get("/customers")
async def getCustomers(inactiveOnly:str="False", platform:str | None = None, country:str | None = None, custRole:str | None = None):
    cust = mdp.getCustomers(db, inactiveOnly=inactiveOnly, custRole=custRole, platform=platform, country=country)
    return cust

@app.get("/variablegenerators")
async def getVarGens(ownerEmail:str):
    try:
        data = mdp.getVariableGenerators(db, ownerEmail)
        return data
    except Exception as e:
        return f"Import failed: {e}"

@app.get("/experimentgenerators")
async def getExpGenerators(ownerEmail:str, platform:str|None=None):
    print("At the first step in the endpoint:", ownerEmail, platform)
    if platform is not None:
        expGens = mdp.getExperimentGenerators(db, ownerEmail, platform)
    else:
        expGen = mdp.getExperimentGenerators(db, ownerEmail)
    return expGens


@app.get("/experiments")
async def getExperiments(ownerEmail:str, experimentGeneratorIDs:str):
    print("At the first step in the endpoint:", experimentGeneratorIDs)
    expGenIDs = experimentGeneratorIDs.split("-")
    experiments = mdp.getExperiments(db, ownerEmail, expGenIDs)
    return experiments


@app.get("/experiments/contacts")
async def getOutboundContacts(experimentGeneratorIDs:str):
    expGenIDs = experimentGeneratorIDs.split("-")
    print("At the first step in the endpoint:", expGenIDs)
    experiments = mdp.extractAllOutboundContacts(db, expGenIDs)
    return experiments


@app.get("/events")
async def getEvents():
    data = mdp.getEvents(db)
    return data


@app.get("/statistics")
async def getRaw(collection: str):
    data = mdp.getCollection(db, collection)
    return data


@app.post("/variables")
async def uploadVariables(rawData:dict | None = None):
    if rawData:
        try:
            mdp.variableImport(db, rawData["rawData"], rawData["Platform"], rawData["Product"], rawData["OwnerEmail"])
        except Exception as e:
            return f"Import failed: {e}"


@app.post("/customers")
async def uploadCustomers(rawData:dict | None = None):
    if rawData:
        try:
            print(rawData["Platform"], rawData["Title"], rawData["Country"])
            mdp.customerImport(db, rawData["rawData"], rawData["Platform"], rawData["Title"], rawData["Country"])
        except Exception as e:
            return f"Import failed: {e}"


@app.post("/experiments")
async def setupExperiments(rawData:dict | None = None):
    resp = "Error: format input data correctly."
    if rawData:
        vGenIDs = [int(vGen) for vGen in rawData["varGenIDs"]]
        try:
            resp = mdp.fullExperimentalSetup(db, vGenIDs, rawData["trials"], rawData["numExperiments"], rawData["platform"], rawData["country"], rawData["ownerEmail"])
        except Exception as e:
            raise HTTPException(status_code=500, detail="Customers not found. Upload Customers.")
    


@app.post("/replaceNaN")
async def replaceNaN(collection:str):
    mdp.replaceNaN_db(db,[collection])
    return "Done"




    



