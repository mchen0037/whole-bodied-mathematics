# Calibrate Camera Intrinsic to Extrinsic

## Definitions

* *Intrinsic*: The `[x, y, z]` coordinates that are reported from `aruco.estimatePoseSingleMarkers`. This is the location of the AruCo marker based on the camera. The `z` coordinate refers to how far away the object is from the camera.

* *Extrinsic*: The `[x, y, z]` coordinates based in the world. We need to calculate this based on some matrix multiplications. This repository collects data so that we can use a multi-dimensional regression to find the `m` and `b` in `y = mx + b`

## 1. Collect several samples

<center>![Collecting Data](https://github.com/mchen0037/whole-bodied-mathematics/blob/main/assets/collecting_data.gif?raw=true)</center>

After multiple horrendous hours of collecting a few data points by surveying using string and a digital protractor, the idea to just tapethe ground in increments of 100 cmand use those as data points came into my head. This process takes about a total of about 2 hours, as opposed to 2 hours per camera.

* `collect_pictures.py` will take pictures of all cameras and save them into `/images`, whether it sees an aruco marker or not. (this might also be useful for multi-camera calibration in continued development)

Note to self: I originally planned on taking an image for every increment of 50cm, but this was extremely time consuming. I was able to get good results by doing every 100cm, 3 rotations of a single position, and then a few different heights as well.

## 2. Create a dataset out of the samples
* `generate_marker_data.py` looks through the images collected from the file above and scans to see if we can find any AruCo markers. If it can, then we find the estimated position and create `camera_n_data.csv`. This is a CSV file which maps a real world position to the intrinsic position.

## 3. Run a Regression
* [Guoxiang](https://www.github.com/gzhang8)'s `Posegraph.jl` package calculates this for us quickly.
* TODO: Rewrite this in Python or figure out how to write Julia
* Run `generate_icp_jl.py` to generate a Julia file which will calculate a matrix for us to multiple to translate between intrinsic and extrinsic coordinates.
* This matrix will be placed in the [Constants file](https://github.com/mchen0037/whole-bodied-mathematics/blob/main/app/utils/constants/constants.py).
* Once this is calculated, they do not need to be recalculated unless you move the camera.

### Helpful Debugging Tips
* Moving 100cm in the extrinsic should be equivalent to 100cm in the intrinsic. A good test to debug is to check to make sure that calculating the distance between the two points is correct, i.e.:
```
a = [x, y, z] # intrinsic_pose_estimate
b = [x, y, z] # extrinsic_measured_real_world
sqrt( (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) # the result should be about 100cm
```
