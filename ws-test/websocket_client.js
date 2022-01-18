var ws = new WebSocket("ws://localhost:5000/echo");
var calc = Calc.getState()
expressions_list = calc.expressions.list;
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
   var points_list = [];
   for(var i in parsed) {
     points_list.push(parsed[i]);
   }

   // Update each point (put them into Desmos first)
   for (i = 0; i < points_list.length; i++) {
     expressions_list[i].latex = `P_{${i}}=\\left(${points_list[i].x},${points_list[i].y}\\right)`
   }

   // Update the Calculator State
   Calc.setState(calc)
};

ws.onclose = function() {
   // websocket is closed.
   alert("Connection is closed...");
};
