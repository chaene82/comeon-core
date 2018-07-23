#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 16:19:16 2017

@author: chrhae
"""

import pandas as pd
from pinnacle.apiclient import APIClient
import collections
import os



#log = startBetLogging("pinnacle Wrapper")

pin_user = slack_key = os.environ['comeon_pin_username']
pin_passwd = slack_key = os.environ['comeon_pin_passwd']



## Class for as Wrapper


class pinnacle:
    
    sports_id = 33
    api = ''
    odds = None
    
    def __init__(self):
        self.api = APIClient(pin_user, pin_passwd)
                  
    
    def checkBalance(self) :
        """
        CCheck the balance on pinnacle
        
        Args:
            
        Returns:
            total_balance : total balance (including placed open bets)
            availiable : availiable balance for betting
            blocked : placed balance
        """ 
        account = self.api.account.get_account()
        availiable = account['availableBalance']
        blocked = account['outstandingTransactions']
        
        return availiable + blocked, availiable, blocked


    def getEvents(self) :
        """
        Get all open events on pinnacle
        
        Args:
            
        Returns:
            json : the list of the events
        """        
        result = pd.DataFrame()
        
        events =  self.api.market_data.get_fixtures(self.sports_id)
        for league in events['league'] :
            league_id = league['id']
            for event in league['events'] :
                if not "Set" in (event['home']) or not "Set" in (event['away']) : 
                    #log.info("pinnacle_event_id " + str(event['id']))
                    bookie_event_id = event['id']
                    
                    StartDate        = removeTime(event['starts'])
                    StartDateTime    = event['starts']
                    home_player_name = ((event['home']))
                    away_player_name = ((event['away']))
                    live             = (event['liveStatus'])
                    pinnacle_league_id= league_id
    
                    
                    dict = collections.OrderedDict({'bookie_event_id': bookie_event_id, 'StartDate' : StartDate, 'StartDateTime' : StartDateTime,
                                                    'home_player_name' : home_player_name, 'away_player_name': away_player_name, 
                                                    'live' : live, 'pinnacle_league_id' : pinnacle_league_id})
                    
                    result = result.append(pd.DataFrame([dict]))
                
        return result
    
    
   