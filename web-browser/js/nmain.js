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
var tout = 5



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
var showpopflag=false
var showinfflag=false

var prevmarkersDrones    = L.layerGroup().addTo(map);
var prevmarkersStations  = L.layerGroup().addTo(map);

var DroneInfo =[];
var StationInfo =[];

// Pulls status information from the sim_manager and calls parseData() when ready.
function requestData(url,timeout){ // url example http://127.0.0.1:8000/drone?id=1'
    ////console.log("requestData_called")
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function(){
        if(xmlHttp.readyState == 4 && xmlHttp.status == 200)
            parseData(xmlHttp.responseText,timeout);
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
function updateMap(data,timeout){
    updateMarkers(data,timeout);
    //currentmarkersDrones.clearLayers();
}

// Updates RSU and OBU markers for the new positions.
function updateMarkers(data,timeout){
    // Clear and update markers
    //currentmarkersStations.clearLayers();
    //currentmarkersDrones.clearLayers();



    for(i = 0; i < data.length; i++){
        //console.log(data[i])
        var node = data[i];
        var marker = null;

        if(node['has_arrived']!=null){
            if(node['has_arrived']){
                document.getElementById('Packageinf').innerHTML= "Package arrived to destination:"+node['has_arrived']+"\n\n";
                document.getElementById("Packageinf").style.color = "blue";
            }else{
                document.getElementById('Packageinf').innerHTML= "Package arrived to destination:"+node['has_arrived']+"\n\n";
                document.getElementById("Packageinf").style.color = "red";
            }

        }
        
        if(node['has_package']!=null||node['has_package']!=undefined){
            ////console.log("drone")    
            try {

                ////console.log(node['has_package'])
                if(node['has_package']==true){
                    marker = L.marker([node['lat'],node['lon']], {icon:droneIconpack});
                }
                else{
                    marker = L.marker([node['lat'],node['lon']], {icon:droneIcon});
                }

                const popup = L.popup({
                    closeOnClick: false,
                    autoClose: false
                });
                popup.setContent("ID: "+node['id']+", Drone"+" Has_package: "+node['has_package'] +" Battery:"+node['battery']);
                marker.bindPopup(popup).openPopup();


                //marker.on('click', function() {
                //marker.openPopup();
                //} );

                marker.addTo(currentmarkersDrones);

                // Update 'positions' structure
                positions[node['id']] = new L.LatLng(node['lat'], node['lon']);

                DroneInfo.push(JSON.stringify(node))
            }
            catch(err) {
                //console.log(err)
        }
        }else{
            ////console.log("station")
            try {

                marker = L.marker([node['lat'],node['lon']], {icon:stationIcon});
                const popup = L.popup({
                    closeOnClick: false,
                    autoClose: false
                });
                popup.setContent("ID: "+node['id']+", Station with drones: "+node['drones']);
                marker.bindPopup(popup).openPopup();

                marker.addTo(currentmarkersStations);

                // Update 'positions' structure
                positions[node['id']] = new L.LatLng(node['lat'], node['lon']);
                
                StationInfo.push(JSON.stringify(node))
            }
            catch(err) {
                //console.log(err)
            }
        }
    }
    ////console.log("flag:"+showpopflag);
    if(showpopflag){
        currentmarkersDrones.eachLayer(function (layer) {
            layer.openPopup();
        });
        currentmarkersStations.eachLayer(function (layer) {
            layer.openPopup();
        });
    }
    if(showinfflag){
        document.getElementById('Show_info').innerHTML= "Stations:\n" + StationInfo +"\n\n\nDrones:\n"+ DroneInfo;
        DroneInfo=[];
    }
    if(timeout==0){
        //console.log(currentmarkersDrones.getLayers())
        currentmarkersDrones.clearLayers();
        tout=5;
    }else{
        var j=0
        var arr= currentmarkersDrones.getLayers()
        if(arr.length!=data.length&&node['has_package']!=null){
            for(j; j < data.length; j++){
                //console.log(arr[j])
                currentmarkersDrones.removeLayer(arr[j]);
            }         
        }
        tout--;
    }

}

// Main function called for every received request (data).
function parseData(data,timeout){
    try{
        data = JSON.parse(data);
    }catch(err){
        //console.log("err",err,"data",data);
        return;
    }
    updateMap(data,timeout);
}

function clickShowPop(){
    currentmarkersDrones.eachLayer(function (layer) {
        layer.closePopup();
    });
    currentmarkersStations.eachLayer(function (layer) {
        layer.closePopup();
    });
    //console.log("showpop was clicked")
    showpopflag=!showpopflag;
    //console.log(showpopflag)
}
function clickShowinfo(){
    currentmarkersDrones.eachLayer(function (layer) {
        layer.closePopup();
    });
    currentmarkersStations.eachLayer(function (layer) {
        layer.closePopup();
    });
    //console.log("showinfo was clicked")
    showinfflag=!showinfflag;
    //console.log(showinfflag)
    document.getElementById('Show_info').innerHTML= "";
}



function clearSINFO(){
    StationInfo=[];
    currentmarkersStations.clearLayers();
}
function clearDINFO(){
    DroneInfo=[];
    currentmarkersDrones.clearLayers();
}

requestData('http://127.0.0.1:8000/station',0);
requestData('http://127.0.0.1:8000/drone',0);
setInterval(clearSINFO, 10000);
//setInterval(clearDINFO, 1000);
setInterval(requestData, 10000,'http://127.0.0.1:8000/station',0);
setInterval(requestData, 1000,'http://127.0.0.1:8000/drone',tout);

setInterval(requestData, 10000,'http://127.0.0.1:8000/package',0);