from fastapi import FastAPI, Request
from pydantic import BaseModel
from google.cloud import firestore
from google.oauth2 import service_account
import json

path="secrets/bigQuery.json"
with open(path) as jsonFile:
    gcp_cred = json.load(jsonFile)
credentials = service_account.Credentials.from_service_account_info(gcp_cred)
db = firestore.Client(project='spatial-thinker-360216', credentials=credentials)

# Define Pydantic model
class EmailEvent(BaseModel):
    customerEmail: str
    postingDate: str
    status: str

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Ciao bella!"}

@app.post("/emailEvent")
async def emailActivity(newEvent: EmailEvent):
    payload = json.loads(newEvent.json())
    payload["platform"] = "Email"
    try:
        db.collection("events").add(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {e}")
    return payload

@app.post("/linkedInEvent")
async def linkedInActivity(payload:dict):
    payload["platform"]="LinkedIn"    
    try:
        db.collection("events").add(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {e}")
    return payload




    



