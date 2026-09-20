import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app= FastAPI()
model=joblib.load("house_model.joblib") #this loads your trained model for use in deployment
features=joblib.load("house_features.joblib") #this loads all the column header names of your dataset

#input schema(this will give schema to backend that in which format data will be recieved)
#create a class and let it inherit the feature of class BaseModel this will automate the schema format

class HouseFeatures(BaseModel): 
    #takes input all the features(mainly column headers execpt the predicted property) on basis of which model is trained
    MedInc: float= Field(gt=0, description="Median Income of Neighbours") #gt is greater than and Field helps setup valid condition
    HouseAge:float= Field(gt=0, description="Age of the house")
    AveRooms:float= Field(gt=0, description="")
    AveBedrms:float= Field(gt=0, description="")
    Popultion:float= Field(gt=0, description="")
    AveOccup:float= Field(gt=0, description="")
    Latitude:float= Field(ge=32, le=42, description="Latitude")
    Longitude=float= Field(ge=-125, le=-114, description="Longitude")

#home

@app.get("/")
def home():
    return{
        "message": "California House Prediction API",
        "status": "running",
        "endpoint": "send a POST request to /predict"

    }

#health(how much average error model is giving)

@app.get("/health")
def health():
    return{
        "status":"running",
        "model":"RandomForestRegressor",
        "features": features,
        "avg_error":"$39000"
    }

#prediction(output from model after sending it input)

@app.post("/predict")
def predict(house:HouseFeatures):
    try:
        input_data= pd.DataFrame([{
            "MedInc": house.MedInc,
            "HouseAge":house.HouseAge,
            "AveRooms":house.AveRooms,
            "AveBedrms":house.AveBedrms,
            "Population":house.Popultion,
            "AveOccup": house.AveOccup,
            "Latitude":house.Latitude,
            "Longitude":house.Longitude
        }])
        predicted=model.predict(input)[0]
        price_usd= predicted*100000

        return{
            "predicted_price":f"${price_usd:,.0f}",
            "predicted_price_short":f"${predicted:.2f} hundred thousands",
            "fidence_range":f"${price_usd-39000:,.0f} to ${price_usd+39000:,.0f}"
        }
    except Exception as e:
        raise HTTPException(
            status_code= 500,
            detail="prediction failed:{str(e)}"
        )
    
        
            

    




