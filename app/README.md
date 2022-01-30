# app

Run `app.py` to run the motion capture system.

This creates a web server which will start the motion capture system and then have a websocket which will continuously spit out the positions of detected aruco markers.

The Client side, [currently using GeoGebra](https://www.geogebra.org/m/qzn6g9ju) will take in these positions as x, y coordinates and then plot those points.

![Image of using System](https://github.com/mchen0037/whole-bodied-mathematics/blob/main/assets/app_example.gif?raw=true)

Most code is written in `utils` folder, under `MocapSystem.py` and `VideoStreamWidget.py`.

## TODO
[] Extend `VideoStreamWidget.py` to have a data collection mode which saves video as the system is running
[] Extend `MocapSystem.py` to have a data collection mode which saves (x,y) positions as the system is running
[] Extend `/show_frames` endpoint in `app.py` to have a front end view of the video stream
[] Multi-camera calibration for improved accuracy
[] Improved README and include more pictures
[] Website explaining project
