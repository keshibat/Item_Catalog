from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, ClothingItem

app = Flask(__name__)

engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog/<int:catalog_id>/')
def catalogMenu(catalog_id):
    catalog = session.query(Catalog).filter_by(id=catalog_id).one()
    items = session.query(ClothingItem).filter_by(catalog_id=catalog.id)
    return render_template('clothing.html', catalog=catalog, items=items)

# Task 1: Create route for newMenuItem function here


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

# Task 2: Create route for editMenuItem function here


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

# Task 3: Create a route for deleteMenuItem function here


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
