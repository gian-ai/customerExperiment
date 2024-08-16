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
    def __init__(self, id: int, generatorID: int, contentA: str | None = None, contentB: str | None = None, contentC: str | None = None, contentD: str | None = None, 
                 contentE: str | None = None, painPoint: str = "N/A"):
        """
        Initialize a Variable instance to track a message and its success rate.

        Parameters:
        - id: Unique identifier for the variable.
        - generatorID: ID of the generator that created this variable.
        - contentA-E: Content associated with the variable.
        - painPoint: Description of the pain point this variable addresses.
        """
        self.varID = id
        self.generatorID = generatorID
        self.contentA = contentA
        self.contentB = contentB
        self.contentC = contentC
        self.contentD = contentD
        self.contentE = contentE
        self.painPoint = painPoint
        self.trials = 0
        self.successes = 0
        
    def declareTrial(self) -> int:
        """
        Increment the trial count for this variable.

        Returns:
        - The updated trial count.
        """
        self.trials += 1
        return self.trials
    
    def declareSuccess(self) -> int:
        """
        Increment the success count for this variable.

        Returns:
        - The updated success count.
        """
        self.successes += 1
        return self.successes

    def restore(self, trials: int, successes: int) -> None:
        """
        Restore the trials and successes counts for this variable.

        Parameters:
        - trials: The number of trials to restore.
        - successes: The number of successes to restore.
        """
        self.trials = trials
        self.successes = successes
        
    def getContent(self) -> str:
        """
        Retrieve the content associated with this variable.

        Returns:
        - A tuple of the contents (contentA, contentB, contentC, contentD, contentE).
        """
        return self.contentA, self.contentB, self.contentC, self.contentD, self.contentE

    def getType(self) -> str:
        """
        Retrieve the type of the variable.

        Returns:
        - The type of the variable.
        """
        return self.vartype
    
    def getID(self) -> int:
        """
        Retrieve the ID of the variable.

        Returns:
        - The ID of the variable.
        """
        return self.varID

    def getTrials(self) -> int:
        """
        Retrieve the number of trials for this variable.

        Returns:
        - The number of trials.
        """
        return self.trials

    def getSuccesses(self) -> int:
        """
        Retrieve the number of successes for this variable.

        Returns:
        - The number of successes.
        """
        return self.successes

    def fullDescription(self) -> dict:
        """
        Provide a full description of the variable, including all its attributes.

        Returns:
        - A dictionary containing the full description of the variable.
        """
        contentA, contentB, contentC, contentD, contentE = self.getContent()
        d = {
            "ID": self.getID(),
            "VariableGeneratorID": self.generator.getID(),
            "ContentA": contentA,
            "ContentB": contentB,
            "ContentC": contentC,
            "ContentD": contentD,
            "ContentE": contentE,
            "Trials": self.getTrials(),
            "Successes": self.getSuccesses()
        }
        return d
        
    def assignGenerator(self, varGen: VariableGenerator) -> None:
        """
        Assign a generator to this variable.

        Parameters:
        - varGen: The VariableGenerator instance to assign to this variable.
        """
        self.generator = varGen

    def reportSuccess(self) -> str:
        """
        Generate a success report for this variable.

        Returns:
        - A string report detailing the success rate.
        """
        sr = 0 if self.trials == 0 else round(self.getSuccesses() / self.getTrials(), 2)
        return f"Out of {self.trials}, {self.getContent()[:10]}... has a {sr}% success rate"
        
    def __repr__(self):
        """
        Provide a string representation of the variable.

        Returns:
        - A string representing the variable.
        """
        return f"{self.getType()}: {self.getID()}"


class VariableGenerator:
    def __init__(self, phase: str, product: str, ownerEmail: str, platform: str, generatorID: int, versionID: int):
        """
        Initialize a VariableGenerator instance for generating variables (messages) randomly from a list.

        Parameters:
        - phase: The phase of the variable generator.
        - product: The product associated with the variable generator.
        - ownerEmail: The email of the owner of the variable generator.
        - platform: The platform associated with the variable generator.
        - generatorID: Unique ID of the variable generator.
        - versionID: Version ID of the variable generator.
        """
        self.generatorID = generatorID
        self.phase = phase
        self.platform = platform
        self.product = product
        self.ownerEmail = ownerEmail
        self.Bank = set()
        self.lastVarID = 0
        self.versionID = versionID

    def getBank(self):
        """
        Retrieve the bank of variables associated with this generator.

        Returns:
        - A set of variables.
        """
        return self.Bank

    def generateVariable(self) -> str:
        """
        Generate a random variable from the bank of variables, favoring those with the fewest trials.

        Returns:
        - The selected variable.
        """
        if not self.leastTrials:
            self.leastTrials = min([m.getTrials() for m in self.Bank])
        minTrials = [m for m in self.Bank if m.getTrials() <= self.leastTrials]

        if not minTrials:
            randmessage = random.sample(self.Bank, 1)[0]
            return randmessage
        randmessage = random.choice(minTrials)
        return randmessage

    def checkBank(self, text: str) -> bool:
        """
        Check if a specific text exists in the variable bank.

        Parameters:
        - text: The text to check for.

        Returns:
        - True if the text exists, False otherwise.
        """
        if text in [v.getContent() for v in self.getBank()]:
            return True
        else:
            return False

    def getVarByText(self, text: str) -> Variable:
        """
        Retrieve a variable by its text content.

        Parameters:
        - text: The text content to search for.

        Returns:
        - The variable with the matching text, or None if not found.
        """
        for v in self.getBank():
            if v.content == text:
                return v
        return None

    def addText(self, id: int, generatorID: int, content: str, painPoint: str = "") -> None:
        """
        Add a variable to the bank if it doesn't already exist.

        Parameters:
        - id: ID of the variable.
        - generatorID: ID of the generator creating the variable.
        - content: The content of the variable.
        - painPoint: The pain point the variable addresses.
        """
        if not self.checkBank(content):
            var = Variable(id, generatorID, content, painPoint)
            self.Bank.add(var)
            var.assignGenerator(self)
            self.lastVarID += 1
            if self.leastTrials is None:
                self.leastTrials = 0
        else:
            print("No text has been added.")

    def restoreVariable(self, var: Variable) -> None:
        """
        Restore a variable to the bank.

        Parameters:
        - var: The variable to restore.
        """
        self.Bank.add(var)

    def restorelastVarID(self) -> None:
        """
        Restore the last variable ID based on the variables in the bank.
        """
        lastVarID = max([var.getID() for var in self.Bank]) + 1
        self.lastVarID = lastVarID

    def dropMessage(self, var: Variable) -> None:
        """
        Remove a variable from the bank.

        Parameters:
        - var: The variable to remove.
        """
        self.Bank.remove(var)

    def getType(self) -> str:
        """
        Retrieve the type of the variable generator.

        Returns:
        - The type of the variable generator.
        """
        return self.varType

    def getID(self) -> int:
        """
        Retrieve the ID of the variable generator.

        Returns:
        - The ID of the variable generator.
        """
        return self.generatorID

    def getLastVarID(self) -> int:
        """
        Retrieve the ID of the last variable added to the bank.

        Returns:
        - The ID of the last variable.
        """
        return self.lastVarID

    def exportVariables(self) -> list:
        """
        Export all variables in the bank as a list of dictionaries.

        Returns:
        - A list of dictionaries representing the variables.
        """
        if self.getBank():
            return [v.fullDescription() for v in self.getBank()]
        else:
            return None

    def exportGenerator(self) -> pd.DataFrame:
        """
        Export the generator's information as a DataFrame.

        Returns:
        - A DataFrame containing the generator's information.
        """
        data = {
            "ID": self.getID(),
            "GeneratorID": self.getType(),
            "LastVarID": self.getLastVarID()
        }
        return data

    def __repr__(self):
        """
        Provide a string representation of the variable generator.

        Returns:
        - A string representing the variable generator.
        """
        return f"{self.varType} generator"


class Experiment:
    def __init__(self, experimentID: int, experimentGeneratorID: int, variableGeneratorID_1: int = None, variableGeneratorID_2: int = None,
                 variableGeneratorID_3: int = None, variableGeneratorID_4: int = None, variableGeneratorID_5: int = None, 
                 variableID_1: int = None, variableID_2: int = None, variableID_3: int = None, variableID_4: int = None, 
                 variableID_5: int = None):
        """
        Initialize an Experiment instance to track a specific experiment configuration.

        Parameters:
        - experimentID: Unique identifier for the experiment.
        - experimentGeneratorID: ID of the experiment generator that created this experiment.
        - variableGeneratorID_1-5: IDs of the variable generators used in this experiment.
        - variableID_1-5: IDs of the variables used in this experiment.
        """
        self.experimentID = experimentID
        self.experimentGeneratorID = experimentGeneratorID
        self.variableGeneratorID_1 = variableGeneratorID_1
        self.variableGeneratorID_2 = variableGeneratorID_2
        self.variableGeneratorID_3 = variableGeneratorID_3
        self.variableGeneratorID_4 = variableGeneratorID_4
        self.variableGeneratorID_5 = variableGeneratorID_5
        self.variableID_1 = variableID_1
        self.variableID_2 = variableID_2
        self.variableID_3 = variableID_3
        self.variableID_4 = variableID_4
        self.variableID_5 = variableID_5   
        self.successes = 0
        self.trials = 0

    def __eq__(self, other): 
        """
        Check if two experiments are equal based on their IDs and variables.

        Parameters:
        - other: Another Experiment instance to compare with.

        Returns:
        - True if the experiments are equal, False otherwise.
        """
        if not isinstance(other, Experiment):
            return NotImplemented

        return self.experimentID == other.experimentID and self.experimentGeneratorID == other.experimentGeneratorID

    def declareSuccess(self) -> None:
        """
        Declare a success for this experiment, incrementing the success count and updating the variables.
        """
        for var in self.variables:
            var.declareSuccess()
        self.successes += 1
    
    def sample(self) -> None:
        """
        Sample the experiment, incrementing the trial count and updating the variables.
        """
        for var in self.variables:
            var.declareTrial()
        self.trials += 1

    def getID(self) -> int:
        """
        Retrieve the ID of the experiment.

        Returns:
        - The ID of the experiment.
        """
        return self.experimentID

    def getExperimentGeneratorID(self) -> int:
        """
        Retrieve the ID of the experiment generator.

        Returns:
        - The ID of the experiment generator.
        """
        return self.experimentGeneratorID

    def getVariables(self) -> list:
        """
        Retrieve the variables used in the experiment.

        Returns:
        - A list of variables.
        """
        return self.variables

    def getTrials(self) -> int:
        """
        Retrieve the number of trials for this experiment.

        Returns:
        - The number of trials.
        """
        return self.trials

    def restore(self, successes: int, trials: int) -> None:
        """
        Restore the successes and trials counts for this experiment.

        Parameters:
        - successes: The number of successes to restore.
        - trials: The number of trials to restore.
        """
        self.successes = successes
        self.trials = trials

    def fullDescription(self) -> dict:
        """
        Provide a full description of the experiment, including all its attributes.

        Returns:
        - A dictionary containing the full description of the experiment.
        """
        descript = {
            "experimentID": self.getID(),
            "experimentGeneratorID": self.getExperimentGeneratorID(),
            "TrialCount": self.trials,
            "SuccessCount": self.successes
        }
        
        for i, v in enumerate(self.variables):
            vartype  = v.getType()
            varvalue = v.getID()
            descript[f"Variable {i+1} Type"]  = vartype
            descript[f"Variable {i+1} Value"] = varvalue 

        i = len(self.variables)
        while i < 5:
            descript[f"Variable {i+1} Type"]  = ""
            descript[f"Variable {i+1} Value"] = ""
            i += 1

        return descript

    def __repr__(self):
        """
        Provide a string representation of the experiment.

        Returns:
        - A string representing the experiment.
        """
        return f"Experiment Generator {self.getExperimentGeneratorID()}: Experiment {self.getID()}"


class ExperimentGenerator:
    def __init__(self, experimentGeneratorID: int, ownerEmail: str, platform: str, variableGeneratorID_1: int = None, variableGeneratorID_2: int = None, variableGeneratorID_3: int = None, variableGeneratorID_4: int = None, variableGeneratorID_5: int = None):
        """
        Initialize an ExperimentGenerator instance to generate experiments with pre-configured variable generators.

        Parameters:
        - experimentGeneratorID: Unique identifier for the experiment generator.
        - ownerEmail: Email of the owner of the experiment generator.
        - platform: Platform associated with the experiment generator.
        - variableGeneratorID_1-5: IDs of the variable generators used in this experiment generator.
        """
        self.experimentGeneratorID = experimentGeneratorID
        self.variableGeneratorID_1 = variableGeneratorID_1
        self.variableGeneratorID_2 = variableGeneratorID_2
        self.variableGeneratorID_3 = variableGeneratorID_3
        self.variableGeneratorID_4 = variableGeneratorID_4
        self.variableGeneratorID_5 = variableGeneratorID_5
        self.ownerEmail = ownerEmail
        self.platform = platform
        self.experiments = list()

    def getExperiments(self) -> list:
        """
        Retrieve the experiments generated by this generator.

        Returns:
        - A list of experiments.
        """
        return self.experiments

    def getGenerators(self) -> list:
        """
        Retrieve the variable generator IDs associated with this experiment generator.

        Returns:
        - A list of variable generator IDs.
        """
        varGenIDs = [
            self.variableGeneratorID_1,
            self.variableGeneratorID_2,
            self.variableGeneratorID_3,
            self.variableGeneratorID_4,
            self.variableGeneratorID_5
        ]
        return [varGenID for varGenID in varGenIDs if varGenID is not None]

    def getID(self) -> int:
        """
        Retrieve the ID of the experiment generator.

        Returns:
        - The ID of the experiment generator.
        """
        return self.experimentGeneratorID

    def restoreExperiment(self, experiment: Experiment) -> None:
        """
        Restore an experiment to the generator if it doesn't already exist.

        Parameters:
        - experiment: The experiment to restore.
        """
        if experiment not in self.experiments:
            self.experiments.append(experiment)
    
    def exportExperiments(self) -> list:
        """
        Export all experiments generated by this generator as a list of dictionaries.

        Returns:
        - A list of dictionaries representing the experiments.
        """
        return [exp.fullDescription() for exp in self.getExperiments()]

    def exportGenerator(self) -> dict:
        """
        Export the experiment generator's information as a dictionary.

        Returns:
        - A dictionary containing the experiment generator's information.
        """
        data = [
            self.getID()
        ]
        for varGenID in self.getGenerators():
            data.append(varGenID)
        while len(data) < 7:
            data.append("")

        exportFormat = ["experimentGeneratorID", "variableGeneratorID_1", "variableGeneratorID_2",\
                        "variableGeneratorID_3","variableGeneratorID_4","variableGeneratorID_5"]
        return dict(zip(exportFormat, data))


class Customer:
    def __init__(self, name: str | None = None, firstName: str | None = None, lastName: str | None = None, role: str | None = None, company: str | None = None, email: str | None = None, linkedInUrl: str | None = None, phoneNumber: str | None = None, leadStage: str | None = None, leadSource: str | None = None, leadStatus: str | None = None, productOfInterest: str | None = None, country: str | None = None):
        """
        Initialize a Customer instance to store customer information.

        Parameters:
        - name: Full name of the customer.
        - firstName: First name of the customer.
        - lastName: Last name of the customer.
        - role: Role of the customer.
        - company: Company associated with the customer.
        - email: Email address of the customer.
        - linkedInUrl: LinkedIn URL of the customer.
        - phoneNumber: Phone number of the customer.
        - leadStage: Lead stage of the customer.
        - leadSource: Lead source of the customer.
        - leadStatus: Lead status of the customer.
        - productOfInterest: Product of interest for the customer.
        - country: Country of the customer.
        """
        self.name = name
        self.firstName = firstName
        self.lastName = lastName
        self.role = role
        self.company = company
        self.email = email
        self.linkedInUrl = linkedInUrl
        self.phoneNumber = phoneNumber
        self.leadStage = leadStage
        self.leadSource = leadSource
        self.leadStatus = leadStatus
        self.productOfInterest = productOfInterest
        self.country = country
        self.hasEmail = email is not None
        self.hasLinkedIn = linkedInUrl is not None
        self.hasPhone = phoneNumber is not None

    def setContactInfo(self, email: str = None, 
                       linkedInUrl: str = None, phoneNumber: str = None) -> None:
        """
        Set or update the contact information of the customer.

        Parameters:
        - email: Email address to set.
        - linkedInUrl: LinkedIn URL to set.
        - phoneNumber: Phone number to set.
        """
        if email:
            self.email = email
        if linkedInUrl:
            self.linkedInUrl = linkedInUrl
        if phoneNumber:
            self.phoneNumber = phoneNumber
    
    def getName(self) -> str:
        """
        Retrieve the full name of the customer.

        Returns:
        - The full name of the customer.
        """
        name = ""
        if self.firstName: name += self.firstName
        if self.lastName: name += self.lastName 
        if self.name: name = self.name
        return name

    def getEmail(self) -> str:
        """
        Retrieve the email address of the customer.

        Returns:
        - The email address, or None if not set.
        """
        if (self.email) and (self.email != None):
            return self.email
        return None

    def getLinkedInUrl(self) -> str:
        """
        Retrieve the LinkedIn URL of the customer.

        Returns:
        - The LinkedIn URL, or None if not set.
        """
        if (self.linkedInUrl) and (self.linkedInUrl != None):
            return self.linkedInUrl
        return None

    def getPhoneNumber(self) -> str:
        """
        Retrieve the phone number of the customer.

        Returns:
        - The phone number, or None if not set.
        """
        if (self.phoneNumber) and (self.phoneNumber != None):
            return self.phoneNumber
        return None

    def getRole(self) -> str:
        """
        Retrieve the role of the customer.

        Returns:
        - The role of the customer.
        """
        return self.role

    def getCompany(self) -> str:
        """
        Retrieve the company of the customer.

        Returns:
        - The company of the customer.
        """
        return self.company

    def getZohoInfo(self) -> dict:
        """
        Retrieve the Zoho CRM information for the customer.

        Returns:
        - A dictionary containing the Zoho CRM fields.
        """
        return {
            "leadStage": self.leadStage,
            "leadSource": self.leadSource,
            "leadStatus": self.leadStatus,
            "productOfInterest": self.productOfInterest,
            "country": self.country
        }

    def getContactInfo(self) -> dict:
        """
        Retrieve the contact information of the customer.

        Returns:
        - A dictionary containing the contact information fields.
        """
        return {
            "email": self.getEmail(), 
            "linkedInUrl": self.getLinkedInUrl(),
            "phoneNumber": self.getPhoneNumber(),
            "hasEmail": self.hasEmail,
            "hasLinkedIn": self.hasLinkedIn,
            "hasPhone": self.hasPhone
        }
    
    def fullDescription(self) -> dict:
        """
        Provide a full description of the customer, including all attributes.

        Returns:
        - A dictionary containing the full description of the customer.
        """
        d = {
            "name": self.getName(),        
            "role": self.getRole() if not pd.isnull(self.role) else None,
            "company": self.getCompany() if not pd.isnull(self.role) else None
        }
        d.update(self.getContactInfo())
        d.update(self.getZohoInfo())
        return d
    
    def __repr__(self):
        """
        Provide a string representation of the customer.

        Returns:
        - A string representing the customer.
        """
        return f"Customer {self.getName()}"


class CustomerGenerator:
    def __init__(self):
        """
        Initialize a CustomerGenerator instance to manage and load customer data.
        """
        self.customers = list()
        self.ID = None


    def loadCustomer(self, customerDict: dict, platform: str, role: str | None = None, checkEmail: bool = False, checkLinkedIn: bool = False, checkPhone: bool = False) -> Customer:
        """
        Load a customer from a dictionary and platform information.

        Parameters:
        - customerDict: Dictionary containing customer data.
        - platform: Platform to associate with the customer.
        - role: Role of the customer (optional).
        - checkEmail: Flag to check for email (default: False).
        - checkLinkedIn: Flag to check for LinkedIn URL (default: False).
        - checkPhone: Flag to check for phone number (default: False).

        Returns:
        - The loaded Customer instance.
        """
        c = customerDict
        
        if platform == "LinkedIn":
            firstName   = c.loc["First Name"]           
            lastName    = c.loc["Last Name"]            
            role        = c.loc["Title"] if c.loc["Title"] else role
            company     = c.loc["Company Name"] if c.loc["Company Name"] else None
            linkedInUrl = c.loc["Person Linkedin Url"]
            email       = c.loc["Email"] if (checkEmail and c.loc["Email"] != 'nan') else None
            phone       = c.loc["Phone"] if checkPhone else None
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
            
            email       = c.loc["Email"] if c.loc["Email"] != 'nan' else None
            linkedInUrl = c.loc["Person Linkedin Url"] if (checkLinkedIn and c.loc["LinkedIn Url"] != 'nan') else None
            phone       = c.loc["Phone"] if checkPhone else None

            cust = Customer(firstName=firstName, lastName=lastName, role=role, company=company, email=email, linkedInUrl=linkedInUrl, phoneNumber=phone, leadSource=leadSource, leadStage=leadStage, leadStatus=leadStatus, productOfInterest=productOfInterest, country=country)

        elif platform == "Phone":
            name        = c.loc["Name"]
            role        = c.loc["Role"]
            email       = c.loc["Email"] if (checkEmail and c.loc["Email"] != 'nan') else None
            phone       = c.loc["Phone"] if checkPhone else None
            country     = c.loc["Country"]
    
            cust = Customer(name=name, role=role, email=email, phoneNumber=phone, country=country) 
        self.customers.append(cust)
        return cust


    def getCustomers(self) -> list:
        """
        Retrieve the list of loaded customers.

        Returns:
        - A list of Customer instances.
        """
        return self.customers

    
    def exportCustomers(self) -> list:
        """
        Export the loaded customers as a list of dictionaries.

        Returns:
        - A list of dictionaries representing the customers.
        """
        return [cust.fullDescription() for cust in self.getCustomers()]


def customerImport(dbClient, rawData, platform: str, title: str | None = None, country: str | None = None) -> dict:
    """
    Import customer data into the Firestore database.

    Parameters:
    - dbClient: Firestore database client.
    - rawData: Raw data to import.
    - platform: Platform associated with the customers.
    - title: Title of the customers (optional).
    - country: Country of the customers (optional).

    Returns:
    - A dictionary representing the cleaned and processed data.
    """
    checkPhone = platform in ["Phone", "Email"]
    checkEmail = platform in ["Phone", "Email"]
    checkLinkedIn = platform == "LinkedIn"

    rawDF = pd.DataFrame(rawData)
    
    if platform == "LinkedIn":    
        clean = rawDF[["profile_url", "last_name", "first_name", "current_company", "current_company_position"]]
        rename = {
            "profile_url": "Person Linkedin Url",
            "last_name": "Last Name",
            "first_name": "First Name",
            "current_company": "Company Name",
            "current_company_position": "Title"
        }
        clean = clean.rename(columns=rename)
        clean["Title"] = title
        clean["Country"] = country
        clean.loc[clean["Company Name"].isna(), "Company Name"] = None
    
    elif platform == "Email":
        rawCols = rawDF.keys().to_list()
        cols = ["Email", "First Name", "Last Name", "Lead Source",  "Lead Status", "Title", "Specialty", "Company"]

        if checkPhone:
            if "Phone" in rawCols: 
                cols.append("Phone")
            elif "Phone Number" in rawCols: 
                cols.append("Phone Number")
            else: 
                checkPhone = False

        if "Product-of-Interest-" in rawCols: 
            cols.append("Product-of-Interest-")
        if "Product of Interest" in rawCols: 
            cols.append("Product of Interest")
        
        if "Country-" in rawCols: 
            cols.append("Country-")
        if "Country" in rawCols: 
            cols.append("Country")
        if "Country List" in rawCols: 
            cols.append("Country List")
        
        cols.append("Lead Stage") if "Lead Stage" in rawCols else cols.append("Record Stage")
        
        clean = rawDF[cols]
        rename = {
            "Product-of-Interest-" : "Product of Interest",
            "Country-" : "Country",
            "Country List" : "Country",
            "Record Stage" : "Lead Stage",
            "Phone Number" : "Phone"
        }
        clean = clean.rename(columns=rename)
        
    elif platform == "Phone":
        rawCols = rawDF.keys().to_list()
        columns = ["Name", "Profession", "Phone Number"] 
        if checkEmail:
            if "Email" in rawCols: 
                columns.append("Email")
        clean = rawDF[columns]
        clean.loc[:, "Country"] = country
        rename = {
            "Profession" : "Role",
            "Phone Number" : "Phone"
        }
        clean = clean.rename(columns=rename)

    clean = clean.replace({np.nan: None})
    custGen = CustomerGenerator()
    clean['custObj'] = clean.apply(custGen.loadCustomer, axis=1, args=[platform, title, checkEmail, checkLinkedIn, checkPhone])

    # For indexing against existing customers
    if platform == "LinkedIn":
        keys = ["linkedInUrl"]
    elif platform == "Email":
        keys = ["email"]
    elif platform == "Phone":
        keys = ["phoneNumber"]

    # Upload customers into Firestore
    uploadCustomers(dbClient, custGen, keys=keys)
    countRecords(dbClient, "customers")
    
    return clean.to_dict()


def countRecords(dbClient, collection: str):
    """
    Count the number of records in a Firestore collection.

    Parameters:
    - dbClient: Firestore database client.
    - collection: Name of the Firestore collection.

    Returns:
    - The number of records in the collection.
    """
    return len(dbClient.collection(collection).get())


def dictToDocument(x, batch, collectionRef):
    """
    Convert a dictionary to a Firestore document and add it to a batch.

    Parameters:
    - x: Dictionary to convert.
    - batch: Firestore batch to add the document to.
    - collectionRef: Firestore collection reference.
    """
    doc_ref = collectionRef.document()
    batch.set(doc_ref, x.to_dict())


def compareToDatabase(upload: pd.DataFrame, dbClient, collection: str, keys: list = []):
    """
    Compare a DataFrame to existing records in a Firestore collection and upload new records.

    Parameters:
    - upload: DataFrame containing the records to upload.
    - dbClient: Firestore database client.
    - collection: Name of the Firestore collection.
    - keys: List of keys to use for comparison.

    Returns:
    - None
    """
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
    """
    Upload customer data to Firestore after comparing with existing records.

    Parameters:
    - dbClient: Firestore database client.
    - custGen: CustomerGenerator instance containing the customers to upload.
    - keys: List of keys to use for comparison.
    """
    upload = pd.DataFrame(custGen.exportCustomers())
    collection = "customers"
    compareToDatabase(upload, dbClient, collection, keys)


def variableImport(dbClient, rawData, platform: str | None = None, product: str | None = None, ownerEmail: str | None = None):
    """
    Import variable data into Firestore.

    Parameters:
    - dbClient: Firestore database client.
    - rawData: Raw data to import.
    - platform: Platform associated with the variables (optional).
    - product: Product associated with the variables (optional).
    - ownerEmail: Email of the owner of the variables (optional).

    Returns:
    - A dictionary representing the cleaned and processed data.
    """
    df = pd.DataFrame(rawData)
    if 'Unnamed: 0' in df.keys().to_list():
        df = df.drop('Unnamed: 0', axis=1)
    
    content_flags = {
        "contentA": True,
        "contentB": True,
        "contentC": "contentC" in df.keys().to_list(),
        "contentD": "contentD" in df.keys().to_list(),
        "contentE": "contentE" in df.keys().to_list()
    }
    
    for phase in df["Phase"].unique():
        a = createVariableGenerator(dbClient, phase, product, ownerEmail, platform)
        df[df["Phase"] == phase].apply(uploadVariables, axis=1, args=[dbClient, a["variableGeneratorID"]] + list(content_flags.values())) 

    return df.to_dict()


def lookupVariables(experiment, varTypes):
    """
    Lookup variables by their type in an experiment.

    Parameters:
    - experiment: The experiment to search in.
    - varTypes: List of variable types to search for.

    Returns:
    - A dictionary mapping variable types to their values in the experiment.
    """
    getIndex = lambda varType: experiment.where(experiment == varType).dropna().index.values[0].split(" ")[1]
    getValue = lambda varType:  experiment[f"Variable {getIndex(varType)} Value"]
    
    varLookup = dict()
    for i, v in enumerate(varTypes):
        varLookup[v] = getValue(v)
    return varLookup


def createVariable(dbClient, generatorID: int, painPoint: str, contentA: str | None = None, contentB: str | None = None, contentC: str | None = None, contentD: str | None = None, contentE: str | None = None):
    """
    Create a new variable in Firestore.

    Parameters:
    - dbClient: Firestore database client.
    - generatorID: ID of the generator creating the variable.
    - painPoint: The pain point the variable addresses.
    - contentA-E: Content associated with the variable.

    Returns:
    - A dictionary representing the created variable, or None if not unique.
    """
    collection = "variables"
    varGenFilter = firestore.FieldFilter("variableGeneratorID", "==", generatorID)
    data = [d.to_dict() for d in dbClient.collection(collection).where(filter=varGenFilter).get()]
    varID = 1
    if data:
        df = pd.DataFrame(data=data)
        variableIsUnique = False
        
        if not df.empty:
            if contentA != None and not variableIsUnique:
                variableIsUnique = len(df[df["contentA"] == contentA]) == 0 
                
            if contentB != None and not variableIsUnique:
                variableIsUnique = len(df[df["contentB"] == contentB]) == 0 
            
            if contentC != None and not variableIsUnique:
                variableIsUnique = len(df[df["contentC"] == contentC]) == 0 
            
            if contentD != None and not variableIsUnique:
                variableIsUnique = len(df[df["contentD"] == contentD]) == 0  
            
            if contentE != None and not variableIsUnique:
                variableIsUnique = len(df[df["contentE"] == contentE]) == 0  
            
            if variableIsUnique:  
                varID = max(df["variableID"]) + 1
            else:     
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


def uploadVariables(x, dbClient, generatorID, contentA: bool = False, contentB: bool = False, contentC: bool = False, contentD: bool = False, contentE: bool = False):
    """
    Upload variables to Firestore based on input data.

    Parameters:
    - x: Data to upload.
    - dbClient: Firestore database client.
    - generatorID: ID of the generator creating the variables.
    - contentA-E: Flags indicating which content fields to upload.
    """
    uploadDict = {
        "dbClient": dbClient,
        "generatorID": generatorID,
        "painPoint": x["Pain Point"]
    }
    if contentA:
        uploadDict.update({"contentA": x["contentA"]})
    if contentB:
        uploadDict.update({"contentB": x["contentB"]})
    if contentC:
        uploadDict.update({"contentC": x["contentC"]})
    if contentD:
        uploadDict.update({"contentD": x["contentD"]})
    if contentE:
        uploadDict.update({"contentE": x["contentE"]})
    upload = createVariable(**uploadDict)


def lookupVariablesByVarGen(dbClient, variableGeneratorID):
    """
    Lookup variables based on a variable generator ID.

    Parameters:
    - dbClient: Firestore database client.
    - variableGeneratorID: ID of the variable generator to search for.

    Returns:
    - A list of dictionaries representing the variables.
    """
    varGenFilter = firestore.FieldFilter("variableGeneratorID", '==', variableGeneratorID)
    data = dbClient.collection("variables").where(filter=varGenFilter).get()
    return [d.to_dict() for d in data]


def createVariableGenerator(dbClient, phase: str, product: str, ownerEmail: str, platform: str):
    """
    Create a new variable generator in Firestore.

    Parameters:
    - dbClient: Firestore database client.
    - phase: The phase of the variable generator.
    - product: The product associated with the variable generator.
    - ownerEmail: The email of the owner of the variable generator.
    - platform: The platform associated with the variable generator.

    Returns:
    - A dictionary representing the created variable generator.
    """
    collection = "variableGenerators"
    data = [d.to_dict() for d in dbClient.collection(collection).get()]
    
    if data:
        df = pd.DataFrame(data=data)
        generatorID = max(df["variableGeneratorID"]) + 1
        checkGen = df[(df["phase"] == f"{phase}") & \
                      (df["product"] == f"{product}") & \
                      (df["ownerEmail"] == f"{ownerEmail}") & \
                      (df["platform"] == f"{platform}")]
        if not checkGen.empty:
            versionID = max(checkGen["versionID"]) + 1
        else:
            versionID = 1
    else:
        generatorID = 1
        versionID = 1

    upload = {
        "phase": phase,
        "product": product,
        "ownerEmail": ownerEmail,
        "platform": platform,
        "variableGeneratorID": generatorID,
        "versionID": versionID
    }

    dbClient.collection(collection).add(upload)
    return upload


def createExpGen(dbClient, varGenIDs: list, platform: str, ownerEmail: str) -> dict:
    """
    Create a new experiment generator in Firestore.

    Parameters:
    - dbClient: Firestore database client.
    - varGenIDs: List of variable generator IDs to associate with the experiment generator.
    - platform: Platform associated with the experiment generator.
    - ownerEmail: Email of the owner of the experiment generator.

    Returns:
    - A dictionary representing the created experiment generator.
    """
    rawDataExpGen = dbClient.collection("experimentGenerators").get()
    rawData = [d.to_dict() for d in rawDataExpGen]
    
    expGen = pd.DataFrame(rawData)
    varGenDict = dict()
    
    if not expGen.empty:
        expGenID = max(expGen["experimentGeneratorID"].values) + 1
    else:
        expGenID = 1

    numVars = len(varGenIDs)
    sameSizeExpGen = [d for d in rawData if len(d.keys()) - 3 == numVars]
    expGen = pd.DataFrame(sameSizeExpGen)

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
            expGenInfo = {
                "experimentGeneratorID": int(expGenID),
                "ownerEmail": ownerEmail,
                "platform": platform
            }
            expGenInfo.update(varGenDict)
            
            dbClient.collection("experimentGenerators").add(expGenInfo)
            return expGenInfo


def checkExpGenValid(dbClient, varGenIDs: list) -> bool:    
    """
    Check if an experiment generator is valid based on its variable generators.

    Parameters:
    - dbClient: Firestore database client.
    - varGenIDs: List of variable generator IDs to validate.

    Returns:
    - True if the experiment generator is valid, False otherwise.
    """
    vGen = pd.DataFrame([d.to_dict() for d in dbClient.collection("variableGenerators").get()])
    vGen = vGen[vGen["variableGeneratorID"].isin(varGenIDs)]
    
    check = len(vGen.index) == len(varGenIDs)

    variables = pd.DataFrame([d.to_dict() for d in dbClient.collection("variables").get()])
    
    for vGenID in varGenIDs:
        vCheck = variables[variables["variableGeneratorID"] == int(vGenID)]
        check = not vCheck.empty

    return check


def getVarBank(dbClient, expGen: ExperimentGenerator):
    """
    Retrieve the bank of variables associated with an experiment generator.

    Parameters:
    - dbClient: Firestore database client.
    - expGen: ExperimentGenerator instance.

    Returns:
    - A dictionary containing the variable bank.
    """
    numVariables = len(expGen.getGenerators())
    variables = pd.DataFrame([d.to_dict() for d in dbClient.collection("variables").get()])
    varBank = collections.defaultdict(list)
    for i, varGenID in enumerate(expGen.getGenerators()):
        varBank[f"variableGeneratorID_{i+1}"] = varGenID
        varBank[f"variableID_{i+1}_Bank"] = variables[variables["variableGeneratorID"] == varGenID]["variableID"].values
    return varBank


def createExperiment(dbClient, expGen: ExperimentGenerator, varBank: dict, ownerEmail: str, platform: str) -> int:
    """
    Create a new experiment in Firestore.

    Parameters:
    - dbClient: Firestore database client.
    - expGen: ExperimentGenerator instance.
    - varBank: Bank of variables to use in the experiment.
    - ownerEmail: Email of the experiment owner.
    - platform: Platform associated with the experiment.

    Returns:
    - The ID of the created experiment.
    """
    rawData = dbClient.collection("experiments")

    if ownerEmail is not None:
        ownerFilter = firestore.FieldFilter("ownerEmail", "==", ownerEmail)
        rawData = rawData.where(filter=ownerFilter)
    
    if expGen.getID() is not None:
        expGenFilter = firestore.FieldFilter("experimentGeneratorID", "==", int(expGen.getID()))
        rawData = rawData.where(filter=expGenFilter)

    data = [d.to_dict() for d in rawData.get()]
    numVariables = int((len(varBank.keys())) / 2)

    experiments = pd.DataFrame([d for d in data if (len(d.keys()) - 4) / 2 == numVariables])
    
    expID = 1
    
    if not experiments.empty:
        expID = max(experiments["experimentID"].values) + 1

    expDict = dict()
    expDict["ownerEmail"] = ownerEmail
    
    for i in range(1, numVariables + 1):
        varGenID = int(varBank[f"variableGeneratorID_{i}"])
        varID = int(random.choice(varBank[f"variableID_{i}_Bank"]))        
        
        expDict[f"variableGeneratorID_{i}"] = varGenID
        expDict[f"variableID_{i}"] = varID
        
        if not experiments.empty: 
            experiments = experiments[experiments[f"variableGeneratorID_{i}"] == varGenID]

        if not experiments.empty: 
            experiments = experiments[experiments[f"variableID_{i}"] == varID]        
    
    if not experiments.empty:
        expID = int(experiments["experimentID"].values[0])
    
    else:
        expDict["experimentGeneratorID"] = int(expGen.getID())
        expDict["experimentID"] = int(expID)
        expDict["platform"] = platform
        dbClient.collection("experiments").add(expDict)

    return expID


def getActiveCustomers(dbClient, expGenID: int, expID: int = 0) -> dict:
    """
    Retrieve active customers associated with a specific experiment or experiment generator.

    Parameters:
    - dbClient: Firestore database client.
    - expGenID: ID of the experiment generator.
    - expID: ID of the experiment (optional).

    Returns:
    - A list of references to the active customers.
    """
    customers_ref = dbClient.collection("customers")
    if expID != 0:
        experiment_filter = firestore.FieldFilter("experimentID", "==", int(expID))
    experimentGen_filter = firestore.FieldFilter("experimentGeneratorID", "==", int(expGenID))

    customers = customers_ref.stream()    
    customers_with_experiments = []
    
    for customer in customers:
        customer_ref = customer.reference
        experiments_ref = customer_ref.collection("experiments")
        
        if expID != 0:
            experiments = experiments_ref.where(filter=experiment_filter).where(filter=experimentGen_filter).get()
        else: 
            experiments = experiments_ref.where(filter=experimentGen_filter).get()

        if len(experiments) != 0:
            customers_with_experiments.append(deepcopy(customer_ref))   

    return customers_with_experiments


def getInactiveCustomers(customers, platform) -> dict:
    """
    Retrieve inactive customers associated with a specific platform.

    Parameters:
    - customers: Firestore collection of customers.
    - platform: Platform to filter by.

    Returns:
    - A list of references to the inactive customers.
    """
    customers_without_experiments = []
    platform_filter = firestore.FieldFilter("platform", "==", platform)
    
    for customer in customers.stream():
        customer_ref = customer.reference
        experiments_ref = customer_ref.collection("experiments")
        
        experiments = experiments_ref.where(filter=platform_filter).get()
        print(experiments)

        if len(experiments) == 0:
            customers_without_experiments.append(deepcopy(customer_ref))

    return customers_without_experiments


def lookupCustomerBatch(dbClient, customers):
    """
    Lookup a batch of customers in Firestore.

    Parameters:
    - dbClient: Firestore database client.
    - customers: DataFrame containing the customers to lookup.

    Returns:
    - A list of references to the found customers.
    """
    cust_references = []

    for cust in customers.to_dict(orient='records'):
        emailFilter = firestore.FieldFilter("email", "==", cust["email"])
        phoneFilter = firestore.FieldFilter("phoneNumber", "==", cust["phoneNumber"])
        customer_ref = dbClient.collection("customers").where(
            filter=emailFilter).where(filter=phoneFilter).get()[0].reference
        cust_references.append(deepcopy(customer_ref))

    return cust_references


def getCustomers(dbClient, custRole: str = None, platform: str = None, country: str = None, inactiveOnly: str = "False") -> pd.DataFrame:
    """
    Retrieve customers from Firestore based on filters.

    Parameters:
    - dbClient: Firestore database client.
    - custRole: Role to filter by (optional).
    - platform: Platform to filter by (optional).
    - country: Country to filter by (optional).
    - inactiveOnly: Flag to include only inactive customers (default: "False").

    Returns:
    - A DataFrame containing the filtered customers.
    """
    customers = dbClient.collection("customers")
    
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
        elif platform == "Phone":
            platform_filter = firestore.FieldFilter("hasPhone", "==", True)
        customers = customers.where(filter=platform_filter)

    try:
        if inactiveOnly:
            customer_data = getInactiveCustomers(customers, platform)
        else:
            customer_data = customers.get()

    except Exception as e:
        print(f"Error retrieving customer data: {e}")
        return None

    numCust = len(customer_data)
    print("Number of customers found in the database", numCust)
    if numCust > 0:
        customers_export = [d.get().to_dict() for d in customer_data]
        return {"customers": customers_export}
    else:
        return None


def replaceNaN_single(d):
    """
    Replace NaN and other placeholder values with None in a dictionary.

    Parameters:
    - d: Dictionary to process.

    Returns:
    - The processed dictionary with NaN and placeholder values replaced with None.
    """
    for key, value in d.items():
        if value in ["N/A", "NaN", float('inf'), float('-inf')]:
            d[key] = None
        elif pd.isna(value):
            d[key] = None
    return d


def replaceNaN_db(dbClient, collections: list) -> pd.DataFrame:
    """
    Replace NaN values in multiple Firestore collections.

    Parameters:
    - dbClient: Firestore database client.
    - collections: List of collection names to process.

    Returns:
    - A message indicating completion.
    """
    for collection in collections:
        docs = dbClient.collection(collection)
        docSnapshots = docs.get()
    
        for docSnapshot in docSnapshots:
            docInfo = replaceNaN_single(docSnapshot.to_dict())
            docSnapshot.reference.set(docInfo, merge=True)

    return f"Done with {len(collections)} collections."
        

def checkCustomers(customers: pd.DataFrame, requestedCustomers: int) -> bool:
    """
    Check if the number of provided customers meets the requested amount.

    Parameters:
    - customers: DataFrame containing the customers.
    - requestedCustomers: Number of requested customers.

    Returns:
    - True if the provided customers meet or exceed the requested amount, False otherwise.
    """
    print(f"Customers provided: {len(customers.index)}. Customers Requested: {requestedCustomers}" )
    return len(customers.index) >= requestedCustomers


def assignExperiment(x, batch, dbClient, expID: int, expGenID: int, platform: str):
    """
    Assign an experiment to a customer in Firestore.

    Parameters:
    - x: Customer data to process.
    - batch: Firestore batch to add the experiment assignment to.
    - dbClient: Firestore database client.
    - expID: ID of the experiment.
    - expGenID: ID of the experiment generator.
    - platform: Platform associated with the experiment.
    """
    cust = None

    if platform == "LinkedIn":
        key = x.to_dict()["linkedInUrl"]
        linkedIn_filter = firestore.FieldFilter("linkedInUrl", "==", key)
        cust = dbClient.collection("customers").where(filter=linkedIn_filter).get()
    
    elif platform == "Email":
        key = x.to_dict()["email"]
        email_filter = firestore.FieldFilter("email", "==", key)
        cust = dbClient.collection("customers").where(filter=email_filter).get()
    
    elif platform == "Phone":
        key = x.to_dict()["phoneNumber"]
        phone_filter = firestore.FieldFilter("phoneNumber", "==", key)
        cust = dbClient.collection("customers").where(filter=phone_filter).get()
        
    if cust:
        custRef = cust[0].reference
        _expID, _expGenID = int(expID), int(expGenID)
        expRef = custRef.collection("experiments").document()

        batch.set(expRef, {
            "experimentID": _expID, 
            "experimentGeneratorID": _expGenID, 
            "platform": platform,
            "status": "Active",
            "assigned_At": firestore.SERVER_TIMESTAMP
        })


def assignContentToCustomers(dbClient, customers, batch, expID: int, expGenID: int, ownerEmail: str = None, platform: str = None) -> dict:
    """
    Assign content to customers in an experiment.

    Parameters:
    - dbClient: Firestore database client.
    - customers: DataFrame containing the customers to assign content to.
    - batch: Firestore batch to add the assignments to.
    - expID: ID of the experiment.
    - expGenID: ID of the experiment generator.
    - ownerEmail: Email of the experiment owner (optional).
    - platform: Platform associated with the experiment (optional).

    Returns:
    - A dictionary containing the assigned customers.
    """
    activeCustomers = lookupCustomerBatch(dbClient, customers)

    if not activeCustomers:
        return None
    
    experiment_ref = dbClient.collection("experiments")
    experiment_data = experiment_ref.where(
        filter=firestore.FieldFilter("experimentID", "==", expID)
    ).where(
        filter=firestore.FieldFilter("experimentGeneratorID", "==", expGenID)
    ).get()

    if not experiment_data:
        return None

    expInfo = experiment_data[0].to_dict()
    numVariables = int((len(expInfo.keys()) - 3) / 2)
    
    variable_content = {}
    for i in range(1, numVariables + 1):
        varGenID = expInfo[f"variableGeneratorID_{i}"]
        varID = expInfo[f"variableID_{i}"]

        var_data = dbClient.collection("variables").where(
            filter=firestore.FieldFilter("variableGeneratorID", "==", varGenID)
        ).where(
            filter=firestore.FieldFilter("variableID", "==", varID)
        ).get()

        if var_data:
            content = var_data[0].to_dict()
            for suffix in ["A", "B", "C", "D", "E"]:
                content_key = f"content{suffix}"
                if content.get(content_key):
                    variable_content[f"content_{i}_{suffix}"] = content[content_key]

    tasks = []
    if ownerEmail:
        owner = dbClient.collection("Users").where(
            filter=firestore.FieldFilter("email", "==", ownerEmail)
        ).get()[0].reference

        for i in range(1, numVariables + 1):
            task = {
                "sequence_idx": f"{i}",
                "platform": platform
            }
            for suffix in ["A", "B", "C", "D", "E"]:
                key = f"content_{i}_{suffix}"
                if key in variable_content:
                    task[key] = variable_content[key]
            task.update(expInfo)
            tasks.append(task)    

    for active in activeCustomers:
        customer_info = active.get().to_dict()
        
        expRef = active.collection("experiments").document()
        expInfo.update(variable_content)
        batch.set(expRef, expInfo, merge=True)
        
        if ownerEmail:
            for task in tasks:
                task_with_customer_info = {**task, **customer_info}
                task_doc = owner.collection("Agenda").document()
                batch.set(task_doc, task_with_customer_info)
    
    return activeCustomers


def getExperiments(dbClient, ownerEmail, experimentGeneratorID) -> dict:
    """
    Retrieve experiments associated with a specific owner and experiment generator.

    Parameters:
    - dbClient: Firestore database client.
    - ownerEmail: Email of the experiment owner.
    - experimentGeneratorID: ID(s) of the experiment generator(s).

    Returns:
    - A dictionary containing the experiments.
    """
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
    
                numVariables = int((len(expInfo.keys()) - 3) / 2)
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


def getTasks(dbClient, ownerEmail):
    """
    Retrieve tasks associated with a specific owner.

    Parameters:
    - dbClient: Firestore database client.
    - ownerEmail: Email of the owner.

    Returns:
    - A list of tasks associated with the owner.
    """
    owner = dbClient.collection("Users").where("email", "==", ownerEmail).get()[0].reference
    tasks_data = owner.collection("Agenda").get()
    tasks = [t.to_dict() for t in tasks_data]
    return tasks


def completeTask(dbClient, batch, ownerEmail: str, platform: str | None = None, phoneNumber: str | None = None, email: str | None = None, sequence_idx: str | None = None):
    """
    Mark a task as complete for a specific owner.

    Parameters:
    - dbClient: Firestore database client.
    - batch: Firestore batch to add the task completion to.
    - ownerEmail: Email of the owner.
    - platform: Platform associated with the task (optional).
    - phoneNumber: Phone number associated with the task (optional).
    - email: Email associated with the task (optional).
    - sequence_idx: Sequence index of the task (optional).

    Returns:
    - A dictionary representing the completed task.
    """
    owner = dbClient.collection("Users").where("email", "==", ownerEmail).get()[0].reference
    get_data = owner.collection("Agenda")

    if platform is not None:
        platformFilter = firestore.FieldFilter("platform", "==", platform)
        get_data = get_data.where(filter=platformFilter)
    
    if phoneNumber is not None:
        phoneFilter = firestore.FieldFilter("phoneNumber", "==", phoneNumber)
        get_data = get_data.where(filter=phoneFilter)

    if email is not None:
        emailFilter = firestore.FieldFilter("email", "==", email)
        get_data = get_data.where(filter=emailFilter)

    if sequence_idx is not None:
        sequenceFilter = firestore.FieldFilter("sequence_idx", "==", sequence_idx)
        get_data = get_data.where(filter=sequenceFilter)

    batch.delete(get_data.get()[0].reference)

    return get_data.get()[0].to_dict()


def submitEvent(dbClient, batch, event: dict):
    """
    Submit an event to the Firestore database.

    Parameters:
    - dbClient: Firestore database client.
    - batch: Firestore batch to add the event to.
    - event: Dictionary representing the event.
    """
    doc = dbClient.collection("events").document()
    batch.set(doc, event)


def fullExperimentalSetup(dbClient, varGenIDs: list, trials: int = 5, numExperiments: int = 5, platform: str = None, country: str = None, ownerEmail: str = None):    
    """
    Set up a full experiment including variables, customers, and assignments.

    Parameters:
    - dbClient: Firestore database client.
    - varGenIDs: List of variable generator IDs to use in the experiment.
    - trials: Number of trials per experiment (default: 5).
    - numExperiments: Number of experiments to create (default: 5).
    - platform: Platform associated with the experiment (optional).
    - country: Country associated with the experiment (optional).
    - ownerEmail: Email of the experiment owner (optional).

    Returns:
    - A success message indicating completion.
    """
    assert country is not None
    rawDataCust = getCustomers(dbClient, platform=platform, country=country, inactiveOnly="True")
    if rawDataCust is not None:
        expGenInfo = createExpGen(dbClient, varGenIDs=varGenIDs, platform=platform, ownerEmail=ownerEmail)
        expGen = ExperimentGenerator(**expGenInfo)
        varBank = getVarBank(dbClient, expGen)
        
        cust = pd.DataFrame(rawDataCust["customers"])
        
        experiments = set()
        
        while numExperiments > 0:
            if checkCustomers(cust, trials):
                numExperiments -= 1

                expID = createExperiment(dbClient, expGen, varBank, ownerEmail, platform)
                expGenID = expGen.getID()
                experiments.add(expID)
                
                trial_cust = cust.sample(n=trials)

                batch = dbClient.batch()
                if platform == "Phone":
                    assignContentToCustomers(dbClient, trial_cust, batch, int(expID), int(expGenID), ownerEmail, platform)
                else:
                    assignContentToCustomers(dbClient, trial_cust, batch, int(expID), int(expGenID))
                batch.commit()
                
                if platform == "Email":
                    cust = cust[~cust["email"].isin(trial_cust["email"])]
                elif platform == "LinkedIn":
                    cust = cust[~cust["linkedInUrl"].isin(trial_cust["linkedInUrl"])]
                elif platform == "Phone":
                    cust = cust[~cust["phoneNumber"].isin(trial_cust["phoneNumber"])]
            else:
                raise Exception("Error: Upload Customers.")
            
        return "Success: Experiment uploaded."


def getVariableGenerators(db, ownerEmail: str, platform: str | None = None, phase: str | None = None) -> dict:
    """
    Retrieve variable generators associated with a specific owner.

    Parameters:
    - db: Firestore database client.
    - ownerEmail: Email of the owner.
    - platform: Platform to filter by (optional).
    - phase: Phase to filter by (optional).

    Returns:
    - A dictionary containing the variable generators.
    """
    ownerFilter = firestore.FieldFilter("ownerEmail", "==", ownerEmail)
    get_data = db.collection("variableGenerators").where(filter=ownerFilter)
    
    if platform:
        platformFilter = firestore.FieldFilter("platform", "==", platform)
        get_data = get_data.where(filter=platformFilter)

    if phase:
        phaseFilter = firestore.FieldFilter("phase", "==", phase)
        get_data = get_data.where(filter=phaseFilter)

    data = {"variableGenerators": [d.to_dict() for d in get_data.get()]}
    
    if data:
        return data
    else:
        return None


def getExperimentGenerators(db, ownerEmail: str, platform: str | None = None) -> dict:
    """
    Retrieve experiment generators associated with a specific owner.

    Parameters:
    - db: Firestore database client.
    - ownerEmail: Email of the owner.
    - platform: Platform to filter by (optional).

    Returns:
    - A dictionary containing the experiment generators.
    """
    ownerFilter = firestore.FieldFilter("ownerEmail", "==", ownerEmail)
    get_data = db.collection("experimentGenerators").where(filter=ownerFilter)
    
    if platform is not None:
        platformFilter = firestore.FieldFilter("platform", "==", platform)
        get_data = get_data.where(filter=platformFilter)
        print("Platform is not None", ownerEmail, platform)

    get_data = get_data.get()
    data = {"experimentGenerators": [d.to_dict() for d in get_data]}
    if data:
        return data
    else:
        return None


def getAgenda(db, ownerEmail: str, platform: str | None = None):
    """
    Retrieve the agenda (tasks) associated with a specific owner.

    Parameters:
    - db: Firestore database client.
    - ownerEmail: Email of the owner.
    - platform: Platform to filter by (optional).

    Returns:
    - A dictionary containing the tasks.
    """
    emailFilter = firestore.FieldFilter("email", "==", ownerEmail)
    owner = db.collection("Users").where(filter=emailFilter).get()[0].reference
    
    if platform is not None:
        platformFilter = firestore.FieldFilter("platform", "==", platform)
        get_data = owner.collection("Agenda").where(filter=platformFilter)

    get_data = get_data.get()
    data = {"Tasks": [d.to_dict() for d in get_data]}
    if data:
        return data
    else:
        return None


def getCollection(db, collection) -> dict:
    """
    Retrieve a collection from Firestore.

    Parameters:
    - db: Firestore database client.
    - collection: Name of the collection to retrieve.

    Returns:
    - A dictionary containing the collection's documents.
    """
    get_data = db.collection(collection).get()
    data = {collection: [d.to_dict() for d in get_data]}
    if data:
        return data
    else:
        return None


def readWithNone(path: str) -> pd.DataFrame:
    """
    Read a CSV file and replace "None" values with actual None.

    Parameters:
    - path: Path to the CSV file.

    Returns:
    - A DataFrame with "None" values replaced with None.
    """
    checkNone = lambda x: None if x == "None" else x
    raw = pd.read_csv(path, dtype=str)
    raw = raw.applymap(checkNone)
    return raw


def extractOutbound(activeCustomer, expGenID) -> dict:
    """
    Extract outbound data for a customer in an experiment.

    Parameters:
    - activeCustomer: Firestore document reference for the active customer.
    - expGenID: ID of the experiment generator.

    Returns:
    - A dictionary containing the outbound data.
    """
    expRef = activeCustomer.collection("experiments").where("experimentGeneratorID", "==", int(expGenID)).get()[0]
    outbound = activeCustomer.get().to_dict()
    expInfo = expRef.to_dict()

    outbound.update(expInfo)
    
    return outbound


def extractAllOutboundContacts(dbClient, experimentGeneratorIDs) -> dict:
    """
    Extract outbound contacts for multiple experiment generators.

    Parameters:
    - dbClient: Firestore database client.
    - experimentGeneratorIDs: List of experiment generator IDs.

    Returns:
    - A list of dictionaries containing the outbound contacts.
    """
    if type(experimentGeneratorIDs) is not list:
        experimentGeneratorIDs = list(experimentGeneratorIDs)

    contacts = []

    for expGenID in experimentGeneratorIDs:         
        activeCustomers = getActiveCustomers(dbClient, expGenID)
        if activeCustomers:
            contacts.extend([deepcopy(extractOutbound(active, expGenID)) for active in activeCustomers])

    return contacts
