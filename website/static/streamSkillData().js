streamSkillData() ;
var message = []; 


var subscribeMsg = {
    "Operation": "subscribe", // create a new subscription
    "Type": "SelfState", // event type to subscribe to
    "DebounceMs": 1000, // send data every 100 milliseconds
    "EventName": "localization", // name of this subscription
  
    
  };
var subMsg = JSON.stringify(subscribeMsg);

var unsubscribeMsg = {
    "Operation": "unsubscribe",
    "EventName": "localization",
  };
var unsubMsg = JSON.stringify(unsubscribeMsg);


function streamSkillData() {
    //Open a WebSocket connection to Misty
  var ws = new WebSocket("ws://192.168.0.102/pubsub");
    ws.onopen = function(event) {
        console.log("WebSocket opened.");
        ws.send(subMsg);
    }

 //Parse and log SkillData messages
 ws.onmessage = function(event) {
    var data = event.data
    //console.log ( data );
    var message = JSON.parse(data).message.occupancyGridCell; 
    console.log (message);
    
    //var message = JSON.parse(event.data).message.occupancyGridCell;
    //message.push(message);

   
    //console.log("ho salvato i file ")
};
ws.onclose = function(event) {
    console.log("WebSocket closed.");
  };
};
