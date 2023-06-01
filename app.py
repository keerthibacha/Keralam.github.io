from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import re
import os
import requests
import json
import ibm_boto3              #pip install ibm-cos-sdk in terminal
from ibm_botocore.client import Config, ClientError
import datetime



app = Flask(__name__)
  
app.secret_key = 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=syj61291;PWD=XSW7tQ3SZASMgkNM",'','')


print("Connected")


# Constants for IBM COS values
COS_ENDPOINT = "https://s3.jp-tok.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "uNit-Hjo_8BNssKFZMxY8_gEtLY6Btf2VMotfCXQFzAj"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/98db753e3fa94bb7b8ff210866e85a90:ed1b977b-3036-464b-82f8-aee4c7d6e316::"
# Create resource
cos = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

# @app.route('/')
@app.route('/', methods=["POST", "GET"])
def login():
    msg = ''
    if request.method == 'POST':
        USERNAME = request.form["username"]
        PASSWORD = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE USERNAME=? AND PASSWORD=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account['ROLL']== 1:
            session['Loggedin'] = True
            session['USERNAME'] = account['USERNAME']
            session['USERID'] = account['USERID']
            session['EMAIL'] = account['EMAIL']
            return render_template("homepage.html")

        elif account['ROLL']==0:
            session['Loggedin'] = True
            session['USERID'] = account['USERID']
            return render_template("adminhome.html")
        else:
            msg=("Incorrect username / Password !")
    return render_template("login.html", msg = msg)


@app.route('/register', methods=['GET', 'POST'])
def Register():
    msg = ' '

    if request.method == 'POST':
        USERNAME = request.form["username"]
        EMAIL = request.form["email"]
        PASSWORD = request.form["password"]
        ROLL=1
        sql = "SELECT * FROM REGISTER WHERE USERNAME=? AND PASSWORD=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            msg = 'Account already exists! '
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', EMAIL):
            msg = ' Invalid email address! '
        elif not re.match(r'[A-Za-z0-9]+', USERNAME):
            msg = ' username must contain only characters and numbers! '
        else:
            sql2 = "SELECT count(*) FROM REGISTER"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.execute(stmt2)
            length = ibm_db.fetch_assoc(stmt2)
            print(length)
            insert_sql = " INSERT INTO REGISTER VALUES(?,?,?,?,?) "
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, USERNAME)
            ibm_db.bind_param(prep_stmt, 3, EMAIL)
            ibm_db.bind_param(prep_stmt, 4, PASSWORD)
            ibm_db.bind_param(prep_stmt, 5, ROLL)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            return render_template("login.html", msg=msg)
    return render_template("register.html")


@app.route('/home', methods=['GET', 'POST'])
def homepage():
    return render_template('homepage.html')

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    sql = 'SELECT * FROM MENU'
    stmt2 = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt2)
    rows = []
    while True:
        data = ibm_db.fetch_assoc(stmt2)
        print("data:", )
        if not data:
            break
        else:
            data['FOODID'] = str(data['FOODID'])
            rows.append(data)
    print('rows: ', rows)
    return render_template('menu.html', rows = rows)

@app.route('/admin_home', methods=['GET', 'POST'])
def admin_home():
    return render_template('adminhome.html')

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    
    select_sql = "SELECT * FROM ORDER  "
    stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)
    rows = []
    while data!= False:
        rows.append(data)
        data=ibm_db.fetch_tuple(stmt)
    print(rows)
    return render_template('transaction.html', rows=rows)
@app.route('/admenu', methods=['GET', 'POST'])
def addmenu():
    sql="SELECT * FROM REGISTER WHERE ROLL=0"
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)

    if request.method == 'POST':
        f = request.files['image']
        foodname = request.form['name']
        foodid = request.form['foodid']
        cost = request.form['cost']
        insert_sql ="INSERT INTO MENU VALUES (?,?,?,?,?) "
        stmt1 = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(stmt1, 1, data[0])
        ibm_db.bind_param(stmt1, 2, data[1])
        ibm_db.bind_param(stmt1, 3, foodname)
        ibm_db.bind_param(stmt1, 4, foodid)
        ibm_db.bind_param(stmt1, 5, cost)
        ibm_db.execute(stmt1)

        sql = 'SELECT * FROM MENU' 
        stmt2 = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt2)
        data = ibm_db.fetch_assoc(stmt2)
        print(data)
        # os.mkdir('myimages')
        basepath=os.path.dirname(__file__) #getting the current path i.e where app.py is present
        #print("current path",basepath)
        filepath=os.path.join(basepath,'myimages','.jpg') #from anywhere in the system we can give image but we want that image later  to process so we are saving it to uploads folder for reusing
        #print("upload folder is",filepath)
        f.save(filepath)
        
        cos.upload_file(Filename= filepath, Bucket='keerthimy', Key= foodid +'.jpg')

        print('data sent tô db2')
        # return render_template("view_menu.html") 
    return render_template('admenu.html')

@app.route('/view_menu', methods=['GET', 'POST'])
def veiwmenu():
    sql = 'SELECT * FROM MENU'
    stmt2 = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt2)
    rows = []
    while True:
        data = ibm_db.fetch_assoc(stmt2)
        print("data:", )
        if not data:
            break
        else:
            data['FOODID'] = str(data['FOODID'])
            rows.append(data)
    print('rows: ', rows)
    # return render_template("Orderpage.html")

    return render_template('view_menu.html',rows = rows)


@app.route('/add_to_cart/<string:FOODID>', methods = ['GET', 'POST'])
def add_to_cart(FOODID):
    sql = "SELECT * FROM REGISTER WHERE USERID= "+str(session['USERID'])
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    print("hello")
    print(account)
    DATE=datetime.datetime.now()
    print(DATE)

    sql="SELECT * FROM MENU WHERE FOODID ="+FOODID
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)
    print("hello2")

    insert_sql = "INSERT INTO ORDER VALUES (?,?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, account['USERNAME'])
    ibm_db.bind_param(prep_stmt, 2, data[3])
    ibm_db.bind_param(prep_stmt, 3, data[2])
    ibm_db.bind_param(prep_stmt, 4, data[4])
    ibm_db.bind_param(prep_stmt, 5, account['USERID'])
    ibm_db.bind_param(prep_stmt, 6, DATE)
    print('updated')
    ibm_db.execute(prep_stmt)

    return redirect(url_for('menu'))

    
@app.route('/order')
def order():
    select_sql = "SELECT * FROM ORDER WHERE USERID =" +str(session['USERID']) 
    stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)
    rows = []
    while data!= False:
        rows.append(data)
        data=ibm_db.fetch_tuple(stmt)
    print(rows)

    sql='SELECT SUM(COST) FROM ORDER WHERE USERID =' +str(session['USERID']) 
    # SELECT SUM(COST) FROM ORDER where userid
    stmt = ibm_db.prepare(conn,sql)
    # ibm_db.bind_param(stmt, 1, USERID)
    ibm_db.execute(stmt)
    account=ibm_db.fetch_tuple(stmt)
    print(account)
    total = account[0]
    print(total)
    return render_template('Orderpage.html', rows=rows, total=total) 



@app.route('/tracking', methods=['GET', 'POST'])
def tracking():
    return render_template('tracking.html')


@app.route('/profit', methods=['GET', 'POST'])
def profit():
    sql = "SELECT SUM(COST) FROM order;"
    stmt2 = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt2)
    profit = ibm_db.fetch_tuple(stmt2)
    print(profit)
    total_cost=profit[0]
    print(total_cost)

    return render_template('profit.html',profit = total_cost)

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('username',None)
    return render_template("login.html")

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')