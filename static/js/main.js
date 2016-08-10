
function gPoint ( point )
{
  return new google.maps.LatLng(point.latitude,point.longitude);
}

function convertDate (spotDate)
{
  if (spotDate !== undefined)
    {
  var yr1   = parseInt(spotDate.substring(0,4));
  var mon1  = parseInt(spotDate.substring(5,7));
  var dt1   = parseInt(spotDate.substring(8,10));
  var hr1   = parseInt(spotDate.substring(11,13));
  var min1  = parseInt(spotDate.substring(14,16));
  var sec1  = parseInt(spotDate.substring(17,19));

  var date1 = new Date(yr1, mon1-1, dt1,hr1,min1,sec1);

  return date1;
    }
    else
    {
      return new Date();
    }
}

function makeinfobox(pointnum, thispoint, theotherpoint)  {
 var latlnga, latlngb; 
 var distance;
 var infoboxtext;
 var timestamp;
 
 timestamp = convertDate(thispoint.timestamp); // we convert it from ISO format to something more readable
 infoboxtext = String(timestamp);
 if (pointnum > 0)  {  // no point calculating distance on the point
  latlnga =  gPoint(thispoint);
  latlngb = gPoint(theotherpoint);
  distance = google.maps.geometry.spherical.computeDistanceBetween(latlnga, latlngb) / 1610; // convert to miles
  infoboxtext = infoboxtext + "<br />" + distance.toFixed(2) + " miles";
 } 
 return infoboxtext; 
}



function drawPath(points,map)
{
  var trackline = [];
for ( i = 0 ; i < points.length ; i++ )  {
  var point = points[i];
  var contentstring = "Point " + i; 
  var spot = gPoint(point);
  // here we create the text that is displayed when we click on a marker
  var windowtext = makeinfobox(i, points[i], points[i-1]);  // if you tell anybody I did this I'll deny it vehemently
  var marker = new google.maps.Marker( {
   position: spot, 
   map: map,
   scale:3,
   title: points[i].timestamp,
   html: windowtext
  } );
  
  // instantiate the infowindow
  
  var infowindow = new google.maps.InfoWindow( {
  } );

  // when you click on a marker, pop up an info window
  google.maps.event.addListener(marker, 'click', function() {
   infowindow.setContent(this.html);
   infowindow.open(map, this);
  });

  // set up the array from which we'll draw a line connecting the readings
  trackline.push(spot);
 }  
 
 // here's where we actually draw the path 
 var trackpath = new google.maps.Polyline( {
  path: trackline,
  strokeColor: "#FF00FF",
  strokeWeight: 3
 });
 trackpath.setMap(map);
 return trackpath;
}


jQuery(document).ready(function () {

    var lp = start_data[start_data.length-1];

    var last_point = gPoint(lp);

    var options = {
        zoom: 8,
        center: last_point,
        mapTypeId: google.maps.MapTypeId.HYBRID
    };
    
    var map = new google.maps.Map($('#map')[0], options);
    map.setOptions({
        //styles: style
    });
    path = drawPath(start_data,map);

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });
    socket.on('new points',function(data){
      console.log(data);
      $('newpoints').append($('span').html(JSON.stringify(data)));
    });

    window.socket = socket;
    window.path = path;
    window.map = map;

});
