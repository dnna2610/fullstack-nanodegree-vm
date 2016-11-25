from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Catalog, Base, Item
 
engine = create_engine('postgresql://catalog:udacity@localhost/catalog')
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

items  = [
    Item(name = "Snowboard", description = "Best for any terrain and conditions with snow.", catalog = catalogs[8]),
    Item(name = "Soccer Ball", description = "Round and hard, comes with many different styles. The best ball there is.", catalog = catalogs[0]),
    Item(name = "Basketball", description = "Red, hard and with stripes. This poor ball gets pounded and dunked millions of times per day across the world.", catalog = catalogs[1]),
    Item(name = "Baseball bat", description = "Essential for any baseball players and any self-respecting thugs.", catalog = catalogs[2]),
    Item(name = "Frisbee", description = "Look likes a disc, flies like an ufo.", catalog = catalogs[3]),
    Item(name = "Rock climbing shoe", description = "Just like any shoes, this item comes in pair and in different styles. But unlike any other shoes, this item needs to have more friction, so dont try to slide with these.", catalog = catalogs[4]),
    Item(name = "Foosball Table", description = "Essential item at any college dorm for bored or drunk college students pass their precious time.", catalog = catalogs[5]),
    Item(name = "Skateboard", description = "Well, it's basically a board that is a little curvy attached to a few wheels. This item has been known to be used to increase swag but sometimes fail miserably.'", catalog = catalogs[6]),
    Item(name = "Puck", description = "Black and hard, easy to slide.", catalog = catalogs[7])
]

for item in items:
    session.add(item)
    session.commit()

print "Added catalog items."