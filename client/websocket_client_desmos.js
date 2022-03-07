function getColor(id) {
  color = Desmos.Colors.BLACK;
  if (id == 1) {
    color = Desmos.Colors.RED;
  }
  else if (id == 2) {
    color = Desmos.Colors.BLUE;
  }
  else if (id == 3) {
    color = Desmos.Colors.GREEN;
  }
  else if (id == 4) {
    color = Desmos.Colors.PURPLE;
  }
  else if (id == 5) {
    color = Desmos.Colors.ORANGE;
  }
  return color;
}

function create_web_socket_connection() {
  // This code is run on the client end
  var ws = new WebSocket("ws://localhost:5000/echo");

  ws.onopen = function() {
     // Web Socket is connected, send data using send()
     for (var i = 0; i < 10; i++) {
       Calc.removeExpression({id: `P_{${i}}`});
     }
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
    s_list_latex = `S=\\left[`
    // Update the position of each individual point
    for (var i = 0; i < keys.length; i++) {
      color = getColor(keys[i]);
      Calc.setExpression({
        "id": `P_{${keys[i]}}`,
        "latex": `P_{${keys[i]}}=(${parsed[keys[i]].x}, ${parsed[keys[i]].y})`,
        "dragMode": Desmos.DragModes.NONE,
        "color": color,
        "folderId": "student_points",
      })
      if (i == 0) {
        s_list_latex = s_list_latex + `P_{${keys[i]}}`
      }
      else {
        s_list_latex = s_list_latex + `,P_{${keys[i]}}`
      }
    }
    s_list_latex = s_list_latex + `\\right]`
    // Update the list of student points -- handles if a kid disappears or comes back
    Calc.setExpression({
      "type": "expression",
      "id": "s_list",
      "latex": s_list_latex,
      "hidden": true,
      "folderId": "student_points",
    })
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
