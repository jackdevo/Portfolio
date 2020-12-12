"""
File: routePlanner.py
Purpose: Utilise TransportAPI for text based navigation
Author: Jack Devonshire
"""

import os
import sys
import requests
import json
from geopy.geocoders import Nominatim

#API Credentials
appID = os.environ["routePlannerID"]
appKey = os.environ["routePlannerKey"]
baseurl = "http://transportapi.com/v3/uk"

class transport:
    def __init__(self):
        sys.argv
        if len(sys.argv) < 3:
            print('Correct Usage: routePlanner.py "Current Location" "Target Destination"')
        else:
            self.planJourney(sys.argv[1], sys.argv[2])
        
    def getLatLng(self, address): #Converts address into latitude and longitude format
        geolocator = Nominatim(user_agent="App Name N/A")
        location = geolocator.geocode(address)        
        lonlat = "lonlat:" + str(location.longitude) + ',' + str(location.latitude)
        return lonlat

    def getBusDeparturesRaw(self, routeNo, stopCode): #RouteNo = Bus Number, stopCode = Bus stop ATCO Code
        url = baseurl + "/bus/stop/" + stopCode + "/live.json"
        params = {'app_id': appID, 'app_key': appKey}

        response = requests.get(url,  params)
        data = response.json()
        data = data['departures'][routeNo]
        return data


    def planJourneyRaw(self, fromAddress, toAddress): #Returns raw data of routes for specified journey
        params = {
            'app_id': appID,
            'app_key': appKey,
        }
        fromAddress, toAddress = self.getLatLng(fromAddress), self.getLatLng(toAddress)

        url = baseurl + "/public/journey/from/" + fromAddress + "/to/" + toAddress + ".json"
        response = requests.get(url, params)
        data = response.json()

        for a in data['routes']:
            cur = a['route_parts']
            for x in range(0, len(cur)):
                dict = cur[x]
                dict['coordinates'] = ""

        return data['routes']

    def planJourney(self, fromAddress, toAddress):
        raw = self.planJourneyRaw(fromAddress, toAddress)
        for x in range(0, len(raw)):
            route = raw[x]
            print("\nRoute Idea: " + str(x+1) + "\n--------------")
            print("Estimated Duration: " + str(route['duration']) + "\n")

            route = route['route_parts']
            for z in range(0, len(route)):
                cur = route[z]
                if cur['mode'] == "foot":
                    print("Walk to " + cur['to_point_name'] + " (Depart: " + cur['departure_time'] + " Arrive: " + cur['arrival_time'] + ")")
                elif cur['mode'] == "bus":
                    print("Get on the (" + cur['line_name'] + ") Bus at " + cur['departure_time'] + " (Depart: " + cur['departure_time'] + " Arrive: " + cur['arrival_time'] + ")")
                    print("Exit the bus at " + cur['to_point_name'])
                elif cur['mode'] == "train":
                    print("Get on the (" + cur['line_name'] + " Train at " + cur['departure_time'] + "(Depart: " + cur['departure_time'] + " Arrive: " + cur['arrival_time'] + ")")
                    print("Exit the train at " + cur['to_point_name'])
                elif cur['mode'] == "boat":
                    print("Get on the (" + cur['line_name'] + "Boat at " + cur['departure_time'] + "(Depart: " + cur['departure_time'] + " Arrive: " + cur['arrival_time'] + ")")
                    print("Exit the boat at " + cur['to_point_name'])

t = transport()
