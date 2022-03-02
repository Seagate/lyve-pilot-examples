# lyve-pilot-examples

## Openapi specification

The api-doc.yml file describes the Lyve Pilot API according to the OpenAPI 3.0.0 specification (https://swagger.io/specification/). Tools supporting OpenAPI can be used to consume the YAML file and generate client requests and example code.

## Nodejs examples

A simple script to start an import of a volume. The script assumes that there is a NON-UDX and a UDX volume. It will initiate an import from those volumes found.

### Install

Install the require node js packages

```
$ npm i
```

### Running

The base URL is hardcoded in the example. The instance-uuid is passed in as the first arg and then requires the username and password.

```
$ npm start <instance-uuid> <username> <password>
```  

## Python examples

The python example includes a simple script to start an import for a volume. The script assumes that there is a NON_UDX and a UDX volume. It will initiate an import from those volumes.
There is also a utility script that provides code to handle GET and POST requests along with a login function.

NOTE: All of this code uses python3.

### Install

The python code uses the requests library to make the calls to the API.

```
$ pip install requests
```

### Running 

The base URL is hardcoded in the example. The instance-id is passed in as the first arg and then requires the username and password.

```
$ python getDevices.py <instance-uuid> <username> <password>
```
