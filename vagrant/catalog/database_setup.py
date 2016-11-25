import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class Catalog(Base):
    __tablename__ = 'catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    hased_password = Column(String(250), nullable=False)
    email = Column(String(250), nullable=True)
    picture = Column(String(250), nullable=True)

class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    catalog_id = Column(Integer,ForeignKey('catalog.id'))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    catalog = relationship(Catalog)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'       : self.name,
           'description': self.description,
           'id'         : self.id,
           'created'    : self.created_date
       }

engine = create_engine('postgresql://catalog:udacity@localhost/catalog')
Base.metadata.create_all(engine)