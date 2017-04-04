Spot Tracker 
=================
Using the SPOT API with Google Maps


This was written to populate a custom Google Maps layer with data points accessible from the SPOT API

Requires an active SPOT account.

Features
---------

- Runs a periodic task in another thread to get the latest data point
- Shows where the night was spent by changing the marker
- Websockets update add new data points live, but there is an issue where the page will go stale if left in the background. A reload is needed to get all new points.

