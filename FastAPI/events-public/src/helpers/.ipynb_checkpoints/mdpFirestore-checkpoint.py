import numpy as np
from copy import deepcopy
import random
import math
import pandas as pd
import collections
from google.cloud import firestore


class VariableGenerator:
    pass


class Variable: 
    def __init__(self, id:int, generatorID:int, contentA:str|None=None, contentB:str|None=None, contentC:str|None=None, contentD:str|None=None, 
                 contentE:str|None=None, painPoint:str="N/A"):
        """Useful for tracking a message and its success rate"""
        self.varID = id
        self.generatorID =  generatorID
        self.contentA = contentA
        self.contentB = contentB
        self.contentC = contentC
        self.contentD = contentD
        self.contentE = contentE
        self.painPoint = painPoint
        self.trials = 0
        self.successes = 0
        
    def declareTrial(self)->int:
        self.trials+=1
        return self.trials
    
    def declareSuccess(self)->int:
        self.successes+=1
        return self.successes

    def restore(self, trials:int, successes:int)-> None:
        self.trials = trials
        self.successes = successes
        
    def getContent(self)->str:
        return self.contentA, self.contentB, self.contentC, self.contentD, self.contentE

    def getType(self)->str:
        return self.vartype
    
    def getID(self)->int:
        return self.ID

    def getTrials(self)->int:
        return self.trials

    def getSuccesses(self)->int:
        return self.successes

    def fullDescription(self)->dict:
        contentA, contentB, contentC = self.getContent()
        d = {"ID"     : self.getID(),
             "VariableGeneratorID": self.generator.getID(),
             "ContentA": contentA,
             "ContentB": contentB,
             "ContentC": contentC,
             "ContentD": contentD,
             "ContentE": contentE,
             "Trials" : self.getTrials(),
             "Successes": self.getSuccesses()}
        return d
        
    def assignGenerator(self,varGen:VariableGenerator)->None:
        self.generator = varGen

    def reportSuccess(self):
        sr = 0 if self.trials==0 else round(self.getSuccesses()/self.getTrials(),2)
        return f"Out of {self.trials}, {self.getContent()[:10]}... has a {sr}% success rate"
        
    def __repr__(self):
        return f"{self.getType()}: {self.getID()}"


class VariableGenerator:
    def __init__(self, phase:str, product:str, owner:str, platform:str, generatorID:int, versionID:int):
        """Useful for generating messages randomly from a list of possible messages"""
        self.generatorID = generatorID
        self.phase       = phase
        self.platform    = platform
        self.product     = product 
        self.owner       = owner
        self.Bank        = set()
        self.lastVarID   = 0
        self.versionID   = versionID

    def getBank(self):
        return self.Bank

    def generateVariable(self)->str:
        """Get all messages with least trials, return random choice"""
        if not self.leastTrials:
            self.leastTrials = min([m.getTrials() for m in self.Bank])
        minTrials = [m for m in self.Bank if m.getTrials()<=self.leastTrials]

        # If all messages have been sampled more often than minTrials,
        # then randomly sample the message bank.
        if not minTrials:
            randmessage = random.sample(self.Bank,1)[0]
            return randmessage
        randmessage = random.choice(minTrials)
        return randmessage

    def checkBank(self, text:str)->bool:
        if text in [v.getContent() for v in self.getBank()]:
            return True
        else:
            return False

    def getVarByText(self, text:str)->Variable:
        for v in self.getBank():
            if v.content == text:
                return v
        return None

    def addText(self, id:int, generatorID:int, content:str, painPoint:str="")->None:
        """Add message to message bank, if it doesn't already exist.
        update least trials in message bank"""
        if not self.checkBank(text):
            var = Variable(id, generatorID, content, painPoint)
            self.Bank.add(var)
            var.assignGenerator(self)
            self.lastVarID += 1
            if self.leastTrials is None:
                self.leastTrials = 0
        else:
            print("No text has been added.")

    def restoreVariable(self, var:Variable)->None:
        self.Bank.add(var)

    def restorelastVarID(self)->None:
        lastVarID = max([var.getID() for var in self.Bank]) + 1
        self.lastVarID = lastVarID

    def dropMessage(self,var:Variable)->None:
        self.Bank.remove(var)

    def getType(self)->str:
        return self.varType

    def getID(self)->int:
        return self.ID

    def getLastVarID(self)->int:
        return self.lastVarID

    def exportVariables(self)->list:
        if self.getBank():
            return [v.fullDescription() for v in self.getBank()]
        else:
            return None

    def exportGenerator(self)->pd.DataFrame:
        data = {"ID": self.getID(),
                "GeneratorID":self.getType(),
                "LastVarID":self.getLastVarID()}
        return data

    def __repr__(self):
        return f"{self.varType} generator"


class Experiment:
    def __init__(self, experimentID:int, experimentGeneratorID:int, variableGeneratorID_1:int=None, variableGeneratorID_2:int=None,
                variableGeneratorID_3:int=None, variableGeneratorID_4:int=None, variableGeneratorID_5:int=None, variableID_1:int=None, variableID_2:int=None,
                variableID_3:int=None, variableID_4:int=None, variableID_5:int=None):
        self.experimentID = experimentID
        self.experimentGeneratorID = experimentGeneratorID
        self.variableGeneratorID_1 = None
        self.variableGeneratorID_2 = None
        self.variableGeneratorID_3 = None
        self.variableGeneratorID_4 = None
        self.variableGeneratorID_5 = None
        self.variableID_1 = None
        self.variableID_2 = None
        self.variableID_3 = None
        self.variableID_4 = None
        self.variableID_5 = None   
        self.successes = 0
        self.trials = 0

    def __eq__(self, other): 
        if not isinstance(other, Experiment):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.ID == other.ID and self.variables == other.variables and self.experimentGeneratorID == other.experimentGeneratorID

    def declareSuccess(self)->None:
        decSuc = lambda x: x.declareSuccess()
        for var in self.variables: decSuc(var)
        self.successes+=1
    
    def sample(self)->None:
        decTri = lambda x: x.declareTrial()
        for var in self.variables: decTri(var)
        self.trials+=1

    def getID(self)->int:
        return self.experimentID

    def getExperimentGeneratorID(self)->int:
        return self.experimentGeneratorID

    def getVariables(self)->list:
        return self.variables

    def getTrials(self)->int:
        return self.trials

    def restore(self, successes:int, trials:int)->None:
        self.successes = successes
        self.trials = trials

    def fullDescription(self)->dict:
        descript=dict()
        descript["experimentID"] = self.getID()
        descript["experimentGeneratorID"] = self.getExperimentGeneratorID()
        
        for i,v in enumerate(self.variables):
            vartype  = v.getType()
            varvalue = v.getID()
            descript[f"Variable {i+1} Type"]  = vartype
            descript[f"Variable {i+1} Value"] = varvalue 

        i = len(self.variables)
        while i < 5:
            descript[f"Variable {i+1} Type"]  = ""
            descript[f"Variable {i+1} Value"] = ""
            i += 1

        descript["TrialCount"]   = self.trials
        descript["SuccessCount"] = self.successes
        return descript

    def __repr__(self):
        return f"Experiment Generator {self.getExperimentGeneratorID()}: Experiment {self.getID()}"


class ExperimentGenerator:
    def __init__(self, experimentGeneratorID:int, ownerEmail:str, platform:str, variableGeneratorID_1:int=None, variableGeneratorID_2:int=None, variableGeneratorID_3:int=None, variableGeneratorID_4:int=None, variableGeneratorID_5:int=None):
        """ Useful for generating experiments with pre-configured message generators
        Stores
            - ID
            - Experiment Objects
            - Message Generators
        Generates 
            - Experiments, with random messages in them """
        self.experimentGeneratorID = experimentGeneratorID
        self.variableGeneratorID_1 = variableGeneratorID_1
        self.variableGeneratorID_2 = variableGeneratorID_2
        self.variableGeneratorID_3 = variableGeneratorID_3
        self.variableGeneratorID_4 = variableGeneratorID_4
        self.variableGeneratorID_5 = variableGeneratorID_5
        self.ownerEmail            = ownerEmail
        self.platform              = platform
        self.experiments = list()

    def getExperiments(self)->list:
        return self.experiments

    def getGenerators(self)->list:
        varGenIDs = [self.variableGeneratorID_1,
                    self.variableGeneratorID_2,
                    self.variableGeneratorID_3,
                    self.variableGeneratorID_4,
                    self.variableGeneratorID_5]
        return [varGenID for varGenID in varGenIDs if varGenID is not None]

    def getID(self)->int:
        return self.experimentGeneratorID

    def restoreExperiment(self, experiment:Experiment)->None:
        if experiment not in self.experiments:
            self.experiments.append(experiment)
    
    def exportExperiments(self)->list:
        return [exp.fullDescription() for exp in self.getExperiments()]

    def exportGenerator(self)->dict:
        data = list()
        data.append(self.getID())
        for varGenID in self.getGenerators():
            data.append(varGenID)
        while len(data) < 7:
            data.append("")
        exportFormat = ["experimentGeneratorID", "variableGeneratorID_1", "variableGeneratorID_2",\
                        "variableGeneratorID_3","variableGeneratorID_4","variableGeneratorID_5",]
        return dict(zip(exportFormat, data))
        

class Customer:
    def __init__(self, firstName:str, lastName:str | None=None, role:str | None = None, company:str| None = None, email:str| None = None, linkedInUrl:str| None = None, phoneNumber:str| None = None, leadStage:str| None = None, leadSource:str| None = None, leadStatus:str| None = None,  productOfInterest:str| None = None, country:str| None = None):
        self.firstName   = firstName
        self.lastName    = lastName
        self.role        = role
        self.company     = company
        self.email       = email
        self.linkedInUrl = linkedInUrl
        self.phoneNumber = phoneNumber
        self.leadStage   = leadStage
        self.leadSource  = leadSource
        self.leadStatus  = leadStatus
        self.productOfInterest = productOfInterest
        self.country      = country
        self.experimentID = None
        self.hasExperiment= False
        self.hasEmail     = email is not None
        self.hasLinkedIn  = linkedInUrl is not None
        self.hasPhone     = phoneNumber is not None

    def setContactInfo(self, email:str = None, 
                 linkedInUrl:str = None, phoneNumber:str = None)->None:
        if email:
            self.email       = email
        if linkedInUrl:
            self.linkedInUrl = linkedInUrl
        if phoneNumber:
            self.phoneNumber = phoneNumber
    
    def getFirstName(self)->str:
        return self.firstName

    def getLastName(self)->str:
        return self.lastName

    def getEmail(self)->str:
        if (self.email) and (self.email != None):
            return self.email
        return None

    def getLinkedInUrl(self)->str:
        if (self.linkedInUrl) and (self.linkedInUrl != None):
            return self.linkedInUrl
        return None

    def getPhoneNumber(self)->str:
        if (self.phoneNumber) and (self.phoneNumber != None):
            return self.phoneNumber
        return None

    def getRole(self)->str:
        return self.role

    def getCompany(self)->str:
        return self.company

    def getZohoInfo(self)->dict:
        d = {
            "leadStage":self.leadStage,
            "leadSource":self.leadSource,
            "leadStatus":self.leadStatus,
            "productOfInterest":self.productOfInterest,
            "country":self.country
        }
        return d

    def getContactInfo(self)->dict:
        d = {"email":self.getEmail(), 
            "linkedInUrl":self.getLinkedInUrl(),
            "phoneNumber":self.getPhoneNumber(),
            "hasEmail":self.hasEmail,
            "hasLinkedIn":self.hasLinkedIn,
            "hasPhone":self.hasPhone}
        return d

    def getExperimentInfo(self)->dict:
        d = {
            "experimentID":self.experimentID,
            "hasExperiment":self.hasExperiment
        }
        return d
    
    def fullDescription(self)->dict:
        d = dict()
        d["firstName"] = self.getFirstName()        
        d["lastName"] = self.getLastName()
        d["role"]   = self.getRole() if not pd.isnull(self.role) else None
        d["experimentID"]  = int(self.experimentID) if self.experimentID else None  
        d["company"] = self.getCompany() if not pd.isnull(self.role) else None
        d.update(self.getContactInfo())
        d.update(self.getZohoInfo())
        d.update(self.getExperimentInfo())
        return d
    
    def __repr__(self):
        return f"Customer {self.firstName, self.lastName}: Experiment {self.experimentID}"


class CustomerGenerator:
    def __init__(self):
        self.customers = list()
        self.ID = None


    def loadCustomer(self, customerDict:dict, platform:str, role:str|None = None, checkEmail:bool=False, checkLinkedIn:bool=False, checkPhone:bool=False)->Customer:
        c = customerDict
        rawCols = list(c.keys())
        
        if platform == "LinkedIn":
            firstName   = c.loc["First Name"]           
            lastName    = c.loc["Last Name"]            
            role        = c.loc["Title"]                if c.loc["Title"] else role
            company     = c.loc["Company Name"]         if c.loc["Company Name"] else None
            linkedInUrl = c.loc["Person Linkedin Url"]
            email       = c.loc["Email"]                if (checkEmail and c.loc["Email"] != 'nan') else None
            phone       = c.loc["Phone Number"]         if checkPhone else None
            country     = c.loc["Country"]
    
            cust = Customer(firstName=firstName, lastName=lastName, role=role, company=company, linkedInUrl=linkedInUrl, email=email, phoneNumber=phone, country=country) 

        elif platform == "Email":
            
            firstName   = c.loc["First Name"]           
            lastName    = c.loc["Last Name"]            
            company     = c.loc["Company"]              
            leadSource  = c.loc["Lead Source"]
            leadStage   = c.loc["Lead Stage"]
            leadStatus  = c.loc["Lead Status"]
            productOfInterest = c.loc["Product of Interest"]
            country     = c.loc["Country"]
            title = c.loc["Title"]
            spec  = c.loc["Specialty"]

            role = title if not pd.isnull(title) else ""
            role = "-".join([role, spec]) if not pd.isnull(spec) else role
            
            email       = c.loc["Email"]                if c.loc["Email"] != 'nan' else None
            linkedInUrl = c.loc["Person Linkedin Url"]  if (checkLinkedIn and c.loc["LinkedIn Url"] != 'nan') else None
            phone       = c.loc["Phone Number"]         if checkPhone else None

            
            cust = Customer(firstName=firstName, lastName=lastName, role=role, company=company, email=email, linkedInUrl=linkedInUrl, phoneNumber=phone, leadSource = leadSource, leadStage = leadStage, leadStatus = leadStatus, productOfInterest = productOfInterest, country = country)

        elif platform == "Phone":
            firstName   = c.loc["Name"]
            role        = c.loc["Role"]
            email       = c.loc["Email"]                if (checkEmail and c.loc["Email"] != 'nan') else None
            phone       = c.loc["Phone Number"]         if checkPhone else None
            country     = c.loc["Country"]
    
            cust = Customer(firstName=firstName, role=role, email=email, phoneNumber=phone, country=country) 
        
        self.customers.append(cust)
        return cust


    def getCustomers(self)->list:
        return self.customers

    
    def exportCustomers(self)->list:
        return [cust.fullDescription() for cust in self.getCustomers()]


def customerImport(dbClient, rawData, platform:str, title:str|None=None, country:str|None=None)->dict:
    checkPhone = True if platform == "Phone" else False
    checkEmail = True if platform == "Phone" or platform == "Email" else False
    checkLinkedIn = True if platform == "LinkedIn" else False

    rawDF = pd.DataFrame(rawData)
    
    if platform=="LinkedIn":    
        clean = rawDF[["profile_url","last_name","first_name","current_company","current_company_position"]]
        rename = {
        "profile_url":"Person Linkedin Url",
        "last_name":"Last Name",
        "first_name":"First Name",
        "current_company":"Company Name",
        "current_company_position":"Title" 
        }
        clean = clean.rename(columns=rename)
        clean["Title"]   = title
        clean["Country"] = country
        clean.loc[clean["Company Name"].isna(), "Company Name"] = None
    
    elif platform=="Email":
        rawCols = rawDF.keys().to_list()            
        cols = ["Email", "First Name", "Last Name", "Lead Source", 
                "Product-of-Interest-",  "Lead Status", 
                 "Title", "Specialty", "Company"]
        # Lead Stage or Record Stage
        # Country- or Country List
        
        cols.append("Country-") if "Country-" in rawCols else cols.append("Country List")
        cols.append("Lead Stage") if "Lead Stage" in rawCols else cols.append("Record Stage")
        
        clean = rawDF[cols]
        
        rename = {
            "Product-of-Interest-" : "Product of Interest",
            "Country-"     : "Country",
            "Country List" : "Country",
            "Record Stage" : "Lead Stage"
        }
        clean = clean.rename(columns=rename)
        
    elif platform=="Phone":
        columns = ["Name", "Profession", "Email", "Phone Number"] 
        clean = rawDF[columns]
        clean.loc[:,"Country"] = country
        rename = {
            "Profession" : "Role"
        }
        clean = clean.rename(columns=rename)

    clean = clean.replace({np.nan:None})

    custGen = CustomerGenerator()
    clean['custObj']= clean.apply(custGen.loadCustomer, axis=1, args=[platform, title, checkEmail, checkLinkedIn, checkPhone])
    
    # for indexing against existing customers
    if platform == "LinkedIn":
        keys=["linkedInUrl"]
    elif platform == "Email":
        keys=["email"]
    elif platform == "Phone":
        keys=["phoneNumber"]

    print(clean.head(5))

    # Upload customers into FireStore
    uploadCustomers(dbClient, custGen, keys=keys)
    countRecords(dbClient, "customers")
    
    return clean.to_dict()


def countRecords(dbClient, collection:str):
    return len(dbClient.collection(collection).get())


def dictToDocument(x, batch, collectionRef):
    doc_ref = collectionRef.document()
    batch.set(doc_ref, x.to_dict())


def compareToDatabase(upload: pd.DataFrame, dbClient, collection: str, keys: list = []):
    collectionRef = dbClient.collection(collection)
    data = [doc.to_dict() for doc in collectionRef.get()]
    if data:
        database = pd.DataFrame(data=data)
        
        for key in keys:
            existing_data = set(database[f"{key}"])
            upload = upload[~upload[f"{key}"].isin(existing_data)]
            
    if not upload.empty:
        batch = dbClient.batch()
        upload.apply(dictToDocument, axis=1, args=[batch, collectionRef])
        batch.commit()


def uploadCustomers(dbClient, custGen: CustomerGenerator, keys: list):
    upload = pd.DataFrame(custGen.exportCustomers())
    collection = "customers"
    compareToDatabase(upload, dbClient, collection, keys)


def variableImport(dbClient, rawData, platform:str|None=None, product:str|None=None, owner:str|None=None):
    df = pd.DataFrame(rawData)
    if 'Unnamed: 0' in df.keys().to_list():
        df = df.drop('Unnamed: 0', axis=1)
    
    contentA = True
    contentB = True
    
    if "contentC" in df.keys().to_list():
        contentC = True
    else:
        contentC = False
    
    for phase in df["Phase"].unique():
        a = createVariableGenerator(dbClient, phase, product, owner, platform)
        # Last 3 bools in args for uploadVariables are for flagging existence of contentA, contentB, contentC
        df[df["Phase"]==phase].apply(uploadVariables, axis=1, args=[dbClient, a["variableGeneratorID"], contentA, contentB, contentC]) 

    return df.to_dict()


def lookupVariables(experiment, varTypes):
    # Set everything to NaN if varType is not the value of the field.
    # Then drop NaN and select the remaining index of the not NaN field.
    getIndex = lambda varType: experiment.where(experiment == varType).dropna().index.values[0].split(" ")[1]

    # Using the index from the lookup of the variable type, find the value of the variable for the experiment
    getValue = lambda varType:  experiment[f"Variable {getIndex(varType)} Value"]
    
    varLookup = dict()
    for i,v in enumerate(varTypes):
        varLookup[v] = getValue(v)
    return varLookup


def createVariable(dbClient, generatorID:int, painPoint:str, contentA:str|None=None, contentB:str|None=None, contentC:str|None=None, contentD:str|None=None, contentE:str|None=None,):
    
    collection = "variables"
    data = [d.to_dict() for d in dbClient.collection(collection).get()]
    varID = 1
    if data:
        df = pd.DataFrame(data=data)
        df = df[df["variableGeneratorID"]==generatorID]
        if not df.empty:
            # Generator already has variables assigned to it
            if contentA != None:
                checkExist = df[df["contentA"]==contentA]
            if contentB != None:
                checkExist = df[df["contentB"]==contentB]
            if contentC != None:
                checkExist = df[df["contentC"]==contentC]
            if contentD != None:
                checkExist = df[df["contentD"]==contentD]     
            if contentE != None:
                checkExist = df[df["contentE"]==contentE]     
            if checkExist.empty:  
                varID = max(df["variableID"]) + 1
            else:     
                # Generator has variables assigned
                # However, there are no variables that do not have the same content.
                return None
                
    upload = {
        "variableID": varID,
        "variableGeneratorID": generatorID,
        "painPoint": painPoint,
        "contentA": contentA,
        "contentB": contentB,
        "contentC": contentC,
        "contentD": contentD,
        "contentE": contentE
    }

    dbClient.collection(collection).add(upload)
    return upload


def uploadVariables(x, dbClient, generatorID, contentA:bool=False, contentB:bool=False, contentC:bool=False, contentD:bool=False, contentE:bool=False):
    uploadDict = {"dbClient":dbClient,
        "generatorID":generatorID,
        "painPoint":x["Pain Point"]
    }
    if contentA:
        uploadDict.update({
            "contentA":x["contentA"],
        })
    if contentB:
        uploadDict.update({
            "contentB":x["contentB"],
        })
    if contentC:
        uploadDict.update({
            "contentC":x["contentC"],
        })
    if contentD:
        uploadDict.update({
            "contentD":x["contentD"],
        })
    if contentE:
        uploadDict.update({
            "contentE":x["contentE"],
        })
    upload = createVariable(**uploadDict)


def createVariableGenerator(dbClient, phase:str, product:str, owner:str, platform:str):
    # get generatorID:int, versionID:int from database
    collection="variableGenerators"
    data = [d.to_dict() for d in dbClient.collection(collection).get()]
    
    if data:
        df = pd.DataFrame(data=data)
        generatorID = max(df["variableGeneratorID"]) + 1
        checkGen = df[(df["phase"]==f"{phase}") & \
                      (df["product"]==f"{product}") & \
                      (df["owner"]==f"{owner}") & \
                      (df["platform"]==f"{platform}")]
        if not checkGen.empty:
            versionID = max(checkGen["versionID"]) + 1
        else:
            versionID = 1
    else:
        generatorID = 1
        versionID   = 1

    upload = {
        "phase":phase,
        "product":product,
        "owner":owner,
        "platform":platform,
        "variableGeneratorID":generatorID,
        "versionID":versionID
    }

    dbClient.collection(collection).add(upload)
    return upload


def createExpGen(dbClient, varGenIDs:list, platform:str, ownerEmail:str)->dict:
    platform_filter = firestore.FieldFilter("platform", "==", platform)
    
    rawDataExpGen = dbClient.collection("experimentGenerators").where(
        filter=platform_filter).get()
    rawData = [d.to_dict() for d in rawDataExpGen]

    
    expGen = pd.DataFrame(rawData)
    varGenDict = dict()
    
    if not expGen.empty:
        expGenID = max(expGen["experimentGeneratorID"].values) + 1
    else:
        expGenID = 1

    numVars = len(varGenIDs)
    # First, make a list of all experiment generators that have 
    # the same number of variable generators.
    sameSizeExpGen = [d for d in rawData if len(d.keys())-3 == numVars]
    expGen = pd.DataFrame(sameSizeExpGen)

    
    
    # Check if each there any experiment geenrators that are a 1:1 match
    for i, varGenID in enumerate(varGenIDs):
        if not expGen.empty: 
            expGen = expGen[expGen[f"variableGeneratorID_{i+1}"] == varGenID]
        varGenDict[f"variableGeneratorID_{i+1}"] = varGenID
    
    if not expGen.empty:
        print("Existing experiment generator found.")
        expGenInfo = expGen.iloc[0].to_dict()
        return expGenInfo
    
    else:
        if checkExpGenValid(dbClient, varGenIDs):
            expGenInfo = {"experimentGeneratorID":int(expGenID),
                          "ownerEmail":ownerEmail,
                          "platform":platform}
            expGenInfo.update(varGenDict)
            
            dbClient.collection("experimentGenerators").add(expGenInfo)
            return expGenInfo


def checkExpGenValid(dbClient, varGenIDs:list)->bool:    
    # Check that each of the variable generators exists
    vGen = pd.DataFrame([d.to_dict() for d in dbClient.collection("variableGenerators").get()])
    vGen[vGen["variableGeneratorID"].isin(varGenIDs)]
    
    check = (len(vGen.index) == len(varGenIDs))

    # Check that each of the variable generators contains atleast 1 variable
    variables = pd.DataFrame([d.to_dict() for d in dbClient.collection("variables").get()])
    
    for vGenID in varGenIDs:
        vCheck = variables[variables["variableGeneratorID"] == int(vGenID)]
        check = (not vCheck.empty)

    return check


def getVarBank(dbClient, expGen:ExperimentGenerator):
    # Get the list of variables for each variable generator
    numVariables = len(expGen.getGenerators())
    variables    = pd.DataFrame([d.to_dict() for d in dbClient.collection("variables").get()])
    varBank      = collections.defaultdict(list)
    for i,varGenID in enumerate(expGen.getGenerators()):
        varBank[f"variableGeneratorID_{i+1}"] = varGenID
        varBank[f"variableID_{i+1}_Bank"] = (variables[variables["variableGeneratorID"]==varGenID]["variableID"].values)
    return varBank


def createExperiment(dbClient, expGen:ExperimentGenerator, varBank:dict, ownerEmail:str)->int:
    """
    Generate a set of variables from the variable generator.
    If the set of variables is already being used on an experiment,
    then return the existing experimentID. 
    Else, create and upload an experiment, return the new experiment ID. 
    """

    rawData = dbClient.collection("experiments")

    if ownerEmail is not None:
        ownerFilter = firestore.FieldFilter("ownerEmail", "==", ownerEmail)
        rawData = rawData.where(filter=ownerFilter)
    
    if expGen.getID() is not None:
        expGenFilter = firestore.FieldFilter("experimentGeneratorID", "==", int(expGen.getID()))
        rawData = rawData.where(filter=expGenFilter)

    data = [d.to_dict() for d in rawData.get()]
    numVariables = int((len(varBank.keys()))/2)

    experiments = pd.DataFrame([d for d in data if (len(d.keys())-3)/2 == numVariables])

    print(len(experiments.index))
    
    expID = 1
    
    if (not experiments.empty):
        expID = max(experiments["experimentID"].values) + 1

    # Generate a combination for an experiment
    expDict = dict()
    expDict["ownerEmail"] = ownerEmail
    
    for i in range(1,numVariables+1):
        varGenID = int(varBank[f"variableGeneratorID_{i}"])
        varID    = int(random.choice(varBank[f"variableID_{i}_Bank"]))        
        
        expDict[f"variableGeneratorID_{i}"] = varGenID
        expDict[f"variableID_{i}"]          = varID
        
        if (not experiments.empty): 
            experiments = experiments[experiments[f"variableGeneratorID_{i}"] == varGenID]

        if (not experiments.empty): 
            experiments = experiments[experiments[f"variableID_{i}"] == varID]        
    
    if (not experiments.empty):
        expID = int(experiments["experimentID"].values[0])
    
    else:
        expDict["experimentGeneratorID"] = int(expGen.getID())
        expDict["experimentID"]          = int(expID)
        dbClient.collection("experiments").add(expDict)

    return expID


def getCustomers(dbClient, custRole:str=None, platform:str=None, country:str=None, inactiveOnly:str="False")->pd.DataFrame:
    customers = dbClient.collection("customers")

    if inactiveOnly == "True":
        experiment_filter = firestore.FieldFilter("hasExperiment", "==", False)
        customers = customers.where(filter=experiment_filter)
    
    if custRole is not None:
        role_filter = firestore.FieldFilter("role", "==", custRole)
        customers = customers.where(filter=role_filter)
    
    if country is not None:
        country_filter = firestore.FieldFilter("country", "==", country)
        customers = customers.where(filter=country_filter)        

    if platform is not None:    
        if platform == "LinkedIn":
            platform_filter = firestore.FieldFilter("hasLinkedIn", "==", True)
        elif platform == "Email":
            platform_filter = firestore.FieldFilter("hasEmail", "==", True)
        customers = customers.where(filter=platform_filter)
    
    try:
        customer_data = customers.get()
    except Exception as e:
        print(f"Error retrieving customer data: {e}")
        return None

    numCust = len(customer_data)
    if numCust > 0:
        print(numCust)
        customers_export = [d.to_dict() for d in customer_data]
        return {"customers": customers_export}
    else:
        return None


def replaceNaN_single(d):
    for key, value in d.items():
        if value in ["N/A", "NaN", float('inf'), float('-inf')]:
            d[key] = None
        elif pd.isna(value):  # Check for NaN
            d[key] = None
    return d


def replaceNaN_db(dbClient, collections:list)->pd.DataFrame:
    for collection in collections:
        docs = dbClient.collection(collection)
        docSnapshots = docs.get()
    
        for docSnapshot in docSnapshots:
            docInfo = replaceNaN_single(docSnapshot.to_dict())
            docSnapshot.reference.set(docInfo, merge=True)

    return f"Done with {len(collections)} collections."
        

def checkCustomers(customers:pd.DataFrame, requestedCustomers:int)->bool:
    return len(customers.index) >= requestedCustomers

###################################################

# def assignExperiment(x, dbClient, expID:int, expGenID:int, platform:str):
#     if platform == "LinkedIn":
#         key = x.to_dict()["linkedInUrl"]
#         linkedIn_filter=firestore.FieldFilter("linkedInUrl","==",key)
        
#         cust = dbClient.collection("customers").where(filter=linkedIn_filter)
#         custRef = cust.get()[0].reference
#         _expID, _expGenID = int(expID), int(expGenID)
#         custRef.set({"experimentID":_expID, "experimentGeneratorID":_expGenID,"hasExperiment":True}, merge=True)
    
#     elif platform == "Email":
#         key = x.to_dict()["email"]
#         email_filter = firestore.FieldFilter("email","==",key)

#         cust = dbClient.collection("customers").where(filter=email_filter)
#         custRef = cust.get()[0].reference
#         _expID, _expGenID = int(expID), int(expGenID)
#         custRef.set({"experimentID":_expID, "experimentGeneratorID":_expGenID, "hasExperiment":True}, merge=True)


# def getActiveCustomers(dbClient, expID:int, expGenID:int)->dict:
#     experiment_filter    = firestore.FieldFilter("experimentID","==",expID)
#     experimentGen_filter = firestore.FieldFilter("experimentGeneratorID","==",expGenID)
    
#     activeCustomers = dbClient.collection("customers").where(
#         filter=experiment_filter).where(
#         filter=experimentGen_filter).get()
    
#     if activeCustomers:
#         return [active.reference for active in activeCustomers]
#     else: 
#         return None
    

# def assignContentToCustomers(dbClient, expID:int, expGenID:int)->dict:
#     activeCustomers = getActiveCustomers(dbClient, expID, expGenID)
#     experiment_filter    = firestore.FieldFilter("experimentID","==",expID)
#     experimentGen_filter = firestore.FieldFilter("experimentGeneratorID","==",expGenID)
#     if activeCustomers is not None:
#         data = dbClient.collection("experiments").where(
#             filter = experiment_filter).where(
#             filter = experimentGen_filter).get()[0]
#         if data: 
#             expInfo = data.to_dict()
#         else:
#             return None
            
#         numVariables = int((len(expInfo.keys())-2)/2)
#         varContent   = dict()
        
#         for i in range(1,numVariables+1):
#             varGenID = expInfo[f"variableGeneratorID_{i}"]
#             varID    = expInfo[f"variableID_{i}"] 

#             varGen_filter = firestore.FieldFilter("variableGeneratorID","==",varGenID)
#             varID_filter  = firestore.FieldFilter("variableID","==",varID)
            
#             var = dbClient.collection("variables").where(
#                 filter=varGen_filter).where(
#                 filter=varID_filter).get()

#             content = var[0].to_dict()
#             contentA = content["contentA"]
#             contentB = content["contentB"]
#             contentC = content["contentC"]
#             contentD = content["contentD"]
#             contentE = content["contentE"]

#             if contentA != None:
#                 varContent[f"content_{i}_A"] = contentA
#             if contentB != None:
#                 varContent[f"content_{i}_B"] = contentB
#             if contentC != None:
#                 varContent[f"content_{i}_C"] = contentC
#             if contentD != None:
#                 varContent[f"content_{i}_D"] = contentD
#             if contentE != None:
#                 varContent[f"content_{i}_E"] = contentE

#         for active in activeCustomers:
#             active.set(varContent, merge=True)
            
#         return activeCustomers
    
#     else:
#         return None

    
# def getExperiments(dbClient, ownerEmail, experimentGeneratorID) -> dict:
#     if type(experimentGeneratorID) is not list:
#         experimentGeneratorID = list(experimentGeneratorID)

#     experiments = []

#     print(f"These are the experiment Generator IDs {experimentGeneratorID}")
#     for expGenID in experimentGeneratorID: 
        
#         rawData = dbClient.collection("experiments")
    
#         if ownerEmail is not None:
#             ownerFilter = firestore.FieldFilter("ownerEmail", "==", ownerEmail)
#             rawData = rawData.where(filter=ownerFilter)
        
#         if expGenID is not None:
#             expGenFilter = firestore.FieldFilter("experimentGeneratorID", "==", int(expGenID))
#             rawData = rawData.where(filter=expGenFilter)
    
#         data = rawData.get()
        
#         if data:
            
#             for d in data:
#                 if d:
#                     expInfo = d.to_dict()
#                 else:
#                     return None
    
#                 numVariables = int((len(expInfo.keys()) - 2) / 2)
#                 varContent = {"experimentGeneratorID": int(expGenID),
#                               "experimentID": expInfo["experimentID"]}
    
#                 for i in range(1, numVariables + 1):
#                     varGenID = expInfo[f"variableGeneratorID_{i}"]
#                     varID = expInfo[f"variableID_{i}"]
    
#                     varGen_filter = firestore.FieldFilter("variableGeneratorID", "==", varGenID)
#                     varID_filter = firestore.FieldFilter("variableID", "==", varID)
    
#                     var = dbClient.collection("variables").where(filter=varGen_filter).where(filter=varID_filter).get()
    
#                     if var:
#                         content = var[0].to_dict()
#                         for suffix in ["A", "B", "C", "D", "E"]:
#                             content_key = f"content{suffix}"
#                             if content.get(content_key) is not None:
#                                 varContent[f"content_{i}_{suffix}"] = content[content_key]
                        
#                         varContent[f"variableGeneratorID_{i}"] = varGenID
#                         varContent[f"variableID_{i}"] = varID

    
#                 experiments.append(deepcopy(varContent))
#         print(f"Experiment generator {expGenID} has {len(data)} experiments.\n")        

#     if experiments:
#         return experiments
#     else:
#         return None

    
# def fullExperimentalSetup(dbClient, varGenIDs:list, trials:int=5, numExperiments:int=5, platform:str|None=None, country:str|None=None, ownerEmail:str|None=None):
#     expGenInfo = createExpGen(dbClient, varGenIDs=varGenIDs, platform=platform, ownerEmail=ownerEmail)
#     expGen = ExperimentGenerator(**expGenInfo)
#     varBank = getVarBank(dbClient, expGen)    
#     assert country is not None
#     rawDataCust = getCustomers(dbClient, platform=platform, country=country, inactiveOnly="True")
#     cust = pd.DataFrame(rawDataCust["customers"])
#     print(f"Customers available: {len(cust.index)}")
    
#     experiments = set()
    
#     while checkCustomers(cust, trials) and numExperiments:
#         numExperiments -= 1
#         expID  = createExperiment(dbClient, expGen, varBank, ownerEmail)
#         expGenID = expGen.getID()
#         experiments.add(expID)
        
#         trial_cust = cust.sample(n=trials)
#         trial_cust.apply(assignExperiment,axis=1, args=[dbClient, expID, expGenID, platform])
#         assignContentToCustomers(dbClient, int(expID), int(expGenID))
        
#         if platform == "Email":
#             cust = cust[~cust["email"].isin(trial_cust["email"])]
#         elif platform == "LinkedIn":
#             cust = cust[~cust["linkedInUrl"].isin(trial_cust["linkedInUrl"])]


def assignExperiment(x, batch, dbClient, expID: int, expGenID: int, platform: str):
    if platform == "LinkedIn":
        key = x.to_dict()["linkedInUrl"]
        linkedIn_filter = firestore.FieldFilter("linkedInUrl", "==", key)
        
        cust = dbClient.collection("customers").where(filter=linkedIn_filter).get()
        if cust:
            custRef = cust[0].reference
            _expID, _expGenID = int(expID), int(expGenID)
            batch.set(custRef, {"experimentID": _expID, "experimentGeneratorID": _expGenID, "hasExperiment": True}, merge=True)
    
    elif platform == "Email":
        key = x.to_dict()["email"]
        email_filter = firestore.FieldFilter("email", "==", key)

        cust = dbClient.collection("customers").where(filter=email_filter).get()
        if cust:
            custRef = cust[0].reference
            _expID, _expGenID = int(expID), int(expGenID)
            batch.set(custRef, {"experimentID": _expID, "experimentGeneratorID": _expGenID, "hasExperiment": True}, merge=True)


def getActiveCustomers(dbClient, expID: int, expGenID: int) -> dict:
    experiment_filter = firestore.FieldFilter("experimentID", "==", expID)
    experimentGen_filter = firestore.FieldFilter("experimentGeneratorID", "==", expGenID)
    
    activeCustomers = dbClient.collection("customers").where(filter=experiment_filter).where(filter=experimentGen_filter).get()
    
    if activeCustomers:
        return [active.reference for active in activeCustomers]
    else: 
        return None


def assignContentToCustomers(dbClient, expID: int, expGenID: int) -> dict:
    activeCustomers = getActiveCustomers(dbClient, expID, expGenID)
    experiment_filter = firestore.FieldFilter("experimentID", "==", expID)
    experimentGen_filter = firestore.FieldFilter("experimentGeneratorID", "==", expGenID)
    
    if activeCustomers is not None:
        data = dbClient.collection("experiments").where(filter=experiment_filter).where(filter=experimentGen_filter).get()
        if data: 
            expInfo = data[0].to_dict()
        else:
            return None
            
        numVariables = int((len(expInfo.keys()) - 2) / 2)
        varContent = dict()
        
        for i in range(1, numVariables + 1):
            varGenID = expInfo[f"variableGeneratorID_{i}"]
            varID = expInfo[f"variableID_{i}"] 

            varGen_filter = firestore.FieldFilter("variableGeneratorID", "==", varGenID)
            varID_filter = firestore.FieldFilter("variableID", "==", varID)
            
            var = dbClient.collection("variables").where(filter=varGen_filter).where(filter=varID_filter).get()

            if var:
                content = var[0].to_dict()
                for suffix in ["A", "B", "C", "D", "E"]:
                    content_key = f"content{suffix}"
                    if content.get(content_key) is not None:
                        varContent[f"content_{i}_{suffix}"] = content[content_key]

        batch = dbClient.batch()
        for active in activeCustomers:
            batch.set(active, varContent, merge=True)
        batch.commit()
        
        return activeCustomers
    
    else:
        return None


def getExperiments(dbClient, ownerEmail, experimentGeneratorID) -> dict:
    if type(experimentGeneratorID) is not list:
        experimentGeneratorID = [experimentGeneratorID]

    experiments = []

    for expGenID in experimentGeneratorID: 
        rawData = dbClient.collection("experiments")
    
        if ownerEmail is not None:
            ownerFilter = firestore.FieldFilter("ownerEmail", "==", ownerEmail)
            rawData = rawData.where(filter=ownerFilter)
        
        if expGenID is not None:
            expGenFilter = firestore.FieldFilter("experimentGeneratorID", "==", int(expGenID))
            rawData = rawData.where(filter=expGenFilter)
    
        data = rawData.get()
        
        if data:
            for d in data:
                if d:
                    expInfo = d.to_dict()
                else:
                    continue
    
                numVariables = int((len(expInfo.keys()) - 2) / 2)
                varContent = {"experimentGeneratorID": int(expGenID),
                              "experimentID": expInfo["experimentID"]}
    
                for i in range(1, numVariables + 1):
                    varGenID = expInfo[f"variableGeneratorID_{i}"]
                    varID = expInfo[f"variableID_{i}"]
    
                    varGen_filter = firestore.FieldFilter("variableGeneratorID", "==", varGenID)
                    varID_filter = firestore.FieldFilter("variableID", "==", varID)
    
                    var = dbClient.collection("variables").where(filter=varGen_filter).where(filter=varID_filter).get()
    
                    if var:
                        content = var[0].to_dict()
                        for suffix in ["A", "B", "C", "D", "E"]:
                            content_key = f"content{suffix}"
                            if content.get(content_key) is not None:
                                varContent[f"content_{i}_{suffix}"] = content[content_key]
                        
                        varContent[f"variableGeneratorID_{i}"] = varGenID
                        varContent[f"variableID_{i}"] = varID

                experiments.append(deepcopy(varContent))

    if experiments:
        return experiments
    else:
        return None


def fullExperimentalSetup(dbClient, varGenIDs: list, trials: int = 5, numExperiments: int = 5, platform: str = None, country: str = None, ownerEmail: str = None):
    expGenInfo = createExpGen(dbClient, varGenIDs=varGenIDs, platform=platform, ownerEmail=ownerEmail)
    expGen = ExperimentGenerator(**expGenInfo)
    varBank = getVarBank(dbClient, expGen)
    
    assert country is not None
    rawDataCust = getCustomers(dbClient, platform=platform, country=country, inactiveOnly="True")
    if rawDataCust:
        cust = pd.DataFrame(rawDataCust["customers"])
        
        experiments = set()
        
        while checkCustomers(cust, trials) and numExperiments:
            numExperiments -= 1
            expID = createExperiment(dbClient, expGen, varBank, ownerEmail)
            expGenID = expGen.getID()
            experiments.add(expID)
            
            trial_cust = cust.sample(n=trials)
            batch = dbClient.batch()
            trial_cust.apply(assignExperiment, axis=1, args=[batch, dbClient, expID, expGenID, platform])
            batch.commit()
            assignContentToCustomers(dbClient, int(expID), int(expGenID))
            
            if platform == "Email":
                cust = cust[~cust["email"].isin(trial_cust["email"])]
            elif platform == "LinkedIn":
                cust = cust[~cust["linkedInUrl"].isin(trial_cust["linkedInUrl"])]
        return "Success: Experiment uploaded."
    else:
        return "Error: Upload Customers."

# Batch 
################################################################3

def getVariableGenerators(db, owner:str)->dict:
    get_data = db.collection("variableGenerators").where(filter=firestore.FieldFilter("owner","==",owner)).get()
    data = {"variableGenerators": [d.to_dict() for d in get_data] }
    if data:
        return data
    else:
        return None


def getExperimentGenerators(db, ownerEmail:str)->dict:
    get_data = db.collection("experimentGenerators").where(filter=firestore.FieldFilter("ownerEmail","==",ownerEmail)).get()
    data = {"experimentGenerators": [d.to_dict() for d in get_data] }
    if data:
        return data
    else:
        return None


def getCollection(db, collection)->dict:
    get_data = db.collection(collection).get()
    data = {collection: [d.to_dict() for d in get_data] }
    if data:
        return data
    else:
        return None


def readWithNone(path:str)->pd.DataFrame:
    checkNone = lambda x: None if x == "None" else x
    raw = pd.read_csv(path, dtype=str)
    raw = raw.applymap(checkNone)
    return raw


def extractOutbound(dbClient, expID:list)->dict:
    activeCustomers = pd.DataFrame([d.get().to_dict() for d in getActiveCustomers(dbClient, expID)])
    return activeCustomers


def extractAllOutboundContacts(dbClient, experimentGeneratorIDs) -> dict:
    if type(experimentGeneratorIDs) is not list:
        experimentGeneratorIDs = list(experimentGeneratorIDs)

    contacts = []

    print(f"These are the experiment Generator IDs {experimentGeneratorIDs}")
    for expGenID in experimentGeneratorIDs: 
        experimentGen_filter = firestore.FieldFilter("experimentGeneratorID","==",int(expGenID))
        
        activeCustomers = dbClient.collection("customers").where(
            filter=experimentGen_filter).get()
        
        if activeCustomers:
            contacts.extend([active.to_dict() for active in activeCustomers])

    return contacts
