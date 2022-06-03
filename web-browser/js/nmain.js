const obuIcon = L.icon({
    iconUrl: 'img/blue-circle.png',
    iconSize: [10, 10],
    iconAnchor: [5, 5]
});
const rsuIcon = L.icon({
    iconUrl: 'img/yellow-circle.png',
    iconSize: [10, 10],
    iconAnchor: [5, 5]
});
const droneIcon = L.icon({
    iconUrl: 'img/drone.png',
    iconSize: [25, 25],
    iconAnchor: [5, 5]
});
const droneIconpack = L.icon({
    iconUrl: 'img/fdrone.png',
    iconSize: [25, 25],
    iconAnchor: [5, 5]
});
const stationIcon = L.icon({
    iconUrl: 'img/station.png',
    iconSize: [25, 25],
    iconAnchor: [5, 5]
});
const packageIcon = L.icon({
    iconUrl: 'img/package.png',
    iconSize: [20, 20],
    iconAnchor: [5, 5]
});

//var mark=null
//mark =L.marker([40.64,-8.65],{icon:droneIcon})
//
//mark.addTo(currentmarkersOBU)



//var map = L.map('mapid').setView([41.16,-8.6], 13); // Start centered in Porto
var map = L.map('mapid').setView([40.64,-8.65], 14.5); // Start centered in Aveiro
L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoicmljYXJkbzAzYyIsImEiOiJjanZhNHF4N2QwdXZxM3lucmJtcTVvZDdzIn0.37cwnhfRcjk3cVN0HQugsQ',
{attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
maxZoom: 16,
minZoom: 11,
tileSize: 512,
zoomOffset: -1,
id: 'mapbox/dark-v10',
accessToken: 'pk.eyJ1IjoicmljYXJkbzAzYyIsImEiOiJjanZhNHF4N2QwdXZxM3lucmJtcTVvZDdzIn0.37cwnhfRcjk3cVN0HQugsQ'
}).addTo(map);
var currentmarkersDrones    = L.layerGroup().addTo(map);
var currentmarkersStations  = L.layerGroup().addTo(map);
var graph                   = L.layerGroup().addTo(map);
var positions = {};     // {id:[lat,lon],...} - Current position of each node
var progressIDs = [];   // List with progress bar's IDs
var doneList = {};      // nodes that have finished the transfer
var startedList = {};   // nodes that have started the transfer
var currentTS = 0;



// Pulls status information from the sim_manager and calls parseData() when ready.
function requestData(url){ // url example http://127.0.0.1:8000/drone?id=1'
    console.log("requestData_called")
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function(){
        if(xmlHttp.readyState == 4 && xmlHttp.status == 200)
            parseData(xmlHttp.responseText);
    }
    xmlHttp.open( "GET",url, true);
    xmlHttp.send( null );
}

// Helper function to change a 'domID' text field to 'text'.
function changeText(domID,text){
    // Compares previous value with the new one to prevent needless refreshes.
    if (document.getElementById(domID).innerText != text){
        document.getElementById(domID).innerText = text;
    }
}

// Make required changes in the map, according to the new data.
function updateMap(data){
    updateMarkers(data);
}

// Updates RSU and OBU markers for the new positions.
function updateMarkers(data){
    // Clear and update markers
    currentmarkersDrones.clearLayers();
    currentmarkersStations.clearLayers();
    for(i = 0; i < data.length; i++){
        console.log(data[i])
        var node = data[i];
        var marker = null;


        console.log(node['lat'])
        console.log(node['lon'])

        marker = L.marker([node['lat'],node['lon']], {icon:droneIcon});
        marker.bindPopup("ID: "+node['id']+", Drone").openPopup();
        marker.addTo(currentmarkersDrones);
     
        // Update 'positions' structure
        positions[node['id']] = new L.LatLng(node['lat'], node['lon']);
    }
}

// Main function called for every received request (data).
function parseData(data){
    try{
        data = JSON.parse(data);
    }catch(err){
        console.log("err",err,"data",data);
        return;
    }
    updateMap(data);
}

setInterval(requestData, 800,'http://127.0.0.1:8000/drone');
