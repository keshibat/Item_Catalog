from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, ClothingItem

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



# Show all catalogs
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    catalog = session.query(Catalog).all()
    return render_template('catalog.html', catalog=catalog)



# Create a new catalog
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalog():
    if request.method == 'POST':
        newCatalog = Catalog(name=request.form['name'])
        session.add(newCatalog)
        flash('New Catalog %s Successfully Created' % newCatalog.name)
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
            return redirect(url_for('showCatalogs'))
    else:
        return render_template('editCatalog.html', restaurant=editedCatalog)


# Delete a catalog
@app.route('/catalog/<int:catalog_id>/delete/', methods=['GET', 'POST'])
def deleteCatalog(catalog_id):
    catalogToDelete = session.query(
        Catalog).filter_by(id=catalog_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        flash('%s Successfully Deleted' % catalogToDelete.name)
        session.commit()
        return redirect(url_for('showCatalogs', catalog_id=catalog_id))
    else:
        return render_template('deleteCatalog.html', catalog=catalogToDelete)



@app.route('/')
@app.route('/catalog/<int:catalog_id>/')
def catalogMenu(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(ClothingItem).filter_by(catalog_id=catalog.id)
    return render_template('clothing.html', catalog=catalog, items=items)

# Task 1: Create route for newClothingItem function here


@app.route('/catalog/<int:catalog_id>/new/', methods=['GET', 'POST'])
def newClothingItem(catalog_id):
    if request.method == 'POST':
        newItem = CatalogItem(
            name=request.form['name'], catalog_id=catalog_id)
        session.add(newItem)
        session.commit()
        flash("new clothing item created!")
        return redirect(url_for('catalogClothing', catalog_id=catalog_id))
    else:
        return render_template('newclothingitem.html', catalog_id=catalog_id)

# Task 2: Create route for editClothingItem function here


@app.route('/catalog/<int:catalog_id>/<int:clothing_id>/edit/', methods=['GET', 'POST'])
def editClothingItem(catalog_id, clothing_id):
    editedItem = session.query(ClothingItem).filter_by(id=clothing_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("Clothing Item has been edited")
        return redirect(url_for('catalogClothing', catalog_id=catalog_id))
    else:
        # USE THE RENDER_TEMPLATE FUNCTION BELOW TO SEE THE VARIABLES YOU
        # SHOULD USE IN YOUR EDITMENUITEM TEMPLATE
        return render_template(
            'editclothingitem.html', catalog_id=catalog_id, clothing_id=clothing_id, item=editedItem)

# Task 3: Create a route for deleteClothingItem function here


@app.route('/catalog/<int:catalog_id>/<int:clothing_id>/delete/', methods=['GET', 'POST'])
def deleteClothingItem(catalog_id, clothing_id):
    itemToDelete = session.query(ClothingItem).filter_by(id=clothing_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Catalog Item has been deleted")
        return redirect(url_for('catalogClothing', catalog_id=catlog_id))
    else:
        return render_template('deleteconfirmation.html', item=itemToDelete)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
