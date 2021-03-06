from flask import Flask, render_template, request, redirect, url_for
import os
from bson.objectid import ObjectId
import pymongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(MONGO_URI)

# define my db_name
DB_NAME = "book_review"

# The Home Route
# Display all the book listing


@app.route('/')
def home():
    # extract the search terms
    search_terms = request.args.get('search-terms')
    # create empty object
    criteria = {}
    # if there are search terms, add it into criteria object
    if search_terms != "" and search_terms is not None:
        criteria['title'] = {
            "$regex": search_terms,
            "$options": 'i'
        }
    # fetch data from mongodb
    books = client[DB_NAME].bookListing.find(criteria)
    return render_template('home.template.html', books=books)


@app.route('/book/add')
def add_book():
    return render_template('add_book.template.html')


@app.route('/book/add', methods=['POST'])
def process_add_book():
    book_title = request.form.get('title')
    book_author = request.form.get('author')
    book_comments = request.form.get('comments')

    client[DB_NAME].bookListing.insert_one({
        'title': book_title,
        'author': book_author,
        'comments': book_comments,
    })
    return "New book added"


@app.route('/book/edit/<id>')
def edit_book(id):
    # find the book by its id
    # match by the objectid
    books = client[DB_NAME].bookListing.find_one({
        "_id": ObjectId(id)
    })

    return render_template('edit_book.template.html', books=books)


@app.route('/book/edit/<id>', methods=['POST'])
def process_edit_book(id):
    book_title = request.form.get('title')
    book_author = request.form.get('author')
    book_comments = request.form.get('comments')
    client[DB_NAME].bookListing.update_one({
        "_id": ObjectId(id)
    },  {
        "$set": {
            "title": book_title,
            "author": book_author,
            "comments": book_comments
        }
    })
    return redirect(url_for('home'))

@app.route('/book/delete/<id>')
def delete_book(id):
    books=client[DB_NAME].bookListing.find_one({
        '_id': ObjectId(id)
    })
    return render_template('confirm_delete_book.template.html', books=books)


@app.route('/book/delete/<id>', methods=['POST'])
def process_delete_book(id):
    client[DB_NAME].bookListing.remove({
        "_id" :ObjectId(id)
    })
    return redirect( url_for('home'))


# "magic code" -- boilerplate
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
