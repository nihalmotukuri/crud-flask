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

@app.route('/get_books')
def get_books():
    books_list = list(books.find({}))
    return render_template('books.html', books_list = books_list)

@app.route('/get_authors')
def get_authors():
    authors_list = list(authors.find({}))
    return render_template('authors.html', authors_list = authors_list)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        author_name = request.form['author_name']
        authors.insert_one({ 'author_name': author_name })
        return redirect('/get_authors')
    return render_template('add_author.html')

@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        books.insert_one({ 'title': title, 'genre': genre })
        return redirect('/get_books')
    return render_template('add_book.html')

@app.route('/update_book/<book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    authors_list = list(authors.find({}))
    
    if request.method == 'POST':
        book = books.find_one({'_id': ObjectId(book_id)})
        author_ids = request.form.getlist('authors')
        print(author_ids)
        author_names = []

        for author in authors_list:
            
            if author['_id'] in author_ids:
                author_names.append(author['author_name'])

            # authors.update_one({'_id': ObjectId(a_id)}, {'$set': {'book_ids': book_ids}})

        books.update_one({'_id': ObjectId(book_id)}, {'$set': {'author_ids': author_ids, 'author_names': author_names}})

        return redirect('/get_books')
    
    return render_template('update_book.html', authors_list = authors_list)

@app.route('/update_author/<author_id>', methods=['GET', 'POST'])
def update_author(author_id):
    books_list = list(books.find({}))
    if request.method == 'POST':
        book_ids = request.form.getlist('books')
        book_titles = []
        for b_id in book_ids:
            book = books.find_one({'_id': ObjectId(b_id)})
            book_titles.append(book['title'])
            if book.get('author_ids'):
                author_ids = book['author_ids']
            else: 
                author_ids = []
            if author_id not in author_ids:
                author_ids.append(author_id)
                books.update_one({'_id': ObjectId(b_id)}, {'$set': {'author_ids': author_ids}})
        authors.update_one({'_id': ObjectId(author_id)}, {'$set': {'book_ids': book_ids}})
        return redirect('/get_authors')
    return render_template('update_author.html', book_titles = book_titles, books_list = books_list)

if __name__ == '__main__':
    app.run(debug=True)