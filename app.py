import sqlite3
from flask import Flask, render_template, request, redirect

global db
global sql
db = sqlite3.connect('base.db', check_same_thread=False)
sql = db.cursor()

sql.execute("""CREATE TABLE IF NOT EXISTS users (
            login TEXT,
            pass TEXT,
            deliver INT,
            orderid BIGINT,
            status INT
)""")

db.commit()

sql.execute("""CREATE TABLE IF NOT EXISTS orders (
            id BIGINT,
            what TEXT,
            towhere TEXT,
            fromwhere TEXT,
            price TEXT,
            status INT
)""")

db.commit()

global mesmas
mesmas = {
    "0": "не визначене",
    "1": "замовлене",
    "2": "прийняте",
    "3": "виконане",
}

app = Flask(__name__)


class USER:
    user_active = 0


@app.route('/login', methods=["GET", "POST"])
def login():

    message = ''
    if request.method == "GET":
        for i in sql.execute(f"SELECT * FROM users"):
            print(i)
        return render_template("login.html", message=message)

    if request.method == "POST":
        sql.execute(f"SELECT * FROM users WHERE login='{request.form['login']}'")
        if sql.fetchone() is not None:
            sql.execute(f"SELECT * FROM users WHERE login='{request.form['login']}'")
            data = sql.fetchone()
            if data[1] == request.form['password']:
                if data[2] == 0:
                    USER.user_active = request.form['login']
                    return redirect('/personal_office')
                elif data[2] == 1:
                    USER.user_active = request.form['login']
                    return redirect('/deliver')
                else:
                    return render_template("login.html")
            else:
                message = 'Невірний пароль!'
        else:
            message = "Немає користувача з таким ім'ям!"
        return render_template("login.html", message=message)


@app.route('/reg', methods=["GET", "POST"])
def reg():
    message = ''
    if request.method == 'GET':
        return render_template('reg.html', message=message)

    if request.method == 'POST':
        for i in sql.execute(f"SELECT * FROM users"):
            print(i)
        username = request.form['email_e']
        password = request.form['password']

        if len(username) >= 4 and len(password) >= 8:
            sql.execute(f"SELECT * FROM users WHERE login='{request.form['email_e']}'")
            if sql.fetchone() is None:
                isdeliver = request.form['categories']
                sql.execute(f"INSERT INTO users VALUES ('{request.form['email_e']}','{request.form['password']}','{isdeliver}', '0', '0')")
                db.commit()
                return redirect('/login')
            else:
                message = "Користувач з таким іменем вже зареєстрований!"
        else:
            if len(username) < 4 and len(password) < 8:
                message = "Пароль та логін введені не правильно!"
            elif len(password) < 8:
                message = "Довжина пароля повинна бути мінімум 8 символів!"
            elif len(username) < 4:
                message = "Довжина логіна повинна бути мінімум 4 символи!"

    return render_template('reg.html', message=message)


@app.route('/seller', methods=["GET", "POST"])
def seller():

    if request.method == "GET":
        if USER.user_active != 0:
            sql.execute(f"SELECT status FROM users WHERE login='{USER.user_active}'")
            if sql.fetchone()[0] == 1:
                message = ['text', 1]
                return render_template("seller.html", message=message)
        return render_template("seller.html", message='')

    if request.method == "POST" and USER.user_active is not None:
        for i in sql.execute(f"SELECT * FROM orders"):
            print(i)
        sql.execute(f"SELECT status FROM users WHERE login='{USER.user_active}'")

        message = [mesmas[f'{sql.fetchone()[0]}']]

        sql.execute(f"SELECT status FROM users WHERE login='{USER.user_active}'")
        sql.execute(f"SELECT status FROM users WHERE login='{USER.user_active}'")
        if sql.fetchone()[0] == 0:
            sql.execute(f"SELECT MAX(id) FROM orders")
            if sql.fetchone()[0] is not None:
                sql.execute(f"SELECT MAX(id) FROM orders")
                tmpid = sql.fetchone()[0]+1
            else:
                tmpid = 0
            sql.execute(f"INSERT INTO orders VALUES ('{tmpid}','{request.form['what']}','{request.form['towhere']}','{request.form['fromwhere']}','{request.form['price']}',1)")
            db.commit()
            sql.execute(f"UPDATE users SET status=1, orderid={tmpid} WHERE login='{USER.user_active}'")
            db.commit()
            sql.execute(f"SELECT status FROM users WHERE login='{USER.user_active}'")
            message.append(sql.fetchone()[0])
            return render_template("seller.html", message=message)
        else:
            return render_template("seller.html", message=message)
    else:
        return render_template("seller.html", message=mesmas['0'])


@app.route('/deliver', methods=["GET", "POST"])
def deliver():
    button = ""
    corid = None
    sql.execute(f"SELECT * FROM orders WHERE status=1")
    orders = sql.fetchall()
    if request.args.get('login') is not None:
        if request.args.get('id') is not None:
            corid = request.args.get('id')
            sql.execute(f"SELECT status FROM users WHERE login='{USER.user_active}'")#DEL
            print(request.args.get('login'))#DEL
            print(request.args.get('login'), sql.fetchone()[0])#DEL
            sql.execute(f"SELECT status FROM users WHERE login='{USER.user_active}'")
            if sql.fetchone()[0] == 0:
                sql.execute(f"UPDATE users SET status=2, orderid={request.args.get('id')} WHERE login='{USER.user_active}'")
                db.commit()
                sql.execute(f"UPDATE orders SET status=2 WHERE id={request.args.get('id')}")
                db.commit()
                button = request.args.get('id')
        if request.args.get('butid') is not None:
            corid = request.args.get('butid')
            sql.execute(f"UPDATE users SET status=0, orderid=0 WHERE login='{USER.user_active}'")
            db.commit()
            sql.execute(f"UPDATE orders SET status=3 WHERE id={request.args.get('butid')}")
            db.commit()
            button = ""
    return render_template("deliver.html", orders=orders, button=button, ordreid=corid, login=request.args.get('login'))


@app.route('/personal_office', methods=["GET", "POST"])
def personal_office():
    msg = ''
    if request.method == "GET":
        if not USER.user_active == 0:
            sql.execute(f"SELECT * FROM users WHERE login='{USER.user_active}'")
            msg = sql.fetchone()
            msgs = [msg]
            order_id = msg[-2]
            order_status = msg[-1]

            if not order_status == 0:
                sql.execute(f"SELECT * FROM orders WHERE id='{order_id}'")
                order_msg = sql.fetchone()
                mess = [msg, order_msg]
                return render_template("personal_office.html", message=mess)
            else:
                return render_template("personal_office.html", message=msgs)
        else:
            return render_template("personal_office.html", message=msg)

    if request.method == "POST":
        if not USER.user_active == 0:
            USER.user_active = 0
            return redirect('/login')
        return render_template('personal_office.html', message='')


@app.route('/about_us', methods=["GET", "POST"])
def about_us():
    return render_template("about_us.html")


@app.route('/')
def index():
    return redirect(f"/login")


if __name__ == "__main__":
    app.run()
