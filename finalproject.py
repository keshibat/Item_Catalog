from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, ClothingItem, User
from flask import session as login_session
import random, string

#New Import for this step
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Clothing Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for ex in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:# Upgrade the authorization code into a credentials object
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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = credentials.id_token['sub']


    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']


    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

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


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None



# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
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
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response




# JSON APIs to view Restaurant Information
@app.route('/catalog/<int:catalog_id>/clothing/JSON')
def catalogClothingJSON(catalog_id):
    catalog = session.query(Catalog).filter_by(id = catalog_id).one()
    items = session.query(ClothingItem).filter_by(catalog_id = catalog_id).all()
    return jsonify(CatalogItems=[i.serialize for i in items])

@app.route('/catalog/<int:catalog_id>/clothing/<int:clothing_id>/JSON')
def clothingItemJSON(catalog_id, clothing_id):
    clothingItem = session.query(ClothingItem).filter_by(id=clothing_id).one()
    return jsonify(clothingItem=ClothingItem.serialize)

@app.route('/catalog/JSON')
def catalogJSON():
    catalog = session.query(Catalog).all()
    return jsonify(catalog=[r.serialize for r in catalog])


# Show all catalogs
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    catalog = session.query(Catalog).all()
    if 'username' not in login_session:
        return render_template('publicCatalog.html', catalog = catalog)
    else:
        return render_template('catalog.html', catalog = catalog)



# Create a new catalog
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if request.method == 'POST':
        newCatalog = Catalog(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCatalog)
        flash('New Catalog %s Successfully Created' % newCatalog.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCatalog.html')

#Edit a catalog
@app.route('/catalog/<int:catalog_id>/edit/', methods=['GET', 'POST'])
def editCatalog(catalog_id):
    editedCatalog = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedCatalog.name = request.form['name']
            flash('Catalog Successfully Edited %s' % editedCatalog.name)
            return redirect(url_for('showCatalog'))
    else:
        return render_template('editCatalog.html', catalog=editedCatalog)


# Delete a catalog
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        session.delete(catalogToDelete)
        flash('%s Successfully Deleted' % catalogToDelete.name)
        session.commit()
        return redirect(url_for('showCatalog', catalog_id=catalog_id))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete)


#Show a clothing item

@app.route('/catalog/<int:catalog_id>/')
@app.route('/catalog/<int:catalog_id>/clothing/')
def showClothing(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(ClothingItem).filter_by(catalog_id=catalog.id)
    creator = getUserInfo(catalog.user_id)
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicclothing.html', catalog=catalog, items=items, creator=creator)
    else:
        return render_template('clothing.html', catalog=catalog, items=items, creator=creator)


def showFavApps(appmaker_id):
    appmaker = session.query(AppMaker).filter_by(id=appmaker_id).one()
    items = session.query(FavApps).filter_by(
        appmaker_id=appmaker_id).all()
    print "appmaker.user_id %s" % appmaker.user_id
    creator = getUserInfo(appmaker.user_id)
    items = session.query(FavApps).filter_by(appmaker_id=appmaker_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicfavapps.html', items=items, appmaker=appmaker, creator=creator)
    else:
        return render_template('favapps.html', items=items, appmaker=appmaker, creator=creator)

    #return "This page will show all my FavApps."
    #return render_template('favapps.html', items=items, appmaker=appmaker)

# Create route for newClothingItem function here

@app.route('/catalog/<int:catalog_id>/clothing/new/', methods=['GET', 'POST'])
def newClothingItem(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        newItem = ClothingItem(name=request.form['name'], catalog_id=catalog_id, user_id=catalog.user_id)
        session.add(newItem)
        session.commit()
        flash("new Clothing %s Item Successfully Created" % (newItem.name))
        return redirect(url_for('showCatalog', catalog_id=catalog_id))
    else:
        return render_template('newclothingitem.html', catalog_id=catalog_id)

# Task 2: Create route for editClothingItem function here

@app.route('/catalog/<int:catalog_id>/clothing/<int:clothing_id>/edit/', methods=['GET', 'POST'])
def editClothingItem(catalog_id, clothing_id):
    editedItem = session.query(ClothingItem).filter_by(id=clothing_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("Clothing Item has been edited")
        return redirect(url_for('showClothing', catalog_id=catalog_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'editclothingitem.html', catalog_id=catalog_id, clothing_id=clothing_id, item=editedItem)

# Task 3: Create a route for deleteClothingItem function here

@app.route('/catalog/<int:catalog_id>/clothing/<int:clothing_id>/delete/', methods=['GET', 'POST'])
def deleteClothingItem(catalog_id, clothing_id):
    itemToDelete = session.query(ClothingItem).filter_by(id=clothing_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Catalog Item has been deleted")
        return redirect(url_for('showClothing', catalog_id=catalog_id))
    else:
        return render_template('deleteclothingitem.html', item=itemToDelete)




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)