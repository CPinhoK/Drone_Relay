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
var currentmarkersOBU = L.layerGroup().addTo(map);
var currentmarkersRSU = L.layerGroup().addTo(map);
var currentmarkersOBU = L.layerGroup().addTo(map);
var graph             = L.layerGroup().addTo(map);
var positions = {};     // {id:[lat,lon],...} - Current position of each node
var progressIDs = [];   // List with progress bar's IDs
var doneList = {};      // nodes that have finished the transfer
var startedList = {};   // nodes that have started the transfer
var currentTS = 0;

// Handles START button click - id="btn_start"
// Calls /start and blocks.
function clickStart(){
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "/start", true);
    xmlHttp.send( null );
    document.getElementById("btn_start").disabled = true;
}

// Handles STOP button click - id="btn_stop"
function clickStop(){
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "/stop", true);
    xmlHttp.send( null );
    document.getElementById("btn_start").disabled = false;
    window.location.reload(false);
}

// Pulls status information from the sim_manager and calls parseData() when ready.
function requestData(){
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function(){
        if(xmlHttp.readyState == 4 && xmlHttp.status == 200)
            parseData(xmlHttp.responseText);
    }
    xmlHttp.open( "GET", "/status", true);
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
    //updateGraph(data);
}

// Updates RSU and OBU markers for the new positions.
function updateMarkers(data){
    // Clear and update markers
    currentmarkersOBU.clearLayers();
    currentmarkersRSU.clearLayers();
    for(i = 0; i < data.length; i++){
        if('timestamp' in data[i]){
            continue;
        }
        var node = data[i];
        var marker = null;
        if (node['rsu'] == 1){40.64,-8.65
            marker = L.marker([node['lat'],node['lon']], {icon:rsuIcon});
            marker.bindPopup("ID: "+node['id']+", RSU").openPopup();
            marker.addTo(currentmarkersRSU);
        }else{
            marker = L.marker([node['lat'],node['lon']], {icon:obuIcon});
            marker.bindPopup("ID: "+node['id']).openPopup();
            marker.addTo(currentmarkersOBU);
        }
        // Update 'positions' structure
        positions[node['id']] = new L.LatLng(node['lat'], node['lon']);
    }
}

// Updates the lines between nodes (graph)
function updateGraph(data){
    graph.clearLayers();
    //let positions = {}; // {id:[lat,lon],...}
    for(i = 0; i < data.length; i++){
        if('timestamp' in data[i]){
            continue;
        }
        let me = data[i]['id'];
        let neighbours = data[i]['neighbours'];

        for(j = 0; j < neighbours.length; j++){
            // Draw a line between 'me' and 'n'
            let n = neighbours[j];
            if(n in positions){
                let points = [];
                points.push(positions[me]);
                points.push(positions[n]);
                var line = new L.Polyline(points, {
                    color: 'white',
                    weight: 3,
                    opacity: 0.7,
                    smoothFactor: 1
                });
                line.addTo(graph);
            }
        }
    }
}

// Updates progress bars, according to the new data.
function updateProgress(data){
    for(i = 0; i < data.length; i++){
        let node = data[i];
        if ('timestamp' in node){
            // Update timestamp
            changeText("sim_ts",node['timestamp']+"s");
            currentTS = node['timestamp'];
            continue;
        }
        let id = node['id']
        // Check if progress bar exists
        if (progressIDs.includes(id)){
            // If progress bar is already there, update it.
            let prog = parseFloat(node['d_now'])/parseFloat(node['d_total'])*100;
            prog = prog.toFixed(0);

            let injection = '<div class="progress-bar" role="progressbar" ';
            if (node['rsu'] == 0){
                injection += `aria-valuenow="${prog}" aria-valuemin="0" aria-valuemax="100" style="width:${prog}%">${prog}%</div>`;
            }else{
                injection += `aria-valuenow="${prog}" aria-valuemin="0" aria-valuemax="100" style="width:${prog}%; background-color: rgb(255, 251, 44); color: black">${prog}%</div>`;
            }
            document.getElementById("sim_progress").children[progressIDs.indexOf(id)].children[0].innerHTML = injection;

            if(prog != 100){
                // Calculate download speed and update.
                let speed = parseFloat(node['d_speed']/1000).toFixed(2);
                let delta = currentTS - startedList[id];
                document.getElementById("sim_progress").children[progressIDs.indexOf(id)].children.info.innerText = speed + " kB/s " + delta +"s";
                
                if (!(id in startedList)){
                    startedList[id] = currentTS;
                }
            }else{
                // Progress is 100%
                // Register timestamp in done list.
                if (!(id in doneList)){
                    doneList[id] = currentTS;
                    let delta = currentTS - startedList[id];
                    document.getElementById("sim_progress").children[progressIDs.indexOf(id)].children.info.innerText = " Done:"+
                    delta+"s";
                }
            }
        }else{
            // Create a new progress bar.
            let prog = 0;
            let injection = `<div id="${id}">`;
            injection += `${id}:`;
            injection += '<div class="progress"><div class="progress-bar" role="progressbar" ';
            if (node['rsu'] == 0){
                injection += `aria-valuenow="${prog}" aria-valuemin="0" aria-valuemax="100" style="width:${prog}%">${prog}%</div>`;
            }else{
                injection += `aria-valuenow="${prog}" aria-valuemin="0" aria-valuemax="100" style="width:${prog}%; background-color: rgb(255, 251, 44); color: black">${prog}%</div>`;
            }
            injection += '</div>';
            injection += '<div id="info">0 kB/s</div><hr></div>';
            document.getElementById("sim_progress").innerHTML += injection;
            progressIDs.push(id);
        }
    }
}

// Main function called for every received request (data).
function parseData(data){
    try{
        data = JSON.parse(data);
    }catch(err){
        changeText("sim_status",data);
        return;
    }
    changeText("sim_status","Simulation running.");
    updateMap(data);
    updateProgress(data);
}

setInterval(requestData, 5000);
