# Item Catalog Project

###Project Overview

This is RESTful web application about clothing item catalog using Flask which accesss a SQL database.  To create authentication system, this project has OAuth2 with Google API.

This is a part of <a href="https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004"> Udacity Full Stack Web Developer Nanodegree</a>.



### How to run?

#### PreRequisites:

Vagrant

Virtual Box

Python 2.7.11

flask


clone this repo: `https://github.com/keshibat/Item_Catalog`

create virtual environment: `vagrant up`&`vagrant ssh`

move vagrant directory: `cd /vagrant`

run finalproject.py: `python finalproject.py`

Go to http://localhost:5000/ in your browser: `http://localhost:5000/`


### JSON Endpoints
The following are open to the public:

Catalog JSON: `/catalog/JSON` - Displays the whole catalog.

Catalog clothing JSON: `/catalog/<int:catalog_id>/clothing/JSON` - Displays clothing items for a specific catalog

Clothing Item JSON: `/catalog/<int:catalog_id>/clothing/<int:clothing_id>/JSON`- Displays a specific catalog item.