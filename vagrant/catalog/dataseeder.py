from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Catalog, Base, Item
 
engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

catalogs = [
    Catalog(name = "Soccer"),
    Catalog(name = "Basketball"),
    Catalog(name = "Baseball"),
    Catalog(name = "Frisbee"),
    Catalog(name = "Rock Climbing"),
    Catalog(name = "Foosball"),
    Catalog(name = "Skating"),
    Catalog(name = "Hockey"),
    Catalog(name = "Snowboarding")
]

for cat in catalogs:
    session.add(cat)
    session.commit()

item  = Item(name = "Snowboard", description = "Best for any terrain and conditions with snow.", catalog = catalogs[8])
session.add(item)
session.commit()

print "Added catalog items."