// Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates

// Permission is hereby granted, free of charge, to any person obtaining a copy 
// of this software and associated documentation files (the "Software"), to 
// deal in the Software without restriction, including without limitation the 
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
// sell copies of the Software, and to permit persons to whom the Software is 
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in 
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
// DEALINGS IN THE SOFTWARE.

const axios = require('axios');
const { exit } = require('process');

const args = process.argv.slice(2);
const uuid = args[0];
const email = args[1];
const password = args[2];

const data = JSON.stringify({
  "email": email,
  "password": password
});
const base_url = 'https://api.lyve.seagate.com/' + uuid;

let token = null;

async function login() {
  let response = await axios.post(base_url+'/udx/v1/login', data, {headers: {'Content-Type': 'application/json'}});
  let token = response.data.token;
  return token;
}

async function getHelper(jwt, url, filters) {
  const config = {
    method: 'get',
    url: base_url + url,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + jwt
    },
    params: filters
  };

  let response = await axios(config);
  return response.data;
}

async function postHelper(jwt, url, data) {
  const config = {
    method: 'post',
    url: base_url + url,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + jwt
    },
    data: data
  };

  let response = await axios(config);
  return response.data;
}

async function getDevices(jwt) {
  return await getHelper(jwt, '/udx/v1/devices');
}

async function getVolumes(jwt, filters) {
  return await getHelper(jwt, '/udx/v1/volumes', filters);
}

async function importData(jwt, sourceUri, destUri, destDeviceId, filterStr='*') {
  const reqData = {
    'sourceUri': sourceUri,
    'destinationUri': destUri,
    'filter': filterStr,
    'deviceId': destDeviceId,
    'orchestrationMode': 'ENTERPRISE_PERFORMANCE'
  };

  return await postHelper(jwt, '/udx/v1/import', reqData );
}
async function start() {
  try {
    let jwt = await login();

    let devices = await getDevices(jwt);
    console.log(JSON.stringify(devices, null, 2));

    let sourceVolumes = await getVolumes(jwt, { 'category': 'NON-UDX' });
    console.log(JSON.stringify(sourceVolumes, null, 2));

    let destVolumes = await getVolumes(jwt, { 'category': 'UDX' });
    console.log(JSON.stringify(destVolumes, null, 2));

    // Select the first volume found on the device. This is
    // where the code needs to be adjusted to select the desired volumes
    // for source and destination.
    sourceUri = sourceVolumes['data'][0]['uri'];
    destUri = destVolumes['data'][0]['uri']
    destDeviceId = destVolumes['data'][0]['deviceId']

    console.log(sourceUri, destUri, destDeviceId)
    importTask = await importData(jwt, sourceUri, destUri, destDeviceId);
    console.log(JSON.stringify(importTask, null, 2));
  } catch(e) {
    console.log(e);
  }
}

start()

