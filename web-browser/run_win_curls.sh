#!/bin/bash
x=40.634143433650856
#40.634143433650856, -8.631619736734109
i=0
while [ $i -le 500 ]
do
  curl -X 'POST' \
    'http://127.0.0.1:8000/drone' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "id": "string",
    "lat":'$x',
    "lon": -8.631619736734109,
    "has_package": true
  }'
 sleep 1
 x=$(echo $x + 0.0003 | bc)
 i=$(( $i + 1 ))
 echo $x 
 
 done