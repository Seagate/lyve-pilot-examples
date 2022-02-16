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
    'orchestrationMode': 'STANDARD_SECURITY'
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

