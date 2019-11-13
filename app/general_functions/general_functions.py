# -*- coding: utf-8 -*-

import json, base64, zlib, time
from jsonschema import validate as fEXTJsonValidate

from ..my_config.my_config import fGPSMessageVars

"""
    Functions
"""


def fValidateJSONPayload(msg: dict = None, JSONSchema: dict = None) -> dict:
    """
        Validate JSON Payload against a specified JSON Schema
    """

    fName = fValidateJSONPayload.__name__

    returnMessage = dict()
    returnMessage["functionName"] = fName
    returnMessage["error"] = dict()
    error = returnMessage["error"]
    errId = 0
    returnMessage["success"] = dict()
    success = returnMessage["success"]
    successId = 0

    returnMessage["decoded"] = False

    returnMessage['metrics'] = dict()
    metrics = returnMessage['metrics']

    start = time.perf_counter()

    # verify the provided function's variables
    if msg is None or JSONSchema is None:
        error[errId] = f"Missing function variables."
        errId += 1
    else:
        try:
            # check if the variables are JSON
            json.dumps(msg)
            json.dumps(JSONSchema)
        except Exception as e:
            error[errId] = f"Provided function variables are not in JSON format: {str(e)}. msg type is {type(msg)}. JSONSchema type is {type(JSONSchema)}"
            errId += 1
        else:
            success[successId] = f"Provided function variables are in JSON format."
            successId += 1
            # try validating the message against the provided schema
            try:
                # fEXTJsonValidate demands dict variables
                fEXTJsonValidate(msg, JSONSchema)
            except Exception as e:
                error[errId] = f"Errors validating msg {str(msg)}: {str(e)}"
                errId += 1
            else:
                success[successId] = f"JSON data {str(msg)} correctly validated against the schema."
                successId += 1
                returnMessage["decoded"] = True

        elapsed = time.perf_counter() - start; metrics['elapsed'] = round(elapsed,5)
        return returnMessage

def fJSONUnZip(msg: str = None) -> dict:
    """
        Decompress str message
    """

    fName = fJSONUnZip.__name__
    
    returnMessage = dict()
    returnMessage["functionName"] = fName
    returnMessage["error"] = dict()
    error = returnMessage["error"]
    errId = 0
    returnMessage["success"] = dict()
    success = returnMessage["success"]
    successId = 0

    returnMessage["msg"] = None
    newMsg = None

    returnMessage['metrics'] = dict()
    metrics = returnMessage['metrics']

    start = time.perf_counter()

    try:
        myGPSMessageVars = fGPSMessageVars()
        myGPSDataKeys = myGPSMessageVars["myGPSDataKeys"]
    except Exception as e:
        error[errId] = f"Default variables not defined: {str(e)}"
        errId += 1
        elapsed = time.perf_counter() - start; metrics['elapsed'] = round(elapsed,5)
        return returnMessage

    if msg is not None:
        try:
            msg = str(msg)
            unzipMsg = json.loads(zlib.decompress(base64.b64decode(msg)))
        except Exception as e:
            error[errId] = f"Cannot decompress the message: {str(msg)}. The Error was: {str(e)}"
            errId += 1
        else:
            success[successId] = f"The message {msg} was decompressed: {str(unzipMsg)}"
            successId += 1

            newKeys = {v: k for k, v in myGPSDataKeys.items()}
            try:
                newMsg = dict([(newKeys.get(k), v) for k, v in unzipMsg.items()])
            except Exception as e:
                error[errId] = f"Cannot set the keys {str(newKeys)} for the following message: {str(unzipMsg)}. The Error was: {str(e)}"
                errId += 1
            else:
                success[successId] = f"The keys {str(newKeys)} set to the message {str(unzipMsg)}: {str(newMsg)}"
                successId += 1

    returnMessage["msg"] = newMsg

    elapsed = time.perf_counter() - start; metrics['elapsed'] = round(elapsed,5)
    
    return returnMessage
