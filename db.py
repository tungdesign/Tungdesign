__author__ = 'TungDesign'
# coding=utf-8

from sqlite3 import dbapi2 as sqlite3
from flask import g

def connect_db():
    """
    Connects to the specific database.

    :return: :rtype: Returns the connection value of the database.
    """
    print "Connectar db"
    try:
        rv = sqlite3.connect("message.sqlite3")
        print "Creating db"
        rv.row_factory = sqlite3.Row
        return rv
    except sqlite3.Error as e:
        print "An error occurred:", e.args[0]

def get_db():
    """
    Opens a new database connection, if there is none yet for the
    current application context.

    :return: :rtype: Returns the value of the connection.
    """
    if not hasattr(g, 'sqlite_db'):
        print "Creating new connection"
        g.sqlite_db = connect_db()
    return g.sqlite_db

#Not complete!!!
def setup():
    """
    Creates our database with
    Skapar vår databas med för nuvarande två tables en för meddelanden samt en för produkter, ska byggas ut med
    ytterligare tables för användare och ordrar

    """
    db = get_db()
    db.execute("drop table if exists messages")
    db.execute("drop table if exists product")
    db.execute("create table messages(id integer primary key, name text, message text, email text)")
    db.execute("create table product(product_id integer primary key ,product_name text,price integer ,max_size integer,min_size integer,brand text ,category text,info text,pic_url text, classification integer)")
    db.commit()

def register_user(username,password,firstname,lastname):
    """
    Creates a new user by taking information the person have filled in at the frontend and putting it in a database.

    :param username: The specified input of the user for their username.
    :param password: The specified input of the user for their password.
    :param firstname: The specified input of the user for their firstname.
    :param lastname: The specified input of the user for their lastname.
    """
    db = get_db()
    db.execute('insert into user (username, password, firstname, surname) values (?, ?, ?,?)', (username,password,firstname,lastname))
    db.commit()

#NOT WORKING FIX
def get_product_id(name):
    c = get_db()
    cursor = c.cursor()
    cursor.execute('SELECT Product_ID from product where Product_Name = ?', [name])
    result = cursor.fetchone()
    product_id = str(result[0])
    return product_id

def check_password(username,password):
    """
    Verifies the input of username and password against the database.

    :param username: The username that has been given by the user.
    :param password: The password that has been given by the user.
    :return: :rtype: Returns true if the username and password matches, else it returns false.
    """
    c = get_db()
    cursor = c.cursor()
    cursor.execute('SELECT Password from user where Username = ?', [username])
    result = cursor.fetchone()
    if result == None:
        return False
    else:
        c.commit()
        if str(result[0]) == password:
            return True
        else:
            return False

def add_new_message(name, message, email):
    """
    Allows the user to write messages that gets put into the database

    :param name: Name of the user.
    :param message: Input of message by the user.
    :param email: Email given by the user.
    """
    c = get_db()
    c.execute("insert into messages(name,message,email) values(?,?,?)",(name,message,email))
    c.commit()

def add_new_product (product_id, product_name, price, max_size, min_size, brand, category, info, pic_url, classification):
    """
    Allows a user to add new products to the database

    :param product_id: The product id of the new product, input by the user.
    :param product_name: The product name of the new product, input by the user.
    :param price: The product price of the new product, input by the user.
    :param max_size: The product maximum size of the new product, input by the user.
    :param min_size: The product minimum size of the new product, input by the user.
    :param brand: The product brand of the new product, input by the user.
    :param category: The product category of the new product, input by the user.
    :param info: The product information of the new product, input by the user.
    :param pic_url: The link to the picture of the new product, input by the user.
    :param classification: The product classification of the new product, input by the user.
    """
    c = get_db()
    c.execute("insert into Product(product_id, product_name, price, max_size, min_size, brand, category, info, pic_url, classification) values(?,?,?,?,?,?,?,?,?,?)",[product_id, product_name,price,max_size,min_size,brand,category,info,pic_url,classification])
    c.commit()

def get_messages(type):
    """
    Returns all the messages in the database, specified by the type input.

    :param type: Represents the wanted category of messages.
    :return: :rtype: Returns the messages found in the database.
    """
    c = get_db()
    result = c.execute('SELECT * from messages where Category = ?', [type])
    c.commit()
    return result.fetchall()

def get_all_products():
    """
    Picks out all the products in the database and returns them.

    :return: :rtype: Returns the products selected from the database, represented in result.
    """
    c = get_db()
    result = c.execute("select * from Product")
    c.commit()
    return result.fetchall()

def set_admin(name):
    """
    Allows a Admin to change a normal members Authority to a Admin level.

    :param name: The name of the user to be promoted.
    """
    c = get_db()
    s=" insert 2 into Authority in user where Username='"+name+"'"
    c.execute(s)
    c.commit()

def get_specific_product(type,id):
    """
    Allows the website to pick out a specific product based on a search of an attribute and search word.

    :param type: The type of the wanted product, input by user.
    :param id: The id of the wanted product, input by user.
    :return: :rtype: Returns the products that meets the search criterias.
    """
    c = get_db()
    s="select * from product where "+type+"='"+id+"'"
    result = c.execute(s)
    c.commit()
    return result.fetchall()

if __name__ == '__main__':
    p = connect_db()
    print p