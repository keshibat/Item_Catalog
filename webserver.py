from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from Lesson 1
from database_setup import Base, Catalog, ClothingItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///catalogitem.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            # Objective 3 Step 2 - Create /catalog/new page
            if self.path.endswith("/catalog/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New ClothingItem</h1>"
                output += "<form method = 'POST' enctype='multipart/form-data' action = '/catalog/new'>"
                output += "<input name = 'newCatalogName' type = 'text' placeholder = 'New Catalog Name' > "
                output += "<input type='submit' value='Create'>"
                output += "</form></body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/edit"):
                catalogIDPath = self.path.split("/")[2]
                myCatalogQuery = session.query(Catalog).filter_by(
                    id=catalogIDPath).one()
                if myCatalogQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += myCatalogQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' action = '/catalog/%s/edit' >" % catalogIDPath
                    output += "<input name = 'newCatalogName' type='text' placeholder = '%s' >" % myCatalogQuery.name
                    output += "<input type = 'submit' value = 'Rename'>"
                    output += "</form>"
                    output += "</body></html>"

                    self.wfile.write(output)
            if self.path.endswith("/delete"):
                catalogIDPath = self.path.split("/")[2]

                myCatalogQuery = session.query(Catalog).filter_by(
                    id=catalogIDPath).one()
                if myCatalogQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure you want to delete %s?" % myCatalogQuery.name
                    output += "<form method='POST' enctype = 'multipart/form-data' action = '/catalog/%s/delete'>" % catalogIDPath
                    output += "<input type = 'submit' value = 'Delete'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)

            if self.path.endswith("/catalog"):
                catalogs = session.query(Catalog).all()
                output = ""
                # Objective 3 Step 1 - Create a Link to create a new clothing item
                output += "<a href = '/catalog/new' > Make a New Catalog Here </a></br></br>"

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output += "<html><body>"
                for catalog in catalogs:
                    output += catalog.name
                    output += "</br>"
                    # Objective 2 -- Add Edit and Delete Links
                    # Objective 4 -- Replace Edit href

                    output += "<a href ='/catalog/%s/edit' >Edit </a> " % catalog.id
                    output += "</br>"
                    # Objective 5 -- Replace Delete href
                    output += "<a href ='/catalog/%s/delete'> Delete </a>" % catalog.id
                    output += "</br></br></br>"

                output += "</body></html>"
                self.wfile.write(output)
                return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
    # Objective 3 Step 3- Make POST method
    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                catalogIDPath = self.path.split("/")[2]
                myCatalogQuery = session.query(Catalog).filter_by(
                    id=catalogIDPath).one()
                if myCatalogQuery:
                    session.delete(myCatalogQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/catalog')
                    self.end_headers()


            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newCatalogName')
                    catalogIDPath = self.path.split("/")[2]

                    myCatalogQuery = session.query(Catalog).filter_by(
                        id=catalogIDPath).one()
                    if myCatalogQuery != []:
                        myCatalogQuery.name = messagecontent[0]
                        session.add(myCatalogQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/catalog')
                        self.end_headers()

            if self.path.endswith("/catalog/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newCatalogName')

                    # Create new Catalog Object
                    newCatalog = Catalog(name=messagecontent[0])
                    session.add(newCatalog)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/catalog')
                    self.end_headers()

        except:
            pass


def main():
    try:
        server = HTTPServer(('', 8080), webServerHandler)
        print 'Web server running...open localhost:8080/catalog in your browser'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()


if __name__ == '__main__':
    main()
