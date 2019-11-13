# PYGPS APIPROXY

FASTAPI python API endpoint  

Main app code:  
* It receives an HTTP POST call with JSON compressed payload
* It decompresses the JSON payload
* It validates JSON schema
* It stores data to MongoDB  

As a frontend the API endpoint has an NGINX reverse proxy and a Gravitee API GW  
Gravitee API GW provides: 
* analytics
* JWT token validation
* SSL tunnel termination
