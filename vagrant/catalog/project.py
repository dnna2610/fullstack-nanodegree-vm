from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from database_setup import Base, Catalog, Item

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads( open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Udacity Item Catalog"

#Connect to Database and create database session
engine = create_engine('postgresql://catalog:udacity@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# JSON APIs
# Get all catalogs
@app.route('/api/allcatalogs')
def allcatJSON():
    catalogs = session.query(Catalog).all()
    return jsonify(catalogs = [c.serialize for c in catalogs])

# Get all items of one catalog with id
@app.route('/api/catalog/<int:catalog_id>')
def allitemJSON(catalog_id):
    catalog = session.query(Catalog).filter_by(id = catalog_id).one()
    items = session.query(Item).filter_by(catalog_id = catalog_id).all()
    return jsonify(Items = [i.serialize for i in items])

# Get info of one item with id
@app.route('/api/item/<int:item_id>')
def itemJSON(item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    return jsonify(Items = item.serialize)

# Home page, shows all catalogs.
@app.route('/')
@app.route('/catalogs/')
def showCatalog():
    catalogs = session.query(Catalog).order_by(Catalog.name).all()
    latest_items = session.query(Item).options(joinedload(Item.catalog)).order_by(Item.created_date.desc()).all()
    return render_template("catalogs.html", catalogs = catalogs, latest_items = latest_items)

# Show all items of a category
@app.route('/catalog/<catalog_name>')
def showItems(catalog_name):
    catalogs = session.query(Catalog).order_by(Catalog.name)
    catalog = session.query(Catalog).filter_by(name = catalog_name).one()
    items = session.query(Item).filter_by(catalog = catalog).all()
    return render_template("category.html", items = items, catalogs = catalogs, catalog = catalog)

# Show item 
@app.route('/catalog/<catalog_name>/<item_name>')
def showItem(catalog_name, item_name):
    catalog = session.query(Catalog).filter_by(name = catalog_name).one()
    item = session.query(Item).options(joinedload(Item.catalog)).filter_by(catalog_id = catalog.id).filter_by(name = item_name).one()
    return render_template("item.html", item = item)

# Edit item
@app.route('/catalog/edit/<catalog_name>/<item_name>', methods=['GET', 'POST'])
def editItem(catalog_name, item_name):
    if request.method == "POST":
        catalog = session.query(Catalog).filter_by(name = catalog_name).one()
        item = session.query(Item).options(joinedload(Item.catalog)).filter_by(catalog_id = catalog.id).filter_by(name = item_name).one()
        item.name = request.form['name']
        item.description = request.form['description']
        item.catalog_id = request.form['catalog_id']
        session.commit()
        return redirect(url_for("showCatalog"))
    else:
        catalogs = session.query(Catalog).order_by(Catalog.name)
        catalog = session.query(Catalog).filter_by(name = catalog_name).one()
        item = session.query(Item).options(joinedload(Item.catalog)).filter_by(catalog_id = catalog.id).filter_by(name = item_name).one()
        return render_template("edit.html", item = item, catalogs = catalogs)

# Delete item
@app.route('/catalog/delete/<catalog_name>/<item_name>', methods=['GET', 'POST'])
def deleteItem(catalog_name, item_name):
    if request.method == "POST":
        catalog = session.query(Catalog).filter_by(name = catalog_name).one()
        item = session.query(Item).options(joinedload(Item.catalog)).filter_by(catalog_id = catalog.id).filter_by(name = item_name).one()
        session.delete(item)
        session.commit()
        return redirect(url_for("showCatalog"))
    else:
        catalog = session.query(Catalog).filter_by(name = catalog_name).one()
        item = session.query(Item).options(joinedload(Item.catalog)).filter_by(catalog_id = catalog.id).filter_by(name = item_name).one()
        return render_template("delete.html", item = item)

# Add new item
@app.route('/item/new', methods=['GET', 'POST'])
def newItem():
    if request.method == "POST":
        newItem = Item(name = request.form['name'], description = request.form['description'], catalog_id = request.form['catalog_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for("showCatalog"))
    else:
        catalogs = session.query(Catalog).order_by(Catalog.name)
        return render_template("newitem.html", catalogs = catalogs)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)