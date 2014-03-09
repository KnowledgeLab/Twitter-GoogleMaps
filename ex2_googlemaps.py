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
from dateutil import parser
from pygeocoder import Geocoder
from pygeolib import GeocoderError
import pygmaps
import pandas as pd
import csv
import webbrowser
from optparse import OptionParser

"""Read in the store_openings.csv file:
    http://www.econ.umn.edu/~holmes/data/WalMart/store_openings.csv
    This contains opening dates of Wal-Mart stores and supercenters
    from 1962-2006. Geocode the Wal-Mart stores and plot on Google Maps."""

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
    """Initialize Google Map centred on given
    lat,lng and with a zoom factor given by zoom."""
    mymap = pygmaps.maps(lat,lng,zoom)
    mymap.draw(os.getcwd() + '/' + filename)
    return mymap

def updateMap(mymap,cnew,drawFlag,filename,cStr,controller):
    """Update the map with the geo-coordinates of the new location."""
    mymap.addradpoint(cnew[0],cnew[1],20000,cStr)
    if(drawFlag):
        mymap.draw(os.getcwd() + '/' + filename)
        controller.open(os.getcwd() + '/' + filename)

def geocoder(location):
    """Geocode the given location. Returns -99999 if Google
        Maps exception is encountered."""
    coordinates = ["-99999","-99999"]
    try:
        # geocode the user's location* attribute
        if(location):
            coordinates = Geocoder.geocode(location)[0].coordinates
    except GeocoderError,e:
        print "geocode error: " + str(e)
        pass
    except NameError,e:
        print "name error: " + str(e)
        pass
    except Exception,e:
        print "other exception: " + str(e)
        pass
    return coordinates

def geocodeStoreData(ifile):
    """ Iterate over input data, geocode and
    store data frame augmented with lat/lon values"""
    #iDF = pd.read_csv("store_openings.csv")
    iDF = pd.read_csv(ifile)
    iDF["lat"] = -99999
    iDF["lng"] = -99999
    for item,row in iDF.iterrows():
        addr = " ".join([row["STREETADDR"],row["STRCITY"],row["STRSTATE"],\
                                                        str(int(row["ZIPCODE"]))])
        # geocode address
        print "Geocoding address: " + addr
        coords = geocoder(addr)
        iDF.loc[item,"lat"] = coords[0]
        iDF.loc[item,"lng"] = coords[1]
        # inject time delay between API requests
        # to avoid exceeding rate limit.
        time.sleep(2)
    # write data frame augmented with lat,lng
    iDF.to_csv(ofile,sep=",",index=False,quoting=csv.QUOTE_MINIMAL)

if __name__=="__main__":

    usage = "usage: python ex2_googlemaps.py"

    ifile = "store_openings.csv"
    ofile = "geocoded_store_openings.csv"
    ohtml = "ex2_googlemaps.html"
    cDict = {'Supercenter':'FF0000','Wal-Mart':'0000FF'}
    mymap = initMap(ohtml,40.0,-100.0,4.5)
    controller = setWebBrowser()

    # uncomment if the store_openings.csv needs to be geocoded
    #geocodeStoreData(ifile)

    # plot geocoded data about Target/Walmart store openings on Google Maps
    df = pd.read_csv(ofile)
    df['OPENDATE'] = df['OPENDATE'].apply(pd.to_datetime)
    df = df.sort(['OPENDATE'])
    for index,row in df.iterrows():
        print row["OPENDATE"].strftime('%m/%d/%Y')
        # set cadence of the map updates
        if index < 100:
            interval = 20
            time.sleep(0.1)
        elif index < 500:
            interval = 100
        elif index < 1000:
            interval = 150
        else:
            interval = 200
        # update Google Maps map
        if(index % interval == 0):
            updateMap(mymap,[row["lat"],row["lng"]],1,ohtml,cDict[row["type_store"]],controller)
            time.sleep(0.1)
        else:
            updateMap(mymap,[row["lat"],row["lng"]],0,ohtml,cDict[row["type_store"]],controller)
        time.sleep(0.015)
