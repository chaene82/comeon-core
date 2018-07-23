# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import MetaData



Base = declarative_base(metadata=MetaData(schema='core'))  
class Events(Base):  
    __tablename__ = 'events'
    event_id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    event_name = Column(Text)
    event_begin = Column(DateTime)
    te_datetime = Column(JSON)
    head_to_head = Column(JSON)
    matchtype = Column(Text)
    player1_id =  Column(Integer)
    player2_id =  Column(Integer)
    player1 = Column(JSON)
    player2 = Column(JSON)
    result = Column(JSON)
    round = Column(Text)
    status = Column(Text)
    surface = Column(Text)
    te_odds = Column(JSON)
    te_id = Column(Integer)
    tour = Column(Text)
    tournament = Column(Text)
    pin_id = Column(Integer)
    mb_id = Column(Integer)
    bb_id = Column(Integer)
    


    
class Players(Base):  
    __tablename__ = 'players'
    player_id = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
    player_name = Column(Text)
    te_player_link = Column(Text)
    pin_player_name = Column(Text)
    mb_player_name = Column(Text)
    bd_player_name = Column(Text)
    bf_player_name = Column(Text)
    bb_player_name = Column(Text)
