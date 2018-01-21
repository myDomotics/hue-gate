#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os,json
class ConfigurationError(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)

class Configuration(object):
    def __init__(self, configFileName):
        self._configFileName=configFileName
        self.configuration=False
        self.rawConfig=''
        self._hueBridge=None
        self._hueName=None
        self._mqttServer=None
        self._mqttPort=None
        self._dbHost=None
        self._dbPort=None
        self._dbUser=None
        self._dbPassword=None
        self._dbDatabase=None

        if self._configFileName is not None:
            if os.path.exists(self._configFileName):
                configFile=open(configFileName,'r')
                self.rawConfig=json.load(configFile)
                configFile.close()
            else:
                raise ConfigurationError('Missing configuration file')
        else:
            raise ConfigurationError('Missing configuration file')
    def _getProperty(self,key1,key2):
        if key1 in self.rawConfig:
            if key2 in self.rawConfig.get(key1):
                return self.rawConfig.get(key1).get(key2)
        return None

    @property
    def hueBridge(self):
        if self._hueBridge is None:
            self._hueBridge=self._getProperty('hue','bridge')
        if self._hueBridge is None:
            raise ConfigurationError('Missing hue bridge ip parameter')
        return self._hueBridge
    @property
    def hueName(self):
        if self._hueName is None:
            self._hueName=self._getProperty('hue','name')
        return self._hueName
    @property
    def mqttServer(self):
        if self._mqttServer is None:
            self._mqttServer=self._getProperty('mqtt','server')
        if self._mqttServer is None:
            raise ConfigurationError('Missing mqtt server parameter')
        return self._mqttServer
    @property
    def mqttPort(self):
        if self._mqttPort is None:
            self._mqttPort=self._getProperty('mqtt','port')
        if self._mqttPort is None:
            self._mqttPort=1883
        return self._mqttPort
    @property
    def dbHost(self):
        if self._dbHost is None:
            self._dbHost=self._getProperty('database','dbHost')
        if self._dbHost is None:
            raise ConfigurationError('Missing db host parameter')
        return self._dbHost
    @property
    def dbPort(self):
        if self._dbPort is None:
            self._dbPort=self._getProperty('database','dbPort')
        if self._dbPort is None:
            if self._getProperty('database','type')=='mysql':
                self._dbPort=3306
            else:
                raise ConfigurationError('Missing db port parameter')
        return self._dbPort
    @property
    def dbUser(self):
        if self._dbUser is None:
            self._dbUser=self._getProperty('database','dbUser')
        if self._dbUser is None:
            raise ConfigurationError('Missing db user parameter')
        return self._dbUser
    @property
    def dbPassword(self):
        if self._dbPassword is None:
            self._dbPassword=self._getProperty('database','dbPassword')
        if self._dbPassword is None:
            raise ConfigurationError('Missing db password parameter')
        return self._dbPassword
    @property
    def dbDatabase(self):
        if self._dbDatabase is None:
            self._dbDatabase=self._getProperty('database','dbDatabase')
        if self._dbDatabase is None:
            raise ConfigurationError('Missing db name parameter')
        return self._dbDatabase
