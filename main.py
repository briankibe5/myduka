from datetime import datetime
import psycopg2
from flask import Flask, redirect, render_template, request, url_for, flash, session
import re
from datetime import timedelta


app = Flask(__name__)
app.secret_key = "briankibe"
app.permanent_session_lifetime = timedelta(minutes=5)

# Connect to an existing database
# conn = psycopg2.connect(user="sbppptuvedzdmz", password="4195135a2aa915cea64c84560ad518e8f0599765c4dbfc6811f804116d2d6971", host="ec2-54-228-32-29.eu-west-1.compute.amazonaws.com", port="5432", database="dfj3bpv8m5dmgl")

conn = psycopg2.connect(
    user="postgres",
    password="briankibe",
    host="localhost",
    port="5432",
    database="postgres",
)

# Open a cursor to perform database operations
cur = conn.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS products(id serial PRIMARY KEY, name VARCHAR ( 100 ) NOT NULL,buying_price NUMERIC(14, 2), selling_price NUMERIC(14, 2), stock_quantity INT DEFAULT 0);"
)
cur.execute(
    "create table IF NOT EXISTS  sales (id serial, pid int, quantity numeric(5,2), created_at timestamp, primary key(id),constraint myproduct foreign key(pid) references products(id) on update cascade on delete restrict);"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS  users (id serial PRIMARY KEY, username VARCHAR ( 50 ) NOT NULL, password VARCHAR ( 255 ) NOT NULL, email VARCHAR ( 50 ) NOT NULL );"
)
# insert query
# commit changes you make to the database
conn.commit()


# home route
@app.route("/")
def home():

    return render_template("index.html")


# home route
@app.route("/index")
def index():

    return render_template("index.html")


# login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "username" in request.form and "password" in request.form:
            username = request.form["username"]
            password = request.form["password"]

            username = username.lower()
            # Check if account exists using PSQL
            cur.execute(
                "SELECT * FROM users WHERE username = %s and password=%s",
                (username, password),
            )
            # cur.execute('SELECT * FROM users WHERE username = %s and password=%s', (username,password))
            # Fetch one record and return result
            account = cur.fetchone()

            if account:
                password_rs = account[2]
                # print(password_rs)
                # If account exists in users table in  database
                # if check_password_hash(password_rs, password):
                if password_rs == password:
                    # Create session data, we can access this data in other routes
                    session.permanent = True
                    session["loggedin"] = True
                    session["id"] = account[0]
                    session["username"] = account[1]

                    # The following flash message will be displayed on successful login
                    flash("Login successful")
                    # Redirect to home page
                    return redirect(url_for("home"))

                else:
                    # Account doesnt exist or username/password incorrect
                    return redirect(url_for("login"))
            else:
                flash("Login failed.Please create an Account ")
                return redirect(url_for("register"))

    return render_template("login.html")


# register
@app.route("/register", methods=["GET", "POST"])
def register():
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        password == password

        # Check if account exists using psql
        cur.execute(
            "SELECT * FROM users WHERE username = %s and password=%s",
            (username, password),
        )
        account = cur.fetchone()
        # print(account)

        # If account exists show error and validation checks
        if not username or not password or not email:
            flash("Please fill out the form!")
            return redirect(url_for("register"))
        elif account:
            flash("Username already exists!")
            return redirect(url_for("register"))

        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address!")
            return redirect(url_for("register"))

        elif not re.match(r"[A-Za-z0-9]+", username and password):
            flash("Username must contain only characters and numbers!")
            return redirect(url_for("register"))

        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            email = email.strip().lower()
            username = username.strip().lower()

            cur.execute(
                "INSERT INTO users(username,password,email) VALUES (%s,%s, %s)",
                (username, password, email),
            )
            conn.commit()

            session["email"] = email
            session["username"] = username

        flash("Account Created.Proceed to login")
        return redirect(url_for("login"))
    elif request.method == "POST":
        # Form is empty... (no POST data)
        flash("Please fill out the form!")
    return render_template("register.html")


# inventories route
@app.route("/inventories")
def inventories():

    if session:
        pass
    else:
        return redirect(url_for("login"))

    cur.execute("SELECT * FROM products ORDER BY id ASC;")
    records = cur.fetchall()

    return render_template("inventories.html", records=records)


# dashboard route
@app.route("/dashboard")
def dashboard():

    if session:
        pass

    else:

        return redirect(url_for("login"))

    # display every product vs sales
    # python query for BAR GRAPH
    cur.execute(
        "SELECT name,sum(selling_price*quantity) as total_sales FROM products INNER JOIN sales ON products.id = sales.pid GROUP BY name;"
    )
    items = cur.fetchall()
    labels = []
    data = []
    for i in items:
        labels.append(i[0])
        data.append(float(i[1]))

    # python query for LINE GRAPH
    cur.execute(
        "select to_char(sales.created_at,'YYYY-MM') sales,sum(sales.quantity*products.selling_price) as amount from products join sales on sales.pid=products.id group by sales;"
    )
    amount = cur.fetchall()
    labels_line = []
    data_line = []
    for i in amount:
        labels_line.append(i[0])
        data_line.append(float(i[1]))

    return render_template(
        "dashboard.html",
        labels=labels,
        data=data,
        labels_line=labels_line,
        data_line=data_line,
    )


# sales route
@app.route("/sales")
def sales():

    if session:

        pass
    else:
        return redirect(url_for("login"))

    cur.execute("SELECT* FROM sales ORDER BY id ASC;")
    records = cur.fetchall()
    # print(records)
    return render_template("sales.html", records=records)


# stock route
@app.route("/stock")
def stock():

    if session:

        pass
    else:
        return redirect(url_for("login"))

    return render_template("stock.html")


# add item route
@app.route("/add_product", methods=["POST"])
def add_product():
    productName = request.form["product_name"]
    bp = request.form["buying_price"]
    sp = request.form["selling_price"]
    quantity = request.form["quantity"]
    cur.execute(
        "INSERT INTO products (name, buying_price, selling_price, stock_quantity) VALUES (%s,%s, %s, %s)",
        (productName, bp, sp, quantity),
    )
    conn.commit()
    flash("Item added")
    return redirect(url_for("inventories"))


# add sale route
@app.route("/add_sale", methods=["POST"])
def add_sales():
    pid = request.form["product_sale_name"]
    # print(product_name)
    quantity = request.form["sale_quantity"]
    # print(quantity)
    created_at = datetime.now()
    cur.execute(
        "INSERT INTO sales (pid, quantity, created_at ) VALUES (%s,%s,%s)",
        (pid, quantity, created_at),
    )
    conn.commit()
    return redirect(url_for("sales"))


# edit product route
@app.route("/edit_product", methods=["POST", "GET"])
def edit_product():

    if request.method == "POST":
        id = request.form["edit_product_id"]
        name = request.form["edit_product_name"]
        bp = request.form["edit_product_bp"]
        sp = request.form["edit_product_sp"]
        quantity = request.form["edit_product_quantity"]

        cur.execute(
            "UPDATE products SET name = %s, buying_price = %s, selling_price = %s, stock_quantity = %s WHERE id=%s",
            (
                name,
                bp,
                sp,
                quantity,
                id,
            ),
        )
        conn.commit()

        flash("Product Updated")
        return redirect(url_for("inventories"))
    else:
        return render_template("inventories")


# delete product route
@app.route("/delete_product", methods=["POST", "GET"])
def delete_product():

    id = request.form["delete_product_id"]
    print(id)
    # delete sales with pid 1
    cur.execute("DELETE FROM sales WHERE pid = %s", (id,))

    cur.execute("DELETE FROM products WHERE id = %s", (id,))

    conn.commit()
    flash("Product deleted")
    return redirect(url_for("inventories"))


@app.route("/logout")
def logout():
    # Remove session data, this will log the user out
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    # Redirect to login page
    return redirect(url_for("login"))


# reset password
@app.route("/reset_password", methods=["POST", "GET"])
def reset_password():

    if request.method == "POST":

        username = request.form["reset_password_username"]
        password = request.form["reset_password_pwd"]
        email = request.form["reset_password_email"]

        username = username.strip().lower()
        email = email.strip().lower()

        # Check if account exists using psql
        cur.execute(
            "SELECT * FROM users WHERE username = %s and email = %s",
            (
                username,
                email,
            ),
        )
        user = cur.fetchone()
        # print(user)
        if user:
            # print('x')

            cur.execute(
                "UPDATE users SET username = %s, password = %s, email= %s  WHERE username=%s ",
                (
                    username,
                    password,
                    email,
                    username,
                ),
            )

            conn.commit()

            flash("Password Updated")
            return redirect(url_for("login"))

        else:
            flash("Incorrect email/username.")
            return redirect(url_for("login"))

    else:
        # print("y")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run()
