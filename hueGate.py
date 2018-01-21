#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
mqtt to Philips Hue bridge
--------------------------
use json configuration file
node name : hue
topic structure : hue/+
parameters: configuration file name (json)
"""
"""
Documentation
Gamut:
https://developers.meethue.com/documentation/supported-lights

http://openrb.com/control-philips-hue-lamps-with-logicmachine/
"""
"""
Topic structure:
-------------------------------------------------------------------------------------------------------------------
| Topic                                   |Message                  |Description                                  |
-------------------------------------------------------------------------------------------------------------------
|hue/set/lights/<lampname>                |0-254                    |0 will set off, other set brightness to value|
|hue/set/lights/<lampname>                |on, off                  |set the light on or off                      |
|hue/set/lights/<lampname>                |json encoded             |will set parameter as defined bellow         |
on: boolean (True,False)
bri: current brightness 1..254
hue: hue from 0..65535
sat: saturation from 0..254
alert: none,select,lselect
transitiontime: duration multiple of 100ms
colorName: see hueColor dictionnary
effect: none,colorloop

NOT IMPLEMENTED:
xy: an array of floats containing the coordinates (0..1) in CIE colorspace
ct: Mired color temperature (153..500)
bri_inc: Increments or decrements the value of the brightness
sat_inc: Increments or decrements the value of the sat
hue_inc: Increments or decrements the value of the hue
ct_inc: Increments or decrements the value of the ct
xy_inc:  Increments or decrements the value of the xy

examples :
---------------------------------------------------------------------------------------------------------------------
|Topic                                         |Message                                                             |
---------------------------------------------------------------------------------------------------------------------
|hue/set/lights/Droite                         |{"on":true}                                                         |
|hue/set/lights/Droite                         |{"on":true,"colorName":"blue"}                                      |
|hue/set/lights/Droite                         |{"alert":"select"}                                                  |
mosquitto_pub -h 192.168.0.26 -p 1883 -t 'hue/set/lights/Droite' -m '{"colorName":"blue","on":true}'

"""
import os, sys,platform,re,json,time
from Configuration_library import Configuration, ConfigurationError
from phue import Bridge
import paho.mqtt.client as mqtt
lampNames=['Droite','Gauche','Milieu']
hueColor={'blue':43179,'green':27873,'yellow':17538,'red':63928,'purple':54756,'white':39746,'orange':6157,'lightBlue':39741}
topicRegex=re.compile(r'hue/set/lights/S*')
def getConfigFileName():
    # get the configuration file name
    if platform.system() == 'Windows':
        USER_HOME = 'USERPROFILE'
    else:
        USER_HOME = 'HOME'
    if len(sys.argv)>1 and sys.argv[1] is not None:
        config_file_name=sys.argv[1]
    elif os.getenv(USER_HOME) is not None and os.access(os.getenv(USER_HOME), os.W_OK):
        config_file_name=os.path.join(os.getenv(USER_HOME), 'domotique.config')
    else:
        os.path.join(os.getcwd(), 'domotique.config')
    if os.path.exists(config_file_name):
        return config_file_name
    else:
        raise ConfigurationError('Missing configuration file')
        return None
def setLight(bridge,topic,message):
    if topicRegex.match(topic):
        lampName=topic.split('/')[3]
        if lampName in lampNames:
            if message.isdigit():
                if int(message)==0:
                    bridge.set_light(lampName,'on',False)
                elif int(message)<254:
                    bridge.set_light(lampName, 'on', True)
                    bridge.set_light(lampName, 'bri', int(message))
            elif message=='on':
                bridge.set_light(lampName, 'on', True)
            elif message=='off':
                bridge.set_light(lampName, 'on', False)
            else:
                try:
                    jsonMessage=json.loads(message)
                    if 'on' in jsonMessage:
                        if jsonMessage.get('on')==True or jsonMessage.get('on')==False:
                            bridge.set_light(lampName,'on',jsonMessage.get('on'))
                    if 'colorName' in jsonMessage:
                        color=jsonMessage.get('colorName')
                        if color in hueColor:
                            bridge.set_light(lampName,'hue',hueColor.get(color))
                            if color=='white':
                                bridge.set_light(lampName,'sat',0)
                            else:
                                bridge.set_light(lampName, 'sat', 254)
                    if 'sat' in jsonMessage:
                        if jsonMessage.get('sat').isdigit():
                            saturation=int(jsonMessage.get('sat'))
                            if saturation>=0 and saturation<=254:
                                bridge.set_light(lampName,'sat',saturation)
                    if 'bri' in jsonMessage:
                        if jsonMessage.get('bri').isdigit():
                            brightness=int(jsonMessage.get('bri'))
                            if brightness>=0 and brightness<=254:
                                bridge.set_light(lampName,'bri',brightness)
                    if 'alert' in jsonMessage:
                        alerteType=jsonMessage.get('alert')
                        if alerteType in ['none','select','lselect']:
                            bridge.set_light(lampName,'alert',alerteType)
                    if 'transitiontime' in jsonMessage:
                        if jsonMessage.get('transitiontime').isdigit():
                            bridge.set_light(lampName,'transitiontime',int(jsonMessage.get('transitiontime')))
                    if 'colorloop' in jsonMessage:
                        if jsonMessage.get('colorloop')=='on':
                            bridge.set_light(lampName,'effect','colorloop')
                        else:
                            bridge.set_light(lampName, 'effect', 'none')

                except:
                    pass

    else:
        print 'Invalid topic '+topic

def on_connect(client,userdata,flags,rc):
    mqClient.subscribe('hue/set/lights/+')

def on_message(client, userdata, msg):
    setLight(b,msg.topic,msg.payload)

if __name__ == '__main__':
    configFile=getConfigFileName()
    try:
        config=Configuration(configFile)
    except ConfigurationError as er:
        print er.value
    

    b=Bridge(config.hueBridge,config.hueName)
    b.connect()
    
    
    mqClient = mqtt.Client()
    mqClient.on_connect = on_connect
    mqClient.on_message = on_message
    mqClient.connect(config.mqttServer, config.mqttPort, 60)
    mqClient.loop_forever()
