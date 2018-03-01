const commandLineArgs = require('command-line-args')
let Promise = require('promise');
 
const optionDefinitions = [
  { name: 'verbose', alias: 'v', type: Boolean },
  { name: 'profile', alias: 'p', type: String, multiple: false, defaultValue: 'default' },
  { name: 'region', alias: 'r', type: String, multiple: false, defaultValue: 'us-east-1' },
  { name: 'delete', type: Boolean, defaultValue: false }
]

let options = null
try {
  options = commandLineArgs(optionDefinitions);
}
catch (err) {
  console.log(err.message);
  process.exit();
}

let AWS = require('aws-sdk');
let credentials = new AWS.SharedIniFileCredentials({profile: options.profile});
AWS.config.credentials = credentials;

let ec2 = new AWS.EC2({region: options.region});

let params = {
  DryRun: false
};

let VPCS = [];
// let getVPCSPromise = ec2.describeVpcs().promise();
let getVPCSPromise = ec2.describeRouteTables().promise();
getVPCSPromise.then(function(data){
    console.log(JSON.stringify(data));
});