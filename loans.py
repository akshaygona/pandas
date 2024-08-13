import json
import zipfile
from io import TextIOWrapper
import csv

race_lookup = {
        "1": "American Indian or Alaska Native",
        "2": "Asian",
        "21": "Asian Indian",
        "22": "Chinese",
        "23": "Filipino",
        "24": "Japanese",
        "25": "Korean",
        "26": "Vietnamese",
        "27": "Other Asian",
        "3": "Black or African American",
        "4": "Native Hawaiian or Other Pacific Islander",
        "41": "Native Hawaiian",
        "42": "Guamanian or Chamorro",
        "43": "Samoan",
        "44": "Other Pacific Islander",
        "5": "White",
}

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        for _ in race:
            if _ in race_lookup:
                self.race.add(race_lookup[_])
                
    def __repr__(self):
        toReturn = "Applicant('" + str(self.age) + "', " + str(sorted(list(self.race))) + ")"
        return toReturn
    
    def lower_age(self):
        lowerAge = str(self.age).replace("<","").replace(">","")
        return int(lowerAge.split("-")[0])
    
    def __lt__(self, other):
        return self.lower_age() < other.lower_age()

class Loan:
    def __init__(self, values):
        try:
            self.loan_amount = float(values["loan_amount"])
        except ValueError:
             self.loan_amount = -1
                
        try:    
            self.property_value = float(values["property_value"])
        except ValueError:
             self.property_value = -1
                
        try:
            self.interest_rate = float(values["interest_rate"])
        except ValueError:
            self.interest_rate = -1
            
        r1 = []
        for i in values:
            if i.startswith("applicant_race-"):
                r1.append(values[i])    
                
        if values["co-applicant_age"] == "9999":
            self.applicants = [Applicant(values["applicant_age"], r1)]
        else:
            r2 = []
            for i in values:
                if i.startswith("co-applicant_race-"):
                    r2.append(values[i])
            self.applicants = [Applicant(values["applicant_age"], r1), Applicant(values["co-applicant_age"], r2)]
    
    def __str__(self):
        return "<Loan: " + str(self.interest_rate) + "% on $" + str(self.property_value) + " with " + str(len(self.applicants)) + " applicant(s)>"
    
    def __repr__(self):
        return "<Loan: " + str(self.interest_rate) + "% on $" + str(self.property_value) + " with " + str(len(self.applicants)) + " applicant(s)>"
        
    def yearly_amounts(self, yearly_payment):
        assert self.interest_rate > 0
        assert self.loan_amount > 0
        amt = self.loan_amount
        while amt > 0:
            yield amt
            amt += amt*(self.interest_rate/100)
            amt -= yearly_payment

class Bank:
    def __init__(self, name):
        f = open("banks.json")
        data = json.load(f)
        f.close()
        for _ in data:
            if _["name"] == name:
                self.lei = _["lei"]
        
        zf = zipfile.ZipFile("wi.zip")
        f = zf.open("wi.csv")
        reader = csv.DictReader(TextIOWrapper(f))
        
        self.loansList = []
        for _ in reader:
            if _["lei"] == self.lei:
                self.loansList.append(Loan(_))
                
    def __len__(self):
        return len(self.loansList)
    
    def __getitem__(self, i):
        return self.loansList[i]