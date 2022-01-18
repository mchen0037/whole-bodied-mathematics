var ws = new WebSocket("ws://localhost:5000/echo");
var app = ggbApplet;

ws.onopen = function() {
   // Web Socket is connected, send data using send()
   ws.send("Message to send");
};

ws.onmessage = function (evt) {
   var received_msg = evt.data;
   // fken python sends single quotes, JS needs double quotes
   // Convert string to Array of Objects
   received_msg = received_msg.replaceAll("'", "\"");
   var parsed = JSON.parse(received_msg);
   console.log(parsed)
   keys = Object.keys(parsed)

   for (var i = 0; i < keys.length; i++) {
     app.evalCommand(`${keys[i]}=(${parsed[keys[i]].x},${parsed[keys[i]].y})`)
   }
};

ws.onclose = function() {
   // websocket is closed.
   alert("Connection is closed...");
};
