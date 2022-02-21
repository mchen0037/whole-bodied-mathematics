function create_web_socket_connection() {
  // This code is run on the client end
  var app = calculator;
  var ws = new WebSocket("ws://localhost:5000/echo");

  ws.onopen = function() {
     // Web Socket is connected, send data using send()
     document.getElementById("status-icon").className = "bi bi-record-fill"
     document.getElementById("status-icon").style.color = "red"
     var buttonStart = document.getElementById("connect-web-socket-button")
     buttonStart.style.display = "none"
     var buttonStop = document.getElementById("stop-websocket")
     buttonStop.style.display = "inline"
     buttonStop.onclick = function() {
       if (ws.readyState === WebSocket.OPEN) {
         console.log("Closing..")
         ws.close();
       }
     }
  };

  ws.onmessage = function (evt) {
     var received_msg = evt.data;
     // Python sends single quotes, JS needs double quotes
     // Convert string to Array of Objects
     received_msg = received_msg.replaceAll("'", "\"");
     var parsed = JSON.parse(received_msg);
     keys = Object.keys(parsed)

     for (var i = 0; i < keys.length; i++) {
       app.setExpression({
         "id": `P_{${keys[i]}}`,
         "latex": `P_{${keys[i]}}=(${parsed[keys[i]].x}, ${parsed[keys[i]].y})`,
         "dragMode": Desmos.DragModes.NONE
       })
     }
  };

  ws.onclose = function() {
     // websocket is closed.
     status_icon_element = document.getElementById("status-icon")
     status_icon_element.style.color = "black"
     status_icon_element.className = "bi bi-pause-circle"
     var buttonStart = document.getElementById("connect-web-socket-button")
     buttonStart.style.display = "inline"
     var buttonStop = document.getElementById("stop-websocket")
     buttonStop.style.display = "none"
  };

  window.addEventListener("unload", function () {
    if(ws.readyState === WebSocket.OPEN) {
      console.log("closing!")
        ws.close();
    }
  });
}
