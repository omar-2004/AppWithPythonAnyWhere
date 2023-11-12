import http.cookies
from flask import *
import random
from datetime import timedelta
import os
import mysql.connector
from flask_login import *


def VerifyLogIn(username, password):
    sql = "SELECT U.role, W.ID, W.FirstName, W.LastName FROM users U, workersid W WHERE user = %s AND password = %s AND W.ID = U.id"
    mycursor.execute(sql, (username, password))
    myresult = mycursor.fetchall()
    try:
        myresult = myresult[0]
        return myresult
    except:
        return None

class User(UserMixin):
    def __init__(self, username,userID, role, FirstName, LastName):
        self.role = role
        self.id = username
        self.userID = userID
        self.FirstName = FirstName
        self.LastName = LastName

    @staticmethod
    def get(username):
        user_data = users.get(username)
        if user_data:
            return User(user_data.get("username"),user_data.get("userID"),user_data.get("role"), user_data.get("FirstName"), user_data.get("LastName"))
        return None

class Guest:
    id = str
    FirstName = str
    LastName = str

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=15)
login_manager = LoginManager(app)
mydb = mysql.connector.connect(host="localhost", 
                               user="root", 
                               password="", 
                               database="appdb")
mycursor = mydb.cursor()

valid_api_keys = {
    "71031886606-a1f90-4afca-a306-bc05ac63d896b9b": "api_client_name",
    "71031886606-a1f90-4afca-a306-bc05ac63d896b9s": "api_client_name"
}

def api_key_required(f):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Api-Key')
        if api_key and api_key in valid_api_keys:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401  
    return decorated_function


@login_manager.user_loader
def load_user(username):
    return User.get(username)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Routes

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == "U":
            return redirect(url_for('Modify'))
        elif current_user.role == "A":
            return redirect(url_for('AdminDashborad'))
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    global users
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verificationOfTheUser = VerifyLogIn(username, password)
        if verificationOfTheUser:
                users = {username: {
                            'userID'      : verificationOfTheUser[1],
                            'FirstName'      : verificationOfTheUser[2],
                            'LastName'      : verificationOfTheUser[3],
                            'role'      : verificationOfTheUser[0]
                            }
                        }
                user = User(username, users[username]["role"], users[username]["userID"], users[username]["FirstName"], users[username]["LastName"])
                login_user(user)
                if verificationOfTheUser[0] == "A":
                    return redirect(url_for('AdminDashborad'))
                else:
                    return redirect(url_for('Modify'))
    return render_template('index.html', classNameOnError="error") 

@app.route('/modify/')
@login_required
def Modify():    
    if current_user.role != "U":
        return redirect(url_for('unauthorized'))
    return render_template('HourModifyAdd.html',userID=current_user.userID, FirstName=current_user.FirstName,LastName=current_user.LastName)

@app.route('/Admin/dashborad')
@login_required
def AdminDashborad():
    if current_user.role != "A":
        return redirect(url_for('unauthorized'))
    return render_template('AdminDashborad.html',  rangeOfYears=range(2020, 2025))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# API Routes

@app.route('/api/data/modifyHoursAndUpdate',  methods=['POST'])
@login_required
def returnDateAndTotalHours():
    data = request.get_json()
    input_value = data.get('data')
    sql = "SELECT totalOfHourForTheDay, comment FROM workinghour WHERE ID = %s AND Date = %s"
    mycursor.execute(sql, (current_user.userID, input_value))
    myresult = mycursor.fetchall()
    if myresult != []:
        myresult = myresult[0]
        return jsonify(success=True, numOfHours=myresult[0], comments=myresult[1])
    else:
        return jsonify(success=False)


@app.route('/api/data/AddAndUpdate',  methods=['POST'])
@login_required
def AddAndUpdateDataBase():
    data = request.get_json()
    userID = current_user.userID
    inputDate =  data.get('inputDate')
    inputNumberOfWorking =  data.get('inputNumberOfWorking')
    inputComment =  data.get('inputComment')
    sql = "INSERT INTO workinghour (ID, Date, totalOfHourForTheDay, comment) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE totalOfHourForTheDay = VALUES(totalOfHourForTheDay), comment = VALUES(comment);"
    try:
        mycursor.execute(sql, (userID, inputDate, inputNumberOfWorking, inputComment))
        mydb.commit()
        return jsonify(success=True)
    except mysql.connector.Error as err:
        return jsonify(success=True)


@app.route('/api/data/GetYearAndInformation',  methods=['POST'])
def GetYearAndInformation():
    data = request.get_json()
    inputYear =  data.get('inputYear')
    sql = "SELECT MONTH(Date), SUM(totalOfHourForTheDay) FROM workinghour WHERE YEAR(Date) = %s AND ID = %s GROUP BY MONTH(Date);"
    try:
        mycursor.execute(sql, (inputYear, Guest.id,))
        myresult = mycursor.fetchall()
        print(myresult)
        return jsonify(success=True, myresult=myresult)   
    except mysql.connector.Error as err:
        return jsonify(success=False)


@app.route('/viewMonth/<int:month>')
@login_required
def viewMonth(month):
    TitleName="View Month n°"+str(month)
    UserNameAndLastName = Guest.FirstName + " " + Guest.LastName
    sql = "SELECT Date as 'Date', totalOfHourForTheDay as 'NbrHours', comment as 'Comment'  FROM workinghour WHERE ID = %s AND MONTH(Date) = %s"
    mycursor.execute(sql, (Guest.id, month))
    rangeInMonth = mycursor.fetchall()
    fields = ["Date", "Hours", "Comment"]
    return render_template('ViewMonth.html',fields=fields,TitleName=TitleName ,UserNameAndLastName=UserNameAndLastName,rangeInMonth=rangeInMonth )

@app.route('/viewYear/<int:year>')
@login_required
def viewYear(year):
    TitleName="View Year n°"+str(year)
    UserNameAndLastName = Guest.FirstName + " " + Guest.LastName
    sql = "SELECT YEAR(Date), MONTH(Date), SUM(totalOfHourForTheDay) FROM workinghour WHERE ID = %s AND YEAR(Date) = %s GROUP BY MONTH(Date);"
    mycursor.execute(sql, (Guest.id, year))
    rangeInMonth = mycursor.fetchall()
    months = [
            "01. January",
            "02. February",
            "03. March",
            "04. April",
            "05. May",
            "06. June",
            "07. July",
            "08. August",
            "09. September",
            "10. October",
            "11. November",
            "12. December"
          ]
    fields = ["Year","Month",  "Total Hours"]
    return render_template('ViewMonth.html',fields=fields, months=months,TitleName=TitleName,UserNameAndLastName=UserNameAndLastName,rangeInMonth=rangeInMonth )


@app.route('/api/data/GetTheUserFromDataBase',  methods=['POST'])
@login_required
def GetTheUserFromDataBase():
    Guest.id = ""
    Guest.FirstName = ""
    Guest.LastName = ""
    data = request.get_json()
    GivingUserID =  data.get('GivingUserID')
    GivingUserFisrtName =  data.get('GivingUserFisrtName')
    GivingUserLastName =  data.get('GivingUserLastName')
    sql = "SELECT ID , FirstName, LastName FROM workersid WHERE ID = %s OR (FirstName =%s AND LastName =%s) "
    try:
        mycursor.execute(sql, (GivingUserID, GivingUserFisrtName, GivingUserLastName,))
        myresult = mycursor.fetchone()
    except mysql.connector.Error as err:
        return jsonify(success=False)

    if myresult:
        Guest.id = myresult[0]
        Guest.FirstName = myresult[1]
        Guest.LastName = myresult[2]
        return jsonify(success=True, GuestID=Guest.id, GuestFirstName=Guest.FirstName, GuestLastName=Guest.LastName)
    else:
        return jsonify(success=False) 

# Error handlers
@login_manager.unauthorized_handler
def Userunauthorized401():
    return render_template('unauthorized.html'), 401

@app.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404page.html'), 404

@app.errorhandler(405)
def page_not_found(error):
    return render_template('unauthorized.html'), 405


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)