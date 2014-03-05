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
import TweetMapper as mapper

class TweetListener(StreamListener):
    """Extend tweepy's StreamListener class and re-define the on_data() method"""

    def __init__(self,useBrowser,filename,colorDict):
        StreamListener.__init__(self)
        self.useBrowser = useBrowser
        self.ofile = filename
        (self.twMap,self.controller) = mapper.initMap(self.ofile,self.useBrowser)
        self.allCoordinates = []
        self.flog = codecs.open("log.txt",mode="w",encoding="utf-8")
        self.gcCount = 0
        self.tweetCount = 0
        self.colorDict = colorDict

    def on_data(self,data):
        """Called when raw data is received from the Stream."""
        try:
            if "limit" in data:
                print "Limit"
                self.flog.write("Limit\n")
                time.sleep(300)
                return True
            else:
                self.tweetCount += 1
                jsonStr = json.loads(data)
                createdAt = jsonStr["created_at"] if jsonStr["created_at"] else "None"
                tweetText = jsonStr["text"] if jsonStr["text"] else "None"
                screenName = jsonStr["user"]["screen_name"] if jsonStr["user"]["screen_name"] else "None"
                location = jsonStr["user"]["location"] if jsonStr["user"]["location"] else "None"
                print("Tweet: %s|||%s|||%s|||%s\n" % (createdAt,tweetText,screenName,location))
                # geocode the Tweet for mapping
                coordinates = mapper.geocodeTweet(jsonStr,self.gcCount,self.flog)
                self.flog.write("Tweet: createdAt=%s|||" \
                                          "tweetText=%s|||" \
                                          "screenName=%s|||" \
                                          "location=%s|||" \
                                          "lat=%s|||" \
                                          "long=%s\n" % \
                                         (createdAt, \
                                         tweetText, \
                                         screenName,location, \
                                         coordinates[0],coordinates[1]))
                # if coordinates are valid then map the tweet
                if(coordinates[0] != "-99999"):
                    self.gcCount += 1
                    self.allCoordinates.append(map(float,coordinates))
                    tweetColor = self.setTweetColor(jsonStr)
                    if(len(self.allCoordinates)%3 == 0):
                        mapper.updateMap(self.twMap,self.ofile,\
                                            self.allCoordinates[-1],0,tweetColor)
                        # refresh browser if flag set
                        if(self.useBrowser):
                            self.controller.open(os.getcwd() + "/" + self.ofile)
                    else:
                        # update map with tweet coordinates
                        mapper.updateMap(self.twMap,self.ofile,\
                                            self.allCoordinates[-1],1,tweetColor)
                self.flog.write("gcCount = %d tweetCount = %d successRate = %f\n" \
                                % (self.gcCount,self.tweetCount,\
                                    (float(self.gcCount)/self.tweetCount)))
                time.sleep(2)
                return True
        except KeyboardInterrupt, e:
            self.flog.close()
        except SystemExit, e:
            self.flog.close()
        except Exception, e:
            self.flog.write("Exception encountered: %s." % e)
            time.sleep(5)

    def setTweetColor(self,jsonStr):
        for key in self.colorDict.keys():
            if(re.search(key,jsonStr["text"],re.IGNORECASE)):
                    return self.colorDict[key]
        # if we reach this point then color the tweet loc black
        return "#000000"
