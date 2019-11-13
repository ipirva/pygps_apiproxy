#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import time

from ..my_config.my_config import fMongoDBVars

"""
    Functions specific to MongoDB actions
"""


def fInsertDB(data: dict = None) -> dict:
    """
        Insert one line in Mongo DB
    """
    fName = fInsertDB.__name__

    returnMessage = dict()
    returnMessage['functionName'] = fName
    returnMessage['error'] = dict()
    returnMessage['success'] = dict()
    error = returnMessage['error']
    success = returnMessage['success']
    errId = 0; successId = 0

    returnMessage['insertedId'] = None
    
    returnMessage['metrics'] = dict()
    metrics = returnMessage['metrics']

    start = time.perf_counter()

    try:
        myMongoDBVar = fMongoDBVars()
        myMongoDB = myMongoDBVar["myMongoDB"]
        myMongoDBHost = myMongoDBVar["myMongoDBHost"]
        myMongoDBUsername = myMongoDBVar["myMongoDBUsername"]
        myMongoDBPassword = myMongoDBVar["myMongoDBPassword"]
        myMongoDBCollection = myMongoDBVar["myMongoDBCollection"]
    except Exception as e:
        error[errId] = f"Default variables not defined: {str(e)}"
        errId += 1
        elapsed = time.perf_counter() - start; metrics['elapsed'] = round(elapsed,5)
        return returnMessage
    else:
        success[successId] = f"DB details used: DB Host - {myMongoDBHost} DB Username - {myMongoDBUsername} DB - {myMongoDB} Collection - {myMongoDBCollection}"
        successId += 1

    if data != None:
        if type(data) != dict:
            error[errId] = f"Received data is incorrect: {str(e)}"
            errId += 1
            elapsed = time.perf_counter() - start; metrics['elapsed'] = round(elapsed,5)
            return returnMessage
        else:
            success[successId] = "Data format looks ok."
            successId += 1
    else:
        error[errId] = "No argument specified."
        errId += 1
        elapsed = time.perf_counter() - start; metrics['elapsed'] = round(elapsed,5)
        return returnMessage

    # client = MongoClient()
    client = MongoClient(myMongoDBHost,
                       username=myMongoDBUsername,
                       password=myMongoDBPassword,
                       retryWrites=True
    )

    try:
        # database
        db = client[myMongoDB]
        # collection
        gpsdata = db[myMongoDBCollection]
        # insert new row
        result = gpsdata.insert_one(data)
    except Exception as e:
        error[errId] = f"Cannot insert data: {str(e)}"
        errId += 1
        elapsed = time.perf_counter() - start; metrics['elapsed'] = round(elapsed,5)
        return returnMessage
    
    try:
        result.inserted_id
    except Exception as e:
        pass
    else:
        success[successId] = str(result.inserted_id)
        successId += 1
        returnMessage['insertedId'] = str(result.inserted_id)
    
    elapsed = time.perf_counter() - start; metrics['elapsed'] = round(elapsed,5)
    return returnMessage