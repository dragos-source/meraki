#This Script will retruve the Network Geo Address with the WAN 1 and WAN2 configuration
#It is using Meraki API
#Dragos Rimis
#29/05/2023



import requests
import json
import csv

def get_provider_name(public_ip):
    response = requests.get(f"https://ipwhois.app/json/{public_ip}")
    data = response.json()
    return data.get("org", "")

API_KEY = input("Enter your API key: ")
ORG_ID = input("Enter your organization ID: ")

# Retrieve organization name
ORG_URL = f"https://api.meraki.com/api/v1/organizations/{ORG_ID}"
headers = {
    "X-Cisco-Meraki-API-Key": API_KEY
}
organization = requests.get(ORG_URL, headers=headers).json()
org_name = organization["name"]

# Retrieve networks in the organization
NETWORKS_URL = f"https://api.meraki.com/api/v1/organizations/{ORG_ID}/networks"
networks = requests.get(NETWORKS_URL, headers=headers).json()

# Store network information
network_info = []

for network in networks:
    network_id = network["id"]
    network_name = network["name"]

    # Retrieve devices for the network
    DEVICE_URL = f"https://api.meraki.com/api/v1/networks/{network_id}/devices"
    devices = requests.get(DEVICE_URL, headers=headers).json()

    for device in devices:
        if device["model"].startswith("MX"):
            serial = device["serial"]
            
            # Get device status and uplink details
            UPLINK_URL = f"https://api.meraki.com/api/v1/organizations/{ORG_ID}/appliance/uplink/statuses?networkIds[]={network_id}"
            uplinks = requests.get(UPLINK_URL, headers=headers).json()
            
            for uplink in uplinks:
                if uplink["serial"] == serial:
                    role = uplink["highAvailability"]["role"]

                    for uplink_info in uplink["uplinks"]:
                        interface = uplink_info["interface"]
                        status = uplink_info["status"]
                        ip = uplink_info["ip"]
                        public_ip = uplink_info["publicIp"]
                        
                        # Retrieve provider name for public IP
                        if public_ip:
                            provider = get_provider_name(public_ip)
                        else:
                            provider = ""

                        # Store network information
                        network_info.append({
                            "Network Name": network_name,
                            "Address": device["address"],
                            "Role": role,
                            "Interface": interface,
                            "Status": status,
                            "IP": ip,
                            "Public IP": public_ip,
                            "Provider": provider
                        })

# Export to CSV
csv_name = input("Enter the CSV filename: ")
with open(csv_name, mode="w", newline="") as file:
    fieldnames = ["Network Name", "Address", "Role", "Interface", "Status", "IP", "Public IP", "Provider"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(network_info)

print(f"Exported network information to {csv_name} successfully.")
