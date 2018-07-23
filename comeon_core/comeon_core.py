"""Main module."""


from sqlalchemy import create_engine, MetaData
from tennisexplorer import get_te_match_json, get_te_matchlist_all
from sqlalchemy.orm import sessionmaker
import difflib
import pandas as pd
import os

from .Pinnacle import pinnacle

import datetime

from .tables import Players, Events
 
import socket
print (socket.gethostbyname(socket.gethostname()))


#from .tennis_config import *

db_host = os.environ['comeon_db_host']
db_name = os.environ['comeon_db_name']
db_user = os.environ['comeon_db_user']
db_passwd = os.environ['comeon_db_passwd']
db_port = os.environ['comeon_db_port']




def connect(db=db_name, user=db_user, password=db_passwd, host=db_host, port=db_port):
    """
    Returns a connection and a metadata object from the postgres DB
    
    Args:
        db (str): Name of the database to connect.   
        user (str): Name of the database user to connect.    
        password (str): the password for the user to connect.    
        host (str): Name or IP address of the node to connect.    
        port (int): Number of the db port.
        
    Returns:
        con: A database connection
        mate: a database meta object
        
    """
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = create_engine(url , client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = MetaData()
    meta.reflect(con)

    return con


def init_db (engine) :
    try :
        Players.__table__.drop(engine)
    except :
        print("table do not exists")
    Players.__table__.create(engine)
    
    try :
        Events.__table__.drop(engine)
    except :
        print("table do not exists")
    Events.__table__.create(engine)


def add_player(te_player_name, te_player_link, session) :
    """
    Add a new player to the database based on tennis explorer data
    
    Args:
        te_player_name (str): Name of the player
        te_player_link (str): Tennis Explorer Link of the player   
        session             : db session
        
    Returns:
        id: player id on the data base

    """
    
    print("add new player", te_player_name)
    
    u = Players(  
            player_name=te_player_name,
            te_player_link=te_player_link)
    session.add(u)  
    session.commit() 
    
    return u.player_id



def get_te_player_id(te_player_name, te_player_link, session) :
    """
    get the player id based on the name, if not exist, create one
    
    Args:
        te_player_name (str): Name of the player
        te_player_link (str): Tennis Explorer Link of the player   
        session             : db session
        
    Returns:
        id: player id on the data base

    """    
    u = session.query(Players).filter_by(player_name=te_player_name).one_or_none()
    if u == None:
        id = add_player(te_player_name, te_player_link, session)
    else :
        id = u.player_id
    
    return id


def get_pin_player_id(pin_player_name, session) :
    """
    get the player id based on the name from pinnacle
    
    Args:
        pin_player_name (str): Name of the player
        session             : db session
        
    Returns:
        id: player id on the data base

    """    

    # get player id with pin_player_id
    u = session.query(Players).filter_by(pin_player_name=pin_player_name).one_or_none()
    if u == None :
        if '/' in pin_player_name :
            print('double player team, skip for the moment')
            return 0
        rev_pin_player_name_list = pin_player_name.split(' ')[::-1]
        rev_pin_player_name = ' '.join(rev_pin_player_name_list)
        u = session.query(Players).filter_by(player_name=rev_pin_player_name).one_or_none()
        if u != None :
            session.query(Players).filter_by(player_id=u.player_id).update({
                    'pin_player_name' : pin_player_name})
            session.commit() 
            id = u.player_id
        else :
            player_list = [r.player_name for r in session.query(Players.player_name).distinct()]
            match_player = difflib.get_close_matches(rev_pin_player_name, player_list, n=1, cutoff=0.7)
            if len(match_player) > 0 :
                match_player = match_player[0]                           
                session.query(Players).filter_by(player_name=match_player).update({
                        'pin_player_name' : pin_player_name})
                session.commit() 
                u = session.query(Players).filter_by(pin_player_name=pin_player_name).one_or_none()
                if u != None :
                    id = u.player_id
                else :
                    print("pinnacle player" , pin_player_name, 'not found')
                    id = 0
            else :
                print("pinnacle player" , pin_player_name, 'not found')
                id = 0
    else : 
        id = u.player_id
    
    return id


def add_event(te_event, session) :
    """
    add an event based on tennis explorer data
    
    Args:
        te_event (dict): event object
        session             : db session
        
    Returns:
        id: event id

    """       
    te_begin = te_event['datetime']['startdatetime']
    te_event['datetime'].pop('startdatetime', None)
    te_event['datetime'].pop('date', None)
    
    ## Check if result is existing
    if 'result' in te_event:
        te_result =  te_event['result']
    else:
        te_result = None
        
    ## Check if head-to-head is existing
    if 'head-to-head' in te_event:
        head_to_head =  te_event['head-to-head']
    else:
        head_to_head = None        
    
    # first get player id's
    
    player1_id = get_te_player_id(te_event['player1']['name'], te_event['player1']['te_link'], session)
    player2_id = get_te_player_id(te_event['player2']['name'], te_event['player2']['te_link'], session) 
    
    u = Events(
            event_name = te_event['event_name'],
            event_begin = te_begin,
            te_datetime = te_event['datetime'],
            head_to_head = head_to_head,
            matchtype = te_event['matchtype'],
            player1_id =  player1_id,
            player2_id =  player2_id,
            player1 = te_event['player1'],
            player2 = te_event['player2'],
            result = te_result,
            round = te_event['round'],
            status = te_event['status'],
            surface = te_event['surface'],
            te_odds = te_event['te_odds'],
            te_id = te_event['tennisexplorer_id'],
            tour = te_event['tour'],
            tournament =te_event['tournament'])
    session.add(u)  
    session.commit() 
    
    
    return u.event_id


def update_te_event(te_event, session) :
    """
    add an event based on tennis explorer data
    
    Args:
        te_event (dict): event object
        session             : db session
        

    """       
    te_begin = te_event['datetime']['startdatetime']
    te_event['datetime'].pop('startdatetime', None)
    te_event['datetime'].pop('date', None)
    
    if 'result' in te_event:
        te_result =  te_event['result']
    else:
        te_result = None


    
    # first get player id's
       
    session.query(Events).filter_by(te_id=te_event['tennisexplorer_id']).update({
            'event_begin' : te_begin,
            'te_datetime' : te_event['datetime'],
            'result' : te_result,
            'status' : 'complete',
            'te_odds' : te_event['te_odds']})
    session.commit() 
    
    
def update_pin_event(pin_event_id, player1_id, player2_id, session) :
    """
    add an event based on tennis explorer data
    
    Args:
        pin_event_id (id): event id
        player1_id (id)  : id of the home player
        player2_id (id)  : id of the away player
        session             : db session
        
    Returns:
        id: event id
    """       
    
    u = session.query(Events).filter_by(pin_id=pin_event_id).one_or_none()
        
    
    u = session.query(Events).filter_by(player1_id=player1_id, player2_id=player2_id,).one_or_none()
    if u == None :
        u = session.query(Events).filter_by(player1_id=player2_id, player2_id=player1_id,).one_or_none()
    if u != None :
        session.query(Events).filter_by(event_id=u.event_id).update({
            'pin_id' : pin_event_id})
        session.commit()       
        print('event updated')
        id = u.event_id
    else :
        print('event not found')
        id = 0
    return id


def check_pin_event_exists(pin_event_id,session) :
    """
    checking if the event exists
    
    Args:
        pin_event_id (int)   : event id
        session             : db session

    Returns:
        TRUE: event has changed 
        FALSE: event hsn't changed

    """       
    u = session.query(Events).filter_by(pin_id=pin_event_id).one_or_none()
    if u == None :
        return False


    return True
    
def check_event_changed(te_event_id, status, year, month, day, time, session) :
    """
    checking if the event has changed since the last run
    
    Args:
        te_event_id (int)   : event object
        status (str)        : status of the event
        date (str)          : startdate of the event
        time (str)          : startime of the event
        session             : db session

    Returns:
        TRUE: event has changed 
        FALSE: event hsn't changed

    """       
    result = session.query(Events).filter_by(te_id=te_event_id, status=status).one_or_none()
    if result == None :
        return True
    if result.te_datetime['start_time'] != time or \
       result.event_begin.year !=  year or \
       result.event_begin.month !=  month or \
       result.event_begin.day !=  day:
        return False

    return True


def check_event_exists(te_event_id, session) :
    """
    checking if the event has changed since the last run
    
    Args:
        te_event_id (int)   : event object
        status (str)        : status of the event
        date (str)          : startdate of the event
        time (str)          : startime of the event
        session             : db session

    Returns:
        TRUE: event has changed 
        FALSE: event hsn't changed

    """       
    result = session.query(Events).filter_by(te_id=te_event_id).one_or_none()
    if result == None :
        return False

    return True


def update_te(today, match_type, session) :
    """
    Updates te events from a date
    
    Args:
        today (date)   : today function
        
    """
    
    # get active events
    events_df = get_te_matchlist_all(year = str(today.year),\
                                     month = str(today.month),\
                                     day = str(today.day),\
                                     match_type=match_type)
    
    for index, row in events_df.iterrows():
        te_id = int(row.match_link.split('=')[1])
        if check_event_exists(te_id, session) :
            if check_event_changed(te_id, row.status, row.date.split('-')[0], row.date.split('-')[1], row.date.split('-')[2], row.time, session) :
                try:
                    event = get_te_match_json(row.match_link)
                except:
                    print("error getting event details, skip")
                    return
                print("updated tennis explorer event", te_id, event['event_name'])
                update_te_event(event, session)
                
       
        else :
            try:
                event = get_te_match_json(row.match_link)
            except:
                print("error getting event details, skip")     
                return 
            print("add new tennis explorer event", te_id, event['event_name'])
            add_event(event, session)


def updated_pin(session) :
    """
    get events from Pinnacle
    
    Args:
        session   : database session
    """   
    today = datetime.date.today()

    api_pinnacle = pinnacle()
    
    pin_events = api_pinnacle.getEvents()
    
    pin_events['start_date'] = pd.to_datetime(pin_events['StartDate'], format='%Y-%m-%d')
    pin_events_planned = pin_events[pin_events['start_date'] >= today ]
    pin_events_upcoming = pin_events_planned[pin_events_planned['live'] == 0 ]
    
    for index, row in pin_events_upcoming.iterrows():
        if not check_pin_event_exists(row.bookie_event_id, session) :
            
            home_player_id = get_pin_player_id(row.home_player_name, session)
            away_player_id = get_pin_player_id(row.away_player_name, session)
            
            if home_player_id * away_player_id == 0 :
                print("Players not found, skip event", row.bookie_event_id)
            else :
                print("event found")
                update_pin_event(row.bookie_event_id, home_player_id, away_player_id, session)
            
        else:
            print ('event exists, do nothing')
    #for index, row in pin_events.iterrows():
        
    


def update() :
    """ 
    do a full upated    
    """
    SessionFactory = sessionmaker(engine)      
    session = SessionFactory()  
    
    today = datetime.datetime.today()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    date_list = [today, tomorrow]
    matchtype_list = ['wta-single', 'atp-single']
    for date in date_list:
        for matchtype in matchtype_list:
            update_te(date, matchtype, session)
    
    updated_pin(session)



db = connect()
engine = db.connect()  



#init_db(engine)



## TEST

#update()

#
#

#
#Base = declarative_base(metadata=MetaData(schema='public'))  
#class Events(Base):  
#    __tablename__ = 'events'
#    event_id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
#    event_name = Column(Text)
#    player1 = Column(JSON)
#    player2 = Column(JSON)
#    
#SessionFactory = sessionmaker(engine)      
#
#
#session = SessionFactory()  
#u = Events(  
#    #event_id=6,
#    event_name=events['event_name'],
#    player2={'name' : 'test2'})
#session.add(u)  
#session.commit()  
#
#
#uu = session.query(Events).first()
#
#uu = session.query(Events).filter(
#    Events.player1[
#        ("name")
#    ].cast(Text) == 'test'
#).one()