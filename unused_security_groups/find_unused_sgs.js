const commandLineArgs = require('command-line-args')
let Promise = require('promise');
 
const optionDefinitions = [
  { name: 'verbose', alias: 'v', type: Boolean },
  { name: 'profile', alias: 'p', type: String, multiple: false, defaultValue: 'default' },
  { name: 'region', alias: 'r', type: String, multiple: false, defaultValue: 'us-east-1' }
]

const options = commandLineArgs(optionDefinitions)

let AWS = require('aws-sdk');

let credentials = new AWS.SharedIniFileCredentials({profile: options.profile});
AWS.config.credentials = credentials;

let ec2 = new AWS.EC2({region: options.region});

let params = {
  DryRun: false
};

let securitygroups = {};
function getSecurityGroupIds(item, index){
  console.log(item);
  securitygroups[item.GroupId] = 0;
}

function getSecurityGroupID(item, index) {
  let securitygroups = [item.Groups];
  console.log(securitygroups)
  return securitygroups;
}

let sgrequest = ec2.describeSecurityGroups(params);
let sgpromise = sgrequest.promise();
sgpromise.then(
  function(data) {
    /* process the data */
    data.SecurityGroups.map(getSecurityGroupIds);
  
  },
  function(error) {
    console.log(err, err.stack); // an error occurred
  }
) .then(function(){
  let request =  ec2.describeNetworkInterfaces(params);

  let promise  = request.promise();
  promise.then(
    function(data) {
      /* process the data */
      console.log(securitygroups);
      myInterfaces = data.NetworkInterfaces;
      // data.NetworkInterfaces.map(getSecurityGroupID)
      console.log("Oh how did I get here");
    },
    function(error) {
      console.log(err, err.stack); // an error occurred
    }
  ).then(function(){
    console.log("Last do this");
  });

});





// let request =  ec2.describeSecurityGroups(params, function(err, data){
//     if(err) console.log(err, err.stack); // an error occurred
//     console.log("Getting Security Groups")
//   });

// // create the promise object
// let promise = request.promise();

// let ENIs = promise.then(getNetworking, null)
// let pages = 1;
// ec2.describeNetworkInterfaces(params).eachPage( function(err, data){
//     if (err) console.log(err, err.stack); // an error occurred
//     else{
//       console.log("Page", pages++);
//       console.log("Size is", data.NetworkInterfaces.length );
//       // console.log(data); 
//       // data.NetworkInterfaces.map(getSecurityGroupID)

//     }    
// });

// // call EC2 to retrieve policy for selected bucket
// ec2.describeInstances(params, function(err, data) {
//     if (err) {
//       console.log("Error", err.stack);
//     } else {
//       console.log("Success", JSON.stringify(data));
//     }
//   });
