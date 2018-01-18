const commandLineArgs = require('command-line-args')
let Promise = require('promise');
 
const optionDefinitions = [
  { name: 'verbose', alias: 'v', type: Boolean },
  { name: 'profile', alias: 'p', type: String, multiple: false, defaultValue: 'default' },
  { name: 'region', alias: 'r', type: String, multiple: false, defaultValue: 'us-east-1' }
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

let my_securitygroups = {};
function getSecurityGroupIds(item, index){
  if (item.GroupName != 'default'){
    my_securitygroups[item.GroupId] = item;
  }
}

function removeUnusedSecurityGroups(item, index) {
  let securitygroups = [item.Groups];
  if(securitygroups.length > 0){
    if (securitygroups[0] != null){
    // if(securitygroups[0].length > 0){
      for( let i = 0; i < securitygroups[0].length; i++ )
      {
          // console.log(securitygroups[0][i]);
          delete my_securitygroups[securitygroups[0][i].GroupId];
      }
    }
  }
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
).then(function(){
  let request =  ec2.describeNetworkInterfaces(params);

  let promise  = request.promise();
  promise.then(
    function(data) {
      /* process the data */
      // console.log(securitygroups);
      myInterfaces = data.NetworkInterfaces;
      data.NetworkInterfaces.map(removeUnusedSecurityGroups)
      // console.log("Oh how did I get here");
    },
    function(error) {
      console.log(err, err.stack); // an error occurred
    }
  ).then(function(){
    // console.log(my_securitygroups);
    // console.log(Object.keys(my_securitygroups));
    Object.keys(my_securitygroups).map((obj) => { 
      console.log(obj, " ", my_securitygroups[obj].GroupName);
    });
    // .map(console.log()));
  });
});
