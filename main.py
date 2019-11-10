from bottle import route, run, template, static_file, get, post, delete, request
import json
import pymysql

# CONNECT TO THE DATABASE
connection = pymysql.connect(host='localhost',
                             user='',
                             password='',
                             db='store',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)


# CREATING A CATEGORY
@post("/category")
def create_category():
    new_category = request.POST.get("name")

    if new_category == " ":
        return json.dumps({"STATUS": "ERROR",
                           "MSG": "Bad Request",
                           "CAT_ID": None,
                           "CODE": 400})
    else:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT name FROM category"
                cursor.execute(sql)
                categories = cursor.fetchall()

                for category in categories:
                    if new_category == category[""]:
                        return json.dumps({"STATUS": "ERROR",
                                           "MSG": "Category Already Exists",
                                           "CAT_ID": None,
                                           "CODE": 200})

                sql = "INSERT INTO category VALUES(id, %s)"
                category_name = new_category
                cursor.execute(sql, category_name)
                id_new_category = cursor.lastrowid
                connection.commit()
                return json.dumps({"STATUS": "SUCCESS",
                                   "MSG": "Category Created Successfully",
                                   "CAT_ID": id_new_category,
                                   "CODE": 201})
        except:
            return json.dumps({"STATUS": "ERROR",
                               "MSG": "Internal error",
                               "CAT_ID": None,
                               "CODE": 500})


# DELETING A CATEGORY
@route("/category/<id>", method='DELETE')
def delete_category(id):
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM category WHERE id = {}".format(id)
            cursor.execute(sql)
            connection.commit()
            return json.dumps({"STATUS": "SUCCESS",
                               "MSG": "Category Deleted Succesfully",
                               "CODE": 201})
    except:
        return json.dumps({'STATUS': 'ERROR',
                           'MSG': "Internal error",
                           "CODE": 500})


# LIST CATEGORIES
@get("/categories")
def list_categories():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM category"
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({"STATUS": "SUCCESS",
                               "CATEGORIES": result,
                               "CODE": 200})
    except:
        return json.dumps({"STATUS": "ERROR",
                           "MSG": "Internal error",
                           "CODE": 500})


# ADD/EDIT A PRODUCT
@post("/product")
def add_product():

    id_category = request.POST.get('id')
    category = request.POST.get('category')
    title = request.POST.get('title')
    description = request.POST.get('desc')
    price = request.POST.get('price')
    favorite = request.POST.get('favorite')
    img_url = request.POST.get('img_url')

    if favorite == None:
        favorite_value = 0
    else:
        favorite_value = 1

    if id_category != "":
        try:
            with connection.cursor() as cursor:
                sql = ('UPDATE products SET category=%s, title=%s, description=%s, price=%s, favorite=%s, img_url=%s '
                       'WHERE id=%s')
                data = (category, str(title), str(description), price, favorite_value, str(img_url), id_category)
                cursor.execute(sql, data)
                connection.commit()
                return json.dumps({"STATUS": "SUCCESS",
                                   "MSG": "The Product Was Added/Updated Successfully",
                                   "CODE": 201})
        except:
            return json.dumps({"STATUS": "ERROR",
                               "MSG": "Internal Error",
                               "CODE": 500})
    else:
        try:
            with connection.cursor() as cursor:
                sql = 'INSERT INTO products VALUES(id, %s, %s, %s, %s, %s, %s)'
                data = (category, title, description, price, favorite_value, img_url)
                cursor.execute(sql, data)
                connection.commit()
        except:
            return json.dumps({"STATUS": "ERROR",
                               "MSG": "Missing Parameters",
                               "CODE": 400})


# GET A PRODUCT
@get("/product/<id>")
def load_products(id):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT category, description, price, title, favorite, img_url, id FROM products"
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({"STATUS": "SUCCESS",
                               "PRODUCTS": result,
                               "MSG": "Product Fetched Successfully",
                               "CODE": 200})
    except:
        return json.dumps({"STATUS": 'ERROR',
                           "MSG": "Internal error",
                           "CODE": 500})


# DELETE A PRODUCT
@route('/product/<id>', method='DELETE')
def delete_product(id):
    try:
        with connection.cursor() as cursor:
            sql = ('DELETE FROM products WHERE id = {}'.format(id))
            cursor.execute(sql)
            connection.commit()
            return json.dumps({"STATUS": "SUCCESS",
                               "MSG": "Product Deleted Successfully",
                               "CODE": 201})
    except:
        return json.dumps({"STATUS": 'ERROR',
                           "MSG": "Internal error",
                           "CODE": 500})


# LIST ALL PRODUCTS
@get("/products")
def load_products():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT category, description, price, title, favorite, img_url, id FROM products"
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({"STATUS": "SUCCESS",
                               "PRODUCTS": result})
    except:
        return json.dumps({"STATUS": "ERROR",
                           "MSG": "Internal error"})


# LIST PRODUCTS BY CATEGORY
@get('/category/<id>/products')
def list_products_cat(id):
    try:
        with connection.cursor() as cursor:
            sql = ('SELECT category, description, price, title, favorite, img_url, id FROM products '
                   'WHERE category = {} ORDER BY favorite DESC, creation_date ASC'.format(id))
            cursor.execute(sql)
            result = cursor.fetchall()
            return json.dumps({"STATUS": "SUCCESS",
                               "PRODUCTS": result})
    except:
        return json.dumps({"STATUS": "ERROR",
                           "MSG": "Internal error"})


# STATIC ROUTES
@get("/admin")
def admin_portal():
    return template("admin.html")


# @get("/")
# def index():
#     return template("index.html")


@get('/js/<filename:re:.*\.js>')
def javascripts(filename):
    return static_file(filename, root='js')


@get('/css/<filename:re:.*\.css>')
def stylesheets(filename):
    return static_file(filename, root='css')


@get('/images/<filename:re:.*\.(jpg|png|gif|ico)>')
def images(filename):
    return static_file(filename, root='images')


run(host='localhost', port=7000)
