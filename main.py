from datetime import datetime
from flask import Flask, redirect, render_template , request, url_for
import psycopg2
app = Flask(__name__)

#Connect to an existing database
conn = psycopg2.connect(user="postgres", password="briankibe", host="localhost", port="5432", database="postgres")
#Open a cursor to perform database operations
cur = conn.cursor()


# home route
@app.route('/index')
def index():

   return render_template('index.html')


# inventories route
@app.route('/inventories')
def inventories():
   cur.execute("SELECT * FROM products;")
   records = cur.fetchall()
   print(records)
   return render_template('inventories.html'  , records = records)

# sales route
@app.route('/sales')
def sales():
   cur.execute("SELECT* FROM sales ORDER BY id ASC;")
   records = cur.fetchall()
   print(records)
   return render_template('sales.html'  , records = records)

# dashboard route
@app.route('/dashboard')
def dashboard():
   # display every product vs sales
   # fetch the data using psycopg2 cur
   # python query for BAR GRAPH
   cur.execute("SELECT name,sum(selling_price*quantity) as total_sales FROM products INNER JOIN sales ON products.id = sales.pid GROUP BY name;")
   items = cur.fetchall()
   labels=[]
   data=[]
   for i in items:
      labels.append(i[0])
      data.append(float(i[1]))


   # python query for LINE GRAPH
   cur.execute("select to_char(sales.created_at,'YYYY-MM') sales,sum(sales.quantity*products.selling_price) as amount from products join sales on sales.pid=products.id group by sales;")
   amount = cur.fetchall()
   labels_line=[]
   data_line=[]
   for i in amount:
      labels_line.append(i[0])
      data_line.append(float(i[1]))



   return render_template('dashboard.html',labels=labels,data = data, labels_line=labels_line, data_line=data_line)


# add item route
@app.route('/add_product' ,methods = ['POST'])
def add_product():
   productName=request.form["product_name"]
   bp = request.form['buying_price']
   sp = request.form['selling_price']
   quantity=request.form['quantity']
   cur.execute("INSERT INTO products (name, buying_price, selling_price, stock_quantity) VALUES (%s,%s, %s, %s)",(productName,bp,sp,quantity))
   conn.commit()
   return redirect(url_for("inventories"))

# add sale route
@app.route('/add_sale' ,methods = ['POST'])
def add_sales():
   pid=request.form["product_sale_name"]
   # print(product_name)
   quantity=request.form['sale_quantity']
   # print(quantity)
   created_at = datetime.now()
   cur.execute("INSERT INTO sales (pid, quantity, created_at ) VALUES (%s,%s,%s)",(pid,quantity, created_at ))
   conn.commit()
   return redirect(url_for("sales"))

#a new route for viewing sales per product
@app.route('/sales/<int:pid>')
def view_sales(pid):
     # query the sales for that product_id
		cur.execute("SELECT * FROM sales WHERE pid= %s;" ,[pid])
		rows = cur.fetchall()
		return render_template("sales.html", rows = rows) 


app.run()
