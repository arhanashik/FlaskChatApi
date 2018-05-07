from flask import Flask, json, Response, render_template, request
from flaskext.mysql import MySQL
import os
from random import randint

template_dir = os.path.abspath('../pages')
app = Flask(__name__, template_folder=template_dir)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'db_chat'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def index():
    message = 'Chat Api:' + '<br><br>/register = New Registration' + '<br><br>/verify = Verify registered id' \
              + '<br><br>/sync = Synchronize Contacts'
    return '<p>'+message+'</p>'


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/add_user',  methods=['POST'])
def register_user():
    user_id = 0
    name = request.form['name']
    phone_num = request.form['phone_num']

    if request.method == 'POST':

        if not name:
            code = 404
            message = "Missing name(required)"
        elif not phone_num:
            code = 404
            message = "Missing phone_num(required)"

        else:
            sms_code = randint(100000, 999999)
            query = "INSERT INTO tbl_users (name, phone_num, sms_code) VALUES(%s,%s,%s)"
            user = (name, phone_num, sms_code)
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute(query, user)
            user_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()

            if not user_id:
                code = 500
                message = "Registration failed!"
            else:
                code = 200
                message = "Successfully Registered"

    else:
        sms_code = 0
        code = 400
        message = "Invalid Request"

    data = {
        'code': code,
        'message': message,
        'user_id': user_id,
        'name': name,
        'phone_num': phone_num,
        'sms_code': sms_code
    }
    js = json.dumps(data)
    resp = Response(js, status=200, mimetype='application/json')
    return resp


@app.route('/verify')
def verify():
    return render_template('verify.html')


@app.route('/verifier',  methods=['POST'])
def verifier():
    if request.method == 'POST':
        phone_num = request.form['phone_num']
        sms_code = request.form['sms_code']

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tbl_users WHERE phone_num='" + phone_num + "' and sms_code='" + sms_code + "'")
        db_data = cursor.fetchone()
        if db_data is None:
            code = 404
            message = "Phone Number or SMS verification code is wrong!"
        else:
            cursor.execute(
                "UPDATE tbl_users SET sms_code='verified' WHERE  phone_num='" + phone_num + "'")
            code = 200
            message = "Verified successfully"

        conn.commit()
        cursor.close()
        data = {
            'code': code,
            'message': message,
            'phone_num': phone_num,
            'sms_code': sms_code
        }
        js = json.dumps(data)
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    else:
        pass


@app.route('/sync')
def sync():
    return render_template('sync.html')


@app.route('/synchronizer',  methods=['GET'])
def synchronizer():
    if request.method == 'GET':
        phone_num = request.args.get('phone_num')
        contact = request.args.get('contacts')
        friend_list = []
        total_friend = 0

        if phone_num is None or contact is None:
                code = 400
                message = "Missing phone_num or contacts"

        else:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * from tbl_users where phone_num='" + phone_num + "'")
            if not cursor.rowcount:
                code = 404
                message = "You are not a registered user!"
            else:
                code = 200
                message = "Users found!"
                contacts = contact.split(',')
                for c in contacts:
                    if c:
                        crr = conn.cursor()
                        crr.execute("SELECT * from tbl_users where phone_num='" + c.strip() + "'")
                        row = crr.fetchone()
                        if row is not None:
                            user = {
                                'user_id': row[0],
                                'name': row[1],
                                'phone_num': row[2]
                            }
                            friend_list.append(user)
                            total_friend += 1
                        crr.close()

            cursor.close()
            conn.close()

        data = {
            'code': code,
            'message': message,
            'phone_num': phone_num,
            'friend_list': friend_list,
            'total_friend': total_friend
        }
        js = json.dumps(data)
        resp = Response(js, status=200, mimetype='application/json')
        return resp

    else:
        pass


if __name__ == '__main__':
    app.run()

