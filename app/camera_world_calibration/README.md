# Calibrate Camera Intrinsic to Extrinsic

## Definitions

* *Intrinsic*: The `[x, y, z]` coordinates that are reported from `aruco.estimatePoseSingleMarkers`. This is the location of the AruCo marker based on the camera. The `z` coordinate refers to how far away the object is from the camera.

* *Extrinsic*: The `[x, y, z]` coordinates based in the world. We need to calculate this based on some matrix multiplications. This repository collects data so that we can use a multi-dimensional regression to find the `m` and `b` in `y = mx + b`

## 1. Collect several samples
![Collecting Data](https://www.github.com/mchen0037/whole-bodied-mathematics/assets/collecting_data.gif)
After multiple horrendous hours of collecting a few data points by surveying using string and a digital protractor, the idea to just tape the ground and use those as data points came into my head. This process takes about ~2 hours, as opposed to 2 hours per camera.

* `collect_pictures.py` will take pictures of all
