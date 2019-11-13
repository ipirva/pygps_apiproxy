# -*- coding: utf-8 -*-

"""
    Default Variables
"""


def fLoggingVars() -> dict:
    """
        Return logging vars
    """
    variables = dict()
    # the log level accepted
    variables["myLogLevelsShow"] = ["info", "warning", "critical", "debug", "error"]
    variables["myLoggingFilePath"] = "/code/logs/logfile.log"

    return variables

def fMongoDBVars() -> dict:
    """
        Return MongoDB static variables
    """
    variables = dict()
    variables["myMongoDBHost"]="mongodb://mongo:27017/"
    variables["myMongoDB"]="gpsdata"
    variables["myMongoDBUsername"]="gpsdata"
    variables["myMongoDBPassword"]="@b?q^pp98}kQk)Qz"
    variables["myMongoDBCollection"]="gpsdata"

    return variables

def fGPSMessageVars() -> dict:
    """
        Return GPS Data specific variables
        Message example
        {'rOriginLat': xxx, 'uptime': 260584.02, 'rGLONASSsattelitesUsed': 0, 'rStatusGPS': 'Location 3D Fix', 'hostname': 'raspberrypi', 'rOriginLon': xxx, 
        'rGNSSSsattelitesUsed': '7', 'rDestinationLon': xxx, 'publish': {'publish': 3}, 'rAltitude': xxx, 'rGNSSSsattelitesinView': '10', 
        'rDistance': {'cdistance': 0.01, 'units': 'Km', 'distance': 0.0}, 'rOriginTimeUTC': 20191013180849, 'msgid': '4366fe8409149a7312c77490b549747a', 'rUTC': 20191013180857, 
        'rSpeed': 0.0, 'publicIPAddress': 'xxx', 'rDestinationLat': xxx}
    """
    variables = dict()
    # GPS Data Keys
    variables["myGPSDataKeys"] = {'msgid': 'a', 'rAltitude': 'b', 'publish': 'c', 'rDestinationLat': 'd', 'rGNSSSsattelitesinView': 'e', 'rGNSSSsattelitesUsed': 'f', 'rOriginLon': 'g', 'rDistance': 'h', 'rUTC': 'i', 'rGLONASSsattelitesUsed': 'k', 'rOriginTimeUTC': 'l', 'rDestinationLon': 'm', 'rStatusGPS': 'n', 'rSpeed': 'o', 'rOriginLat': 'p', 'uptime': 'r', 'publicIPAddress': 's', 'hostname': 't'}
    # the schema to validate the body data
    variables["msgJSONSchema"] = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$ref": "#/definitions/GPSValues",
        "definitions": {
            "GPSValues": {
                "type": "object",
                "properties": {
                    "rAltitude": {
                        "type": "number"
                    },
                    "rDestinationLat": {
                        "type": "number"
                    },
                    "rDestinationLon": {
                        "type": "number"
                    },
                    "rDistance": {
                        "$ref": "#/definitions/RDistance"
                    },
                    "rOriginLat": {
                        "type": "number"
                    },
                    "rOriginLon": {
                        "type": "number"
                    },
                    "rOriginTimeUTC": {
                        "type": "integer",
                        "minimum": 20181202182023
                    },
                    "rSpeed": {
                        "type": "number",
                        "minimum": 0
                    },
                    "rUTC": {
                        "type": "integer",
                        "minimum": 20181202182023
                    },
                    "rStatusGPS": {
                        "type": "string"
                    },
                    "msgid": {
                        "type": "string"
                    },
                    "uptime": {
                        "type": "number"
                    },
                    "hostname": {
                        "type": "string"
                    },
                    "publicIPAddress": {
                        "type": "string"
                    },
                    "rGLONASSsattelitesUsed": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "rGNSSSsattelitesUsed": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "rGNSSSsattelitesinView": {
                        "type": "integer",
                        "minimum": 0
                    }
                },
                "required": [
                    "rAltitude",
                    "rDestinationLat",
                    "rDestinationLon",
                    "rDistance",
                    "rOriginLat",
                    "rOriginLon",
                    "rOriginTimeUTC",
                    "rSpeed",
                    "rUTC", 
                    "rStatusGPS",
                    "msgid",
                    "uptime",
                    "hostname",
                    "publicIPAddress",
                    "rGLONASSsattelitesUsed",
                    "rGNSSSsattelitesUsed",
                    "rGNSSSsattelitesinView"
                ],
                "title": "GPSValues"
            },
            "RDistance": {
                "type": "object",
                "properties": {
                    "distance": {
                        "type": "number",
                        "minimum": 0
                    },
                    "cdistance": {
                        "type": "number",
                        "minimum": 0
                    },
                    "units": {
                        "type": "string",
                        "enum": [
                            "Km",
                            "m"
                        ]
                    }
                },
                "required": [
                    "distance",
                    "cdistance",
                    "units"
                ],
                "title": "RDistance"
            }
        }
    }

    return variables
