from types import EllipsisType
from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import yaml

app = Flask(__name__)
app.secret_key = "super secret key"
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:ROOT@localhost/hr_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db=SQLAlchemy(app)
#Emplyoee Model
class employee(db.Model):
    employee_id=db.Column(db.Integer,primary_key=True)
    email_id=db.Column(db.String(255))
    department_name=db.Column(db.String(255))
    first_name=db.Column(db.String(255))
    last_name=db.Column(db.String(255))
    date_of_birth=db.Column(db.String(50),nullable=False)
    department_id=db.Column(db.Integer)
    job_id=db.Column(db.Integer)
#Deparment Model
class department(db.Model):
    department_id=db.Column(db.Integer,primary_key=True)
    department_name=db.Column(db.String(255))
    manager_id=db.Column(db.Integer)
    manager_name=db.Column(db.String(255))


class jobs(db.Model):
    job_id=db.Column(db.Integer,primary_key=True)
    job_title=db.Column(db.String(255))
    min_salary=db.Column(db.String(255))
    max_salary=db.Column(db.String(255))


#Main Page - Login Page
@app.route('/')
def Root():
     return render_template('Login.html')

#After successful/unsccussful login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': 
     LoginDetails = request.form
     login_user = LoginDetails['Username']
     login_password = LoginDetails['password']
    cur = mysql.connection.cursor()
    resultValue = cur.execute('SELECT * FROM login_data where login_user =%s and login_password=%s',(login_user,login_password))
    if resultValue > 0:
     return redirect('/DisplayEmpInfo')
    else:
     flash("Login Failed - No  user found or Wrong Credentials")
     return redirect('/')
 

@app.route('/DisplayEmpInfo')
def LandingPage():
    cur = mysql.connection.cursor()
    emps=db.engine.execute("SELECT * FROM employee")
    #depts = db.engine.execute("SELECT * FROM department")
    return render_template('DisplayEmployeeInfo.html',emps=emps)
         

@app.route('/CreatEmployee')
def create_employee():
    dept=db.engine.execute("SELECT * FROM `department`")
    job=db.engine.execute("SELECT * FROM `jobs`")
    return render_template('CreateEmployee.html',dept=dept,job=job)

@app.route('/CreatEmployee', methods=['GET', 'POST'])
def InsertEmployeeData():
    if request.method == 'POST':
        EmplyeeDetail = request.form
        employee_id = EmplyeeDetail['EmployeeId']
        first_name = EmplyeeDetail['Fname']
        last_name = EmplyeeDetail['Lname']
        email_id = EmplyeeDetail['Email']
        department_name = EmplyeeDetail['department_name']
        department_name_valid = department_name.split()
        department_name_valid_d = department_name_valid[1]
        date_of_birth = EmplyeeDetail['date_of_birth']
        department_id_valid_d = department_name_valid[0]
        job_title = EmplyeeDetail['job_title']
        job_title_v = job_title.split()
        job_title_v_data = job_title_v[0]
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employee(email_id, employee_id,first_name,last_name,department_name,date_of_birth,department_id,job_id) VALUES(%s, %s,%s,%s,%s,%s,%s,%s)",(email_id, employee_id,first_name,last_name,department_name_valid_d,date_of_birth,department_id_valid_d,job_title_v_data))
        mysql.connection.commit()
        cur.close()
        flash("Employee Information created Successully")
        return redirect('/DisplayEmpInfo')
 
@app.route("/edit/<string:employee_id>",methods=['POST','GET'])
def edit(employee_id):
     dept = db.engine.execute("SELECT * FROM department")
     posts=employee.query.filter_by(employee_id=employee_id).first()
     job=db.engine.execute("SELECT * FROM `jobs`")
     return render_template('editemployee.html',posts=posts,dept=dept,job=job)


@app.route("/edit/update",methods=['POST','GET'])
def updateemployee():
 if request.method=="POST":
    EmplyeeDetail = request.form
    employee_id = EmplyeeDetail.get('EmployeeId')
    first_name = EmplyeeDetail.get('Fname')
    last_name = EmplyeeDetail.get('Lname')
    email_id = EmplyeeDetail.get('Email')
    date_of_birth = EmplyeeDetail.get('date_of_birth')
    department_name = EmplyeeDetail['department_name']
    department_name_valid = department_name.split()
    department_name_valid_d = department_name_valid[1]
    date_of_birth = EmplyeeDetail['date_of_birth']
    department_id_valid_d = department_name_valid[0]
    db.engine.execute(f"UPDATE `employee` SET `email_id` = '{email_id}', `first_name` = '{first_name}',`last_name` = '{last_name}', `date_of_birth` = '{date_of_birth}', `department_name` = '{department_name_valid_d}', `department_id` = '{department_id_valid_d}' WHERE `employee`.`employee_id` = {employee_id}")
    flash("Update Successful ")
    return redirect('/DisplayEmpInfo')
    

@app.route("/delete/<string:empid>",methods=['POST','GET'])
def delete(empid):
    db.engine.execute(f"DELETE FROM `employee` WHERE `employee`.`employee_id`={empid}")
    flash("Deleted Successful")
    return redirect('/DisplayEmpInfo')

@app.route('/CreatDepartment')
def create_Department():
 return render_template('CreateDepartment.html')


@app.route('/CreatDepartment', methods=['GET', 'POST'])
def InsertDeaprtmentData():
    if request.method == 'POST':
        # Fetch form data
        EmplyeeDetail = request.form
        DepId = EmplyeeDetail['DepId']
        Depname = EmplyeeDetail['Depname']
        ManagerId = EmplyeeDetail['ManagerId']
        ManagerName = EmplyeeDetail['ManagerName']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO department(department_id, department_name,manager_id,manager_name) VALUES(%s, %s,%s,%s)",(DepId, Depname,ManagerId,ManagerName))
        mysql.connection.commit()
        cur.close()
        flash("Department Created Successfully")
        return redirect('/DisplayDeptInfo')

@app.route('/DisplayDeptInfo')
def Display_Department_info():
    depts=db.engine.execute("SELECT * FROM `department`")
    return render_template('DisplayDeptInfo.html',depts=depts)

if __name__ == '__main__':
 app.run(debug=True)