# Copyright 2014, Radhika S. Saksena (radhika dot saksena at gmail dot com)
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

# Web scraping and text processing with Python workshop

import tweepy
import time
import codecs
import sys
import os
import re
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import pygmaps
import webbrowser

"""Build a network of friends for a given list of Twitter users."""

ckey = " " #consumer key
csecret = " " #conumer scret
atoken = " " # access token
asecret = " " #access secret

def setWebBrowser():
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
    return controller


def initMap(filename,lat,lng,zoom):
    """Initialize Google Map centred on Greenwich"""
    mymap = pygmaps.maps(lat,lng,zoom)
    mymap.draw(os.getcwd() + '/' + filename)
    return mymap

def updateMap(mymap,cnew,drawFlag,filename,cStr,controller):
    """Update the map with the geo-coordinates of the new Twitter user."""
    # print "in updateMap"
    mymap.addradpoint(cnew[0],cnew[1],60000,cStr)
    if(drawFlag):
        mymap.draw(os.getcwd() + '/' + filename)
        controller.open(os.getcwd() + '/' + filename)

def updateMapRT(mymap,cnew,cprev,drawFlag,filename,cStr,controller):
    """Update map with geo-coordinates of the new Twitter user"""
    # connection to follower
    mymap.addradpoint(cnew[0],cnew[1],60000,cStr)
    mymap.addpatharrows([cprev,cnew],cStr),
    if(drawFlag):
        mymap.draw(os.getcwd() + '/' + filename)
        controller.open(os.getcwd() + '/' + filename)

def saveMap(mymap,filename):
    """Save map to file"""
    # print "in saveMapRT"
    mymap.draw(os.getcwd() + '/' + filename)

def geocoder(location):
        """Geocode Twitter user using location attribute"""
        coordinates = ["-99999","-99999"]
        try:
            # geocode the user's location* attribute
            if(location):
                #print "location = %s" % location
                coordinates = Geocoder.geocode(location).coordinates
        except GeocoderError,e:
            print "geocode error: " + str(e)
            #print sys.exc_info()[0]
            pass
        except NameError,e:
            print "name error: " + str(e)
            #print sys.exc_info()[0]
            pass
        except Exception,e:
            print "other exception: " + str(e)
            #print sys.exc_info()[0]
            pass
        return coordinates

def mapNetwork(myMap,root,maxFriends,ofilehtml,controller):
    """Map the friends of a given root Twitter user."""

    flog = codecs.open("log_ex3.txt","a",encoding="utf-8")
    print "Start mapping network for %s..." % root["name"]

    twitHandle = root["name"]
    rootCoords = geocoder(root["location"])
    updateMap(mymap,map(float,rootCoords),1,ofilehtml,root["color"],controller)

    friendCount = 0

    for friend in tweepy.Cursor(api.friends,screen_name=twitHandle,retry_delay=15).items():

            print "Processing friend %s of twitHandle %s." % (friend.screen_name,twitHandle)
            if(float(friend.friends_count)/float(friend.followers_count) < 0.1 and friend.verified):
                description = friend.description
                description = re.sub("\s+"," ",description)
                friendCoords = geocoder(friend.location)
                friendRatio = float(friend.friends_count)/float(friend.followers_count)
                if(friendCoords[0] != "-99999"):
                    print ("EliteFriend|||%s|||%s|||%s|||%s|||%s\n"\
                                                        % (twitHandle,\
                                                        (friend.screen_name).encode('ascii','replace'),\
                                                        root["location"].encode('ascii','replace'),\
                                                        friend.location.encode('ascii','replace'),\
                                                        friendRatio))
                    flog.write("EliteFriend|||%s|||%s|||%s|||%s|||%s|||%s|||%s\n" \
                                                    % (twitHandle,\
                                                        friend.screen_name,["location"],\
                                                        friend.location,description,\
                                                        friend.friends_count,\
                                                        friend.followers_count\
                                                        ))
                    flog.write("Coordinates|||%s|||%s|||%s|||%s\n" % \
                            (rootCoords[0],rootCoords[1],friendCoords[0],friendCoords[1]))
                    if(friendCount % 2 == 0):
                            updateMapRT(mymap,map(float,friendCoords),\
                                        map(float,rootCoords),1,ofilehtml,\
                                        root["color"],controller)
                    else:
                            updateMapRT(mymap,map(float,friendCoords),\
                                    map(float,rootCoords),1,ofilehtml,\
                                    root["color"],controller)
                friendCount += 1

                if(friendCount >= maxFriends):
                    break

            # sleep for a bit so as not to exceed the Twitter rate limit
            time.sleep(3)

    #save the map before returning
    saveMap(mymap,ofilehtml)
    flog.close()

    return

if __name__=="__main__":

    # set output file name
    ofilehtml = "ex3_TwitterNetwork.html" 

    # get controller for displaying web browser
    controller = setWebBrowser()

    # instantiate OAuthHandler and initialize it with your credentials
    auth = tweepy.OAuthHandler(ckey,csecret)
    auth.set_access_token(atoken,asecret)
    api = tweepy.API(auth)

    twitRoots = [{"name":"BillGates","location":"Seattle","color":"#0000FF"},
            {"name":"NUSingapore","location":"Singapore","color":"#FFA500"},
            {"name":"Tim_Cook","location":"California","color":"#FF0000"},
            {"name":"KAUST_NEWS","location":"Saudi Arabia","color":"#7D26CD"}
                    ]

    # initialize Google Maps map
    mymap = initMap(ofilehtml,52.0,0.0,2.8)
    open("log3_txt","w").close()

    # extract a maximum of four elite+verified friends
    maxFriends = 4
    for root in twitRoots:
        mapNetwork(mymap,root,maxFriends,ofilehtml,controller)
