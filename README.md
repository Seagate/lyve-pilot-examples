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
