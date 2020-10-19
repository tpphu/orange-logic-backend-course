from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://default:secret@127.0.0.1:3306/dogfood'


db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), unique=False, nullable=False)
    content = db.Column(db.String(4096),    unique=False, nullable=False)

@app.route("/blog", methods=["POST"])
def blog_create():
    title = request.form.get('title')
    content = request.form.get('content')
    blog = Blog(title=title, content=content)
    db.session.add(blog)
    db.session.commit()
    return jsonify(
        id = blog.id,
        title=blog.title,
        content=blog.content
    )

@app.route("/")
def index():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True, threaded=True)