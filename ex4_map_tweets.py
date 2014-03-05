#coding: utf-8

# Copyright 2014, Radhika S. Saksena (radhika dot saksena at gmail dot com)
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

from tweepy import OAuthHandler
from tweepy import Stream
from TweetListener import TweetListener
from optparse import OptionParser

"""Print out JSON elements of tweets (created_at, text, screen_name, location)
    obtained from the Twitter stream and containing filter text. Map the
    tweets on Google Maps using the tweet coordinates or user location."""

# set values as per tokens in your Twitter developer account
ckey = " " #consumer key
csecret = " " #conumer scret
atoken = " " # access token
asecret = " " #access secret

if __name__=="__main__":

    usage = "usage: python ex4_map_tweets.py [options]"

    parser = OptionParser(usage=usage)
    parser.add_option("-b","--browser", action="store_true",
                        dest="useBrowser", default=0,
                            help="display webbrowser? 1 or 0")
    parser.add_option("-o","--output", action="store_true",
                        dest="ofile", default="ex4_map_tweets.html",
                            help="filename for HTML output")
    (options,args) = parser.parse_args()

    # instantiate OAuthHandler and initialize it with your credentials
    auth = OAuthHandler(ckey,csecret)
    auth.set_access_token(atoken,asecret)

    # set up multi-topic search terms to track and display properties
    track1=["obamacare"]
    track2=["ucrania"]
    track3=["tesla","spacex","elonmusk","elon musk","gigafactory","model s","tsla"\
                            "#tesla","#spacex","#elonmusk","#elon musk","#gigafactory","#model s","#tsla"]

    # assign different colors for the tweet marker of different topics
    colorDict = dict.fromkeys(track1,"#0000FF") #blue
    colorDict.update(dict.fromkeys(track2,"#FF0000")) #red
    colorDict.update(dict.fromkeys(track3,"#006400")) #dark green

    # instantiate an instance of the new TweetListener class
    twListener = TweetListener(options.useBrowser,options.ofile,colorDict)
    twStream = Stream(auth,twListener)

    # set terms to be filtered
    twStream.filter(track=track1 + track2 + track3)
