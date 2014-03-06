#coding: utf-8

# Copyright 2014, Radhika S. Saksena (radhika dot saksena at gmail dot com)
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

import time
import json
import os
import sys
import re
import codecs
from tweepy.streaming import StreamListener
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import pygmaps
import webbrowser
#import MapTweet

"""Set of functions that use the GoogleMaps API to geocode and map tweets."""

def geocodeTweet(jsonStr,gcCount,flog):
    """This method geocodes tweets and does one of the following:
    (1) returns tweet's coordinates or (2) returns tweeter's geocoded loc
    or (3) check if it's a retweet and return orig tweeter's loc or
    (4) finally, gc failed and return ["-99999","-99999"]"""
    coordinates = ["-99999","-99999"]
    try:
        if(jsonStr["coordinates"]):
            coordinates = jsonStr["coordinates"]["coordinates"]
        else:
            location = jsonStr["user"]["location"]
            coordinates = Geocoder.geocode(location)[0].coordinates
            gcCount += 1
    except GeocoderError,e:
        flog.write("GeocoderError exception is: %s\n" % e)
        pass
    except Exception,e:
        flog.write("Other exception is: %s\n" % e)
        pass
    return coordinates

def initMap(ofile,useBrowser):
    """Set up Google Maps"""
    # centre map on Greenwich
    twMap = pygmaps.maps(51.20,0.0,2.8)
    twMap.draw(os.getcwd() + "/" + ofile)
    if useBrowser:
            if(re.search("linux",sys.platform)):
                print "os is linux"
                controller = webbrowser.get("firefox")
            elif(re.search("darwin",sys.platform)):
                print "os is darwin"
                controller = webbrowser.get("safari")
            elif(re.search("os/2",sys.platform,re.IGNORECASE)):
                print "os is os/2"
                controller = webbrowser.get("safari")
            else:
                print "os recognized, trying to get default browser."
                controller = webbrowser.get()
    else:
            controller = None
    return (twMap,controller)

def updateMap(twMap,ofile,cnew,drawFlag,cStr):
    """Update map with a new tweet's coordinates"""
    twMap.addradpoint(cnew[0],cnew[1],60000,cStr)
    if(drawFlag):
        twMap.draw(os.getcwd() + "/" + ofile)
