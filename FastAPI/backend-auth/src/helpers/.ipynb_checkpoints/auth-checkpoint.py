from google.cloud import firestore
import streamlit as st

# Checks if a username / password combination is correct
def checkUser(db, email, password):
    query = db.collection("Users")
    userFilter = firestore.FieldFilter("email", "==", email)
    docs = query.where(filter=userFilter).get()
    data = [doc.to_dict() for doc in docs]
    if len(data)>0:
        return password in [d["password"] for d in data]
    return False

# Creates a new user
def createUser(db, email, password):
    query = db.collection("Users")
    userFilter = firestore.FieldFilter("email", "==", email)
    docs = query.where(filter=userFilter).get()
    data = [doc.to_dict() for doc in docs]
    if len(data)>0:
        return False
    else:
        db.collection("Users").add({"email":email, "password":password})
        return True
