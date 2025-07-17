from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
client = MongoClient("mongodb+srv://nihalmotukuri:6gSkQW3gXw111k6L@flask-cluster.eftmwx7.mongodb.net/?retryWrites=true&w=majority&appName=flask-cluster")
db = client['crud-db']
collection = db['crud-app']
students = db['students']
courses = db['courses']
authors = db['authors']
books = db['books']

@app.route('/')
def index():
    users = list(collection.find())
    return render_template('index.html', users=users)

@app.route('/add', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        collection.insert_one({"name": name, "email": email})
        return redirect(url_for("index"))
    return render_template("add_user.html")

@app.route('/students')
def get_students():
    students_list = list(students.find())
    for student in students_list:
        enrolled = []
        for cid in student.get('course_ids', []):
            course = courses.find_one({'_id': cid})
            if course:
                enrolled.append(course['name'])
        student['enrolled_courses'] = enrolled
    return render_template('students.html', students=students_list)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    all_courses = list(courses.find())
    if request.method == 'POST':
        name = request.form['name']
        selected_ids = request.form.getlist('courses')
        course_ids = [ObjectId(cid) for cid in selected_ids]
        students.insert_one({"name": name, "course_ids": course_ids})
        return redirect('/students')
    return render_template('add_student.html', courses=all_courses)

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_user(id):
    user = collection.find_one({"_id": ObjectId(id)})
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": name, "email": email}}
        )
        return redirect(url_for("index"))
    return render_template("edit_user.html", user=user)

# @app.before_request
# def seed_courses():
#     if courses.count_documents({}) == 0:
#         courses.insert_many([
#             {'name': 'Python'},
#             {'name': 'Flask'},
#             {'name': 'MongoDB'}
#         ])

@app.route("/delete/<id>")
def delete_user(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("index"))

@app.route("/add_book", methods=['', 'POST'])

if __name__ == '__main__':
    app.run(debug=True)