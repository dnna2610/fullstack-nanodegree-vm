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
engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE = state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return redirect(url_for("showCatalog"))
    else:
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

def getAuthStatus():
    if "username" not in login_session:
        return False
    return True

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
    logged_in = getAuthStatus()
    catalogs = session.query(Catalog).order_by(Catalog.name).all()
    latest_items = session.query(Item).options(joinedload(Item.catalog)).order_by(Item.created_date.desc()).all()
    return render_template("catalogs.html", catalogs = catalogs, latest_items = latest_items, logged_in = logged_in)

# Show all items of a category
@app.route('/catalog/<catalog_name>')
def showItems(catalog_name):
    logged_in = getAuthStatus()
    catalogs = session.query(Catalog).order_by(Catalog.name)
    catalog = session.query(Catalog).filter_by(name = catalog_name).one()
    items = session.query(Item).filter_by(catalog = catalog).all()
    return render_template("category.html", items = items, catalogs = catalogs, catalog = catalog, logged_in = logged_in)

# Show item 
@app.route('/catalog/<catalog_name>/<item_name>')
def showItem(catalog_name, item_name):
    logged_in = getAuthStatus()
    catalog = session.query(Catalog).filter_by(name = catalog_name).one()
    item = session.query(Item).options(joinedload(Item.catalog)).filter_by(catalog_id = catalog.id).filter_by(name = item_name).one()
    return render_template("item.html", item = item, logged_in = logged_in)

# Edit item
@app.route('/catalog/edit/<catalog_name>/<item_name>', methods=['GET', 'POST'])
def editItem(catalog_name, item_name):
    logged_in = getAuthStatus()
    if not logged_in:
        return redirect(url_for("showCatalog"))
    elif request.method == "POST":
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
    logged_in = getAuthStatus()
    if not logged_in:
        return redirect(url_for("showCatalog"))
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
    logged_in = getAuthStatus()
    if not logged_in:
        return redirect(url_for("showCatalog"))
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