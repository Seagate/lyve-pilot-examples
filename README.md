# lyve-pilot-examples
## Nodejs examples

A simple script to start an import of a volume. The script assumes that there is a NON-UDX and a UDX volume. It will initiate an import from those volumes found.

### Install

Install the require node js packages
$ npm i

### Running

The base URL is hardcoded in the example. The instance-uuid is passed in as the first arg and then requires the username and password.
$ npm start <instance-uuid> <username> <password>
  
