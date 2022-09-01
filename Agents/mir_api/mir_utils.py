#!/usr/bin/env python2 
# coding: utf8
"""
authors: Fabrice DUVAL and Ayman DAMOUN  

Generaly we have three different types of rest commands for the mir (1-get request 2-post request 3-delete request).
important!!!!
To make the robot perform an action, the action must be added to a mission and that mission must be queued.
"""
import requests
import json
import time


MirIp = '10.191.76.55'

class mymir:
    def __init__(self,MirIp):
        self.MirIp = MirIp
        self.default_url = 'http://'+MirIp+'/api/v2.0.0/'
        self.mission_id_moveToPosition = "000000000000000000000000000000000001"
        self.action_id_moveToPosition = "000000000000000000000000000000000001"
        self.mission_moveToPosition = {"guid": self.mission_id_moveToPosition,
                                  "name": "move_to_coordinate", "group_id": "mirconst-guid-0000-0011-missiongroup"}
        self.action_moveToPosition = {"action_type": "move_to_position", "mission_id": self.mission_id_moveToPosition, "priority": 0, "guid": self.action_id_moveToPosition,
                                 "parameters": [{"id": "x", "value": 0}, {"id": "y", "value": 0},
                                                {"id": "orientation", "value": 0}, {
                                                    "id": "retries", "value": 5},
                                                {"id": "distance_threshold", "value": 0.1}]}
        
        self.urls = [self.default_url+"missions",
                    "http://"+MirIp+"/api/v2.0.0/missions/%s/actions" % (self.mission_id_moveToPosition),
                    self.default_url+"status",
                    self.default_url+"mission_queue"]


        self.clear_error = {"clear_error": True}
        self.robot_ready = {"state_id": 3}
        self.liststatus = []
        self.getstatus()

    def get_mir_auth(self):
        # get the Authorization token
        # mir arm token
        mir_auth = 'Basic YWRtaW46NzkzNWUyZGJkYzExMWZkYjhkOTExNjFjMzI3Y2UxNDhhMTRkZDc5MGUxM2Q1MWE5ZjFhMTk3ZTA0M2VhN2QwZg=='
        return mir_auth

    def get_headers(self):
        auth = self.get_mir_auth()
        headers = {'accept': 'application/json', 'Authorization': auth, 'Accept-Language': 'en_US', 'Content-Type': 'application/json'}
        return headers

    def add_to_mission_queue(self,mission = "dc42f7e0-6b8e-11eb-ae10-f44d306ef93b"):
        '''
        Add a mission to the mission queue (default is return to Go Parking)
        '''
        headers = self.get_headers()
        data = {
        "mission_id": mission,
        "priority": 0
        }
        response = requests.post(self.default_url+'mission_queue', headers=headers, json=data)

    def get_mir_status(self):
        '''
        get the current status from the mir robot 
        '''
        headers = self.get_headers()
        response = requests.get(self.default_url+'status', headers=headers)
        # to do save in more elegant way
        try:
    	    with open('mir_status.json', 'w') as fp:
                json.dump(response.text, fp)
        except KeyError as error:
            print("debug: got Error trying to save MiR status on json file")
            return "json-error"
    
    def move_to_position(self,x,y,yaw):
        '''
        Moves the robot to a coordinate in the map 
        for example Go Parking position:
        (x=0.11445918679237366,y=0.12835092842578888,yaw=1.4513847827911377)
        '''
        headers = self.get_headers()
        self.start_mission()
        mission = requests.post(self.urls[0], headers=headers,
                          json=self.mission_moveToPosition)
        action = requests.post(self.urls[1], headers=headers,
                          json=self.action_moveToPosition)
        move_to_coordinate = {"action_type": "move_to_position", "mission_id": self.mission_id_moveToPosition, "priority": 0, "guid": self.action_id_moveToPosition,
                              "parameters": [{"id": "x", "value": x}, {"id": "y", "value": y},
                                             {"id": "orientation", "value": yaw}, {
                                                 "id": "retries", "value": 5},
                                             {"id": "distance_threshold", "value": 0.1}]}
        mission_queue = {"mission_id": self.mission_id_moveToPosition}

        url_1 = self.default_url+"missions/%s/actions/%s" % (
            self.mission_id_moveToPosition, self.action_id_moveToPosition)
        url_2 = self.default_url+"mission_queue"

        q = requests.put(self.urls[0], headers=headers, json=self.clear_error)
        q = requests.put(self.urls[0], headers=headers, json=self.robot_ready)
        q = requests.put(url_1, headers=headers, json=move_to_coordinate)
        q = requests.post(url_2, headers=headers, json=mission_queue)
        ##to do wait until movement is finished method
    

    def go_charging(self):
        '''
        Sends the robot to the charging with V shaped docking 
        '''
        ######## not working for the moment
        headers = self.get_headers()
        data = {
        "mission_id": "mirconst-guid-0000-0020-actionlist00",
        "priority": 0
        }
        response = requests.post(self.default_url+'mission_queue', headers=headers, json=data)

        return

    def getposition(self):
        """ask for current position"""
        headers = self.get_headers()
        reponse = json.loads(requests.get(self.default_url+'status', headers=headers).text)
        return float(reponse['position']['x']), float(reponse['position']['y']), float(reponse['position']['orientation'])

    def getstatus(self):
        """get full sattus"""
        retour = {}
        retour['x'], retour['y'], retour['theta'] = self.getposition()
        headers = self.get_headers()
        reponse = json.loads(requests.get(self.default_url+'status', headers=headers).text)
        retour['map'] = reponse['map_id'] # attention, mauvaise solution
        retour['statusnumber'] = reponse['state_id']
        retour['status_time'] = str(time.mktime(time.strptime('4040-11-14 14:32:30', '%Y-%m-%d %H:%M:%S'))) # to solve
        retour['current_time'] = str(time.time())
        retour['battery'] = float(reponse['battery_percentage'])

        retour['status'] = reponse['state_text']
        retour['rosstatus'] = None
        return retour
    
    def start_mission(self):
        headers = self.get_headers()
        # resumes current mission
        requests.put(self.default_url+'status', headers=headers, json=self.clear_error)
        requests.put(self.default_url+'status', headers=headers, json=self.robot_ready)
        return

    def pause_mission(self):
        headers = self.get_headers()
        # pauses current mission
        robot_ready = {"state_id": 4}
        requests.put(self.default_url+'status', headers=headers, json=robot_ready)
        return
    
    def clear_mission_queue(self):
        # cancels current mission and deletes all queued missions
        headers = self.get_headers()
        q = requests.delete(self.default_url+'mission_queue', headers=headers)
        return