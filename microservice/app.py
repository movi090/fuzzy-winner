import sqlite3
from flask import Flask, request, render_template
from werkzeug.local import Local
from pyzbar.pyzbar import decode
from PIL import Image


app = Flask(__name__)
local = Local()

conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()

create_table_query = '''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        description TEXT
    )
'''
cursor.execute(create_table_query)
conn.commit()
conn.close()

def get_db():
    if not hasattr(local, 'connection'):
        local.connection = sqlite3.connect('mydatabase.db')
    return local.connection

@app.route('/')
def home():
    title = "Главная страница"
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    file = request.files['image']
    image = Image.open(file)
    barcodes = decode(image)
    if barcodes:
        barcode_data = barcodes[0].data.decode("utf-8")
        return barcode_data
    else:
        return 'Штрих-код не найден'

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.form
    name = data['name']
    price = data['price']
    description = data['description']

    conn = get_db()
    cursor = conn.cursor()

    insert_query = "INSERT INTO products (name, price, description) VALUES (?, ?, ?)"
    cursor.execute(insert_query, (name, price, description))
    conn.commit()

    return 'Product added successfully'

@app.route('/products')
def view_products():
    conn = get_db()
    cursor = conn.cursor()
    select_query = "SELECT * FROM products"
    cursor.execute(select_query)
    products = cursor.fetchall()

    return render_template('products.html', products=products)

if __name__ == '__main__':
    app.run()