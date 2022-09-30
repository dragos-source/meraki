#!/bin/bash
#this script will list all clients accross selected organisation 
#Dragos Rimis
#29 September 2022

read -p 'Please provide the Base URL for Meraki API: ' url
read -p 'Please provide your Meraki API key: ' api_key
read -p 'Provide the file name to store the output in csv format: ' filename
echo 'Getting the list of Organisations you are allowed to read:'
curl -s ${url}/api/v1/organizations -H "X-Cisco-Meraki-API-Key: ${api_key}" | jq -r ".[] |[.name, .id] | join(\",\")" | column -ts ','
read -p 'Provide the organization ID from the list above: ' organizationId

#get networks in the organisation
curl -s ${url}/api/v1/organizations/${organizationId}/networks -H "X-Cisco-Meraki-API-Key: ${api_key}" | jq -r ".[] | [.name, .id] | join(\";\")"| while IFS=';' read -r network network_id 
    do
       curl -s -L --request GET --url ${url}/api/v1/networks/${network_id}/clients?perPage=1000  --header "X-Cisco-Meraki-API-Key: ${api_key}" | jq -r '.[] |[.mac, .description, .ip, .manufacturer, .recentDeviceName, .recentDeviceConnection, .switchport] | join(";")' | while IFS=';' read -r mac description ip namufacturer recentDeviceName recentDeviceConnection switchport
        do 
            echo "${network};${network_id};${mac};${description};${ip};${namufacturer};${recentDeviceName};${recentDeviceConnection};${switchport}" >> ${filename}
        done    
    done
echo 'The Output is ready. Please check the output file'