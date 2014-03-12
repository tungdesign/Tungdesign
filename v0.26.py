# coding=utf-8
import os
from flask import Flask, request, session, g, redirect, url_for, \
    render_template, flash, send_from_directory
from werkzeug.utils import secure_filename

import db


app = Flask(__name__)

app.config.update(dict(
    DATABASE='flaskr.db',
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'C:\Users\Patrik\PycharmProjects\V0.26\static\uploads'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    For a given file, return whether it's an allowed type or not.

    :param filename: Name of the file to be checked.
    :return: :rtype: Returns the allowed extension added to the filename, after check.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    The app route for the uploaded file.

    :param filename: Name of the uploaded file.
    :return: :rtype: Returns the uploaded folder and filename.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/')
def index():
    """
    The app route for the rendered index page, when you go to the websites start page.

    :return: :rtype: Returns the rendered template for the index.html and allproducts.
    """
    allproducts = db.get_all_products()
    return render_template("index.html", data=allproducts)


@app.route('/products')
def product():
    """
    The app route for the rendered product page, showing the products in the database.

    :return: :rtype: Returns the rendered template for the products.html and related products.
    """
    allproducts = db.get_all_products()
    return render_template("products.html", data=allproducts)

@app.route('/products/<name>')
def specproduct(name):
    """
    Calls for a function that sorts out the product with the name you searched
    for as well as render a product page for that product.

    :param name: Name of the product wanted.
    :return: :rtype: Returns the rendered template for productdetail.html, related products, name and comments.
    """
    product= db.get_specific_product("product_name",name)
    product_id = db.get_product_id(name)
    comments = db.get_messages(product_id)
    return render_template("productdetail.html",data=product,name=name,comments=comments)

@app.route('/category/<name>')
def speccategory(name):
    """
    Allows the webpage to pick out all products of a specific category and then render a page with all products
    of that category
    :param name: The name of the parameter in the specified category
    :return: :rtype: Returns the rendered html-template, for category with the return values of product and name
    """
    product= db.get_specific_product("category",name)
    return render_template("category.html",data=product,name=name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    The app route for the register page, allowing users to register to the database.

    :return: :rtype: Returns the redirect for the homepage if the user is succesfully registered
    else renders the register home page if the user fails to login properly.
    """
    error = None
    if request.method == 'POST':
        if request.form['username'] == "":
            error = 'Must input username'
        elif request.form['password'] == "":
            error = 'Must input password'
        elif request.form['firstname'] == "":
            error = 'Must input firstname'
        elif request.form['lastname'] == "":
            error = 'Must input lastname'
        else:
            username=request.form['username']
            password=request.form['password']
            firstname=request.form['firstname']
            lastname=request.form['lastname']
            db.register_user(username,password,firstname,lastname)
            session['logged_in'] = True
            flash('You were registered')
            return redirect(url_for('index'))
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Function that controls the login of users of the website.
    It takes in the parameters of username and password  from the website login form.
    If succesful, it redirects you to the logged in view.

    :return: :rtype: Returns the redirect to the homepage, if you're logged in
    else it renders the login.html and sends an error message.
    """
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.check_password(username,password) == False:
            error = 'Invalid password or username'
            flash('Invalid password or username')
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/add_product')
def add_product():
    """
    The app route for the add product site.

    :return: :rtype: Returns the rendered add product site.
    """
    return render_template("add_product.html")

@app.route('/about_us')
def about():
    """
    The app route for the about page.

    :return: :rtype: Returns the rendered about page.
    """
    return render_template("about.html")

@app.route('/contact')
def contact():
    """
    The app route for the contact page.

    :return: :rtype: Returns the rendered contact page.
    """
    return render_template("contact.html")

@app.route('/show')
def show():
    """
    The app route for the contact messages page, allowing you to show messages in the database,
    stored from the contact page.

    :return: :rtype: Returns the rendered show.html and the data that is to be shown.
    """
    all = db.get_messages(1)
    return render_template("show.html", data=all)


#Visar samtliga produkter tillagda i databasen men på en helt odesignad sida , bara här för att testa olika funktioner.
#Sidan är ej tillgänglig från frontend och skall tas bort senare
@app.route('/show_products')
def show_products():
    allproducts = db.get_all_products()
    return render_template("show_products.html", data=allproducts)

# Allows you to log out when youve been log in and redirects you to the startpage after doing so
@app.route('/logout')
def logout():
    """
    The app route for the logout page, that allows you to logout by pressing the list item in the navbar.

    :return: :rtype: Redirects you to the home page.
    """
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

#Plockar in namn, meddelande och email från contact html sidan och sänder dem vidare till sidan för att spara medelandet
# anropar även en funktion som lägger till informationen i våran databas
@app.route("/save_message", methods=['POST', 'GET'])
def save():
    """
    The app route for the save message page, adding information to the database inputted
    by the user, on the contact page.

    :return: :rtype: Returns a message and an url to get back to the contact page.
    """
    name = request.form['name']
    message = request.form['message']
    email = request.form['email']
    db.add_new_message(name, message, email)
    return "Thank you""<a href='" + url_for("contact") + "'>Back to form</a>"

@app.route("/save_product", methods=['POST', 'GET'])
def saveproduct():
    """
    The app route for the save product page, adding information to the database inputted
    by the user, on the add product page.

    :return: :rtype: Returns a message and an url to get back to the add product page.
    """
    Product_ID = request.form['product_id']
    Product_Name = request.form['product_name']
    Price = request.form['price']
    Max_Size = request.form['max_size']
    Min_Size = request.form['min_size']
    Brand = request.form['brand']
    Category = request.form['category']
    Info = request.form['info']
    Classification = request.form['classification']
    Pic_URL = request.files['pic_url']
    # # Check if the file is one of the allowed types/extensions
    if Pic_URL and allowed_file(Pic_URL.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(Pic_URL.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        Pic_URL.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    db.add_new_product(Product_ID, Product_Name, Price, Max_Size, Min_Size, Brand, Category, Info, Classification, filename)
    return "Thank you <a href='" + url_for("add_product") + "'>Back to form</a>"

# Implementera inte igen föränn vi skrivit in databasen som den är nu i db.py
#@app.route("/init_db")
#def setup_db():
    #Warning this method will remove all data from the database
#    db.setup()
 #   return "Database created"

#Flask function that runs after each request used to close the database
@app.teardown_appcontext
def close_db(error):
    """
    Closes the database again at the end of the request.

    :param error: Parameter representing an error in the close down.
    """
    print ("Closing db")
    if hasattr(g, 'sqlite_db'):
        print "found it"
        g.sqlite_db.close()


if __name__ == '__main__':
    app.debug = True
    app.run()
