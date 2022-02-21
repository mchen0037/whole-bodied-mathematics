// This code is run on the client end
var ws = new WebSocket("ws://localhost:5000/echo");
var app = Calc;

ws.onopen = function() {
   // Web Socket is connected, send data using send()
   ws.send("Message to send");
};

ws.onmessage = function (evt) {
   var received_msg = evt.data;
   // fken python sends single quotes, JS needs double quotes
   // Convert string to Array of Objects
   // console.log(received_msg)
   received_msg = received_msg.replaceAll("'", "\"");
   var parsed = JSON.parse(received_msg);
   keys = Object.keys(parsed)

   for (var i = 0; i < keys.length; i++) {
     // console.log(`P_{${keys[i]}}=(${parsed[keys[i]].x},${parsed[keys[i]].y})`)
     app.setExpression({
       "id": `P_{${keys[i]}}`,
       "latex": `P_{${keys[i]}}=(${parsed[keys[i]].x}, ${parsed[keys[i]].y})`
     })
     // app.evalCommand(`P_{${keys[i]}}=(${parsed[keys[i]].x},${parsed[keys[i]].y})`)
   }
};

ws.onclose = function() {
   // websocket is closed.
   alert("Connection is closed...");
};
