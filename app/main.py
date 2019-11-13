#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
    Main app code
        It receives a POST call with JSON compressed payload
        It decompresses the JSON payload
        It validates JSON schema

        It sends the data to the DB
"""
import uuid, time, json, jwt

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from starlette.requests import Request
from starlette.responses import JSONResponse

from .general_functions.general_functions import fJSONUnZip, fValidateJSONPayload
from .general_functions.logging_functions import fWriteLog

from .db_functions.db_functions import fInsertDB

from .my_config.my_config import fGPSMessageVars

fName = "Main"

class Item(BaseModel):
    item: str = None

class CustomException(Exception):
    def __init__(self, detail: str, headers: str, statusCode: int, callId: str, elapsed: float):
        self.detail = detail
        self.headers = headers
        self.statusCode = statusCode
        self.callId = callId
        self.elapsed = elapsed
        

app = FastAPI(title="GetGPS")

# fastAPI exception_handler
@app.exception_handler(CustomException)
def fExceptionHandler(request: Request, exception: CustomException):
    # log
    fWriteLog(exception.callId, fName, f"{exception.detail}", "error")
    fWriteLog(exception.callId, fName, f"END Call. Duration: {exception.elapsed}", "info")
    return JSONResponse(
        status_code=exception.statusCode,
        headers=exception.headers,
        content={"message": f"Oops! {exception.detail}"}
    )

@app.get("/")
def fTest():
    return {"Hello": "World"}

@app.post("/items/")
def fCreateItem(item: Item, request: Request) -> str:
    """
        UnZIP the data
        Check the data against schema
        Insert it into DB
    """
    callId = str(uuid.uuid1())
    start = time.perf_counter()
    fWriteLog(callId, fName, "START Call", "info")

    # the default response returned if no errors
    response = {'Success': 'The data was correctly stored.'}
    # check if Item is provided
    if item is not None:
        try:
            msgCompressed = str(item.item)
        except:
            raise CustomException(
                statusCode=404,
                detail="Item not provided.",
                headers={"X-Error": "No Item provided."},
                callId=callId,
                elapsed=round(time.perf_counter() - start, 5)
            )
    # check if header ip address and jwt token ip address are the same
    JWTtoken = None
    reqIPaddress = None
    JWTIPaddress = None
    try:
        # NGINX reverse proxy must pass along all the received headers
        # Gravitee API GW passes along Authorization bearer with the __validated__ JWT token
        reqAuthorization = request.headers["authorization"]
        reqIPaddress= request.headers["x-ip-address"]
    except Exception as e:
        raise CustomException(
            statusCode=417,
            detail="Wrong HTTP header - missing key(s).",
            headers={"X-Error": "Wrong HTTP header - missing key(s)."},
            callId=callId,
            elapsed=round(time.perf_counter() - start, 5)
        )
    else:
        # decode the JWT and compare the key ipaddress with the request.headers["x-ip-address"]
        try:
            JWTtoken = reqAuthorization.split("Bearer")[1].strip()
        except Exception as e:
            fWriteLog(callId, fName, f"Cannot grab JWT token from HTTP header: {str(e)}", "error")

        try:
            # decode JWT without validation and grab IP address
            JWTIPaddress = jwt.decode(reqAuthorization.split("Bearer")[1].strip(), verify=False)["ipaddress"]
        except Exception as e:
            fWriteLog(callId, fName, f"Cannot grab IP address from the decoded JWT token: {str(e)}", "error")

        if  ( reqIPaddress is None or JWTIPaddress is None ) or ( reqIPaddress != JWTIPaddress ):
            fWriteLog(callId, fName, f"Header IP address {str(reqIPaddress)} different than the JWT token IP address {str(JWTIPaddress)}", "error")
            raise CustomException(
                statusCode=417,
                detail="Wrong source IP address for the request.",
                headers={"X-Error": "Wrong source IP address for the request."},
                callId=callId,
                elapsed=round(time.perf_counter() - start, 5)
            )
        else:
            fWriteLog(callId, fName, f"Header IP address {str(reqIPaddress)} same with the JWT token IP address {str(JWTIPaddress)}", "info")

    # try to unzip the item
    responsefJSONUnZip = fJSONUnZip(msg = msgCompressed)
    # debug
    fWriteLog(callId, fName, str(responsefJSONUnZip), "debug")
    # error    
    if "msg" in responsefJSONUnZip.keys():
        if responsefJSONUnZip["msg"] is not None:
            msg = responsefJSONUnZip["msg"]
            if type(msg) == dict:
                try:
                    # check the data schema
                    myJSONVars = fGPSMessageVars()
                    msgJSONSchema = myJSONVars["msgJSONSchema"]
                except:
                    # the data was not correctly inserted - wrong schema
                    raise CustomException(
                            statusCode=404,
                            detail="Wrong validation schema provided.",
                            headers={"X-Error": "Wrong validation schema provided."},
                            callId=callId,
                            elapsed=round(time.perf_counter() - start, 5)
                    )
                else:
                    # check the message against the schema
                    responsefValidateJSONPayload = fValidateJSONPayload(msg = msg, JSONSchema = msgJSONSchema)
                    # debug
                    fWriteLog(callId, fName, str(responsefValidateJSONPayload), "debug")
                    if "decoded" in responsefValidateJSONPayload.keys():
                        if responsefValidateJSONPayload["decoded"] is True:
                            # the message check OK
                            # insert the messag into DB
                            responsefInsertDB = fInsertDB(msg)
                            """
                            {
                                "_id": ObjectID("5dcb40f54d175d3a9ce29918"),
                                "hostname": "raspberrypi",
                                "rStatusGPS": "Location 3D Fix",
                                "uptime": 2871924.44,
                                "rDistance": {
                                    "cdistance": 0.01,
                                    "distance": 0,
                                    "units": "Km"
                                },
                                "publish": {
                                    "publish": 3
                                },
                                "rDestinationLon": xxx,
                                "rOriginLat": xxx,
                                "rSpeed": 0,
                                "rOriginLon": xxx,
                                "rGNSSSsattelitesinView": 10,
                                "rDestinationLat": xxx,
                                "rUTC": 20191112233201,
                                "msgid": "8242daacb15c45b08ea597be1c2e30a1",
                                "publicIPAddress": "xxx",
                                "rGNSSSsattelitesUsed": 8,
                                "rOriginTimeUTC": 20191112233154,
                                "rAltitude": xxx,
                                "rGLONASSsattelitesUsed": 0
                            }
                            """
                            # debug
                            fWriteLog(callId, fName, str(responsefInsertDB), "debug")
                            if "insertedId" in responsefInsertDB.keys():
                                if responsefInsertDB["insertedId"] is None:
                                    # the data was not correctly inserted
                                    raise CustomException(
                                            statusCode=404,
                                            detail="Item not inserted into DB.",
                                            headers={"X-Error": "The Item was not inserted into DB."},
                                            callId=callId,
                                            elapsed=round(time.perf_counter() - start, 5)
                                    )
                            else:                           
                                # did not get the expected return
                                raise CustomException(
                                        statusCode=417,
                                        detail="DB did not return the expected fields.",
                                        headers={"X-Error": "DB did not return the expected fields."},
                                        callId=callId,
                                        elapsed=round(time.perf_counter() - start, 5)
                                )
                        else: 
                            # the message check NOK
                            raise CustomException(
                                    statusCode=404,
                                    detail="The Item could not be validated against the schema.",
                                    headers={"X-Error": "The Item could not be validated against the schema."},
                                    callId=callId,
                                    elapsed=round(time.perf_counter() - start, 5)
                            )
                    else:
                        # the message check NOK
                        raise CustomException(
                                statusCode=417,
                                detail="Schema validation did not return the expected fields.",
                                headers={"X-Error": "Schema validation did not return the expected fields."},
                                callId=callId,
                                elapsed=round(time.perf_counter() - start, 5)
                        )
            else:
                # the unziped msg format is invalid
                raise CustomException(
                    statusCode=404,
                    detail="The received message format is not valid.",
                    headers={"X-Error": "The received message format is not valid."},
                    callId=callId,
                    elapsed=round(time.perf_counter() - start, 5)
                )  

        else:
            # unzip function could not unzip the message
            raise CustomException(
                statusCode=404,
                detail="UnZIP could not complete.",
                headers={"X-Error": "UnZIP could not complete."},
                callId=callId,
                elapsed=round(time.perf_counter() - start, 5)
            )  
    else:
        # unzip function did not return the expected fields
        raise CustomException(
            statusCode=417,
            detail="UnZIP did not return the expected fields.",
            headers={"X-Error": "UnZIP did not return the expected fields."},
            callId=callId,
            elapsed=round(time.perf_counter() - start, 5)
        )    

    elapsed = round(time.perf_counter() - start, 5)
    fWriteLog(callId, fName, f"END Call. Duration: {str(elapsed)}", "info")

    return jsonable_encoder(response)