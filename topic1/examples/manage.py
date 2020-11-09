from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://default:secret@127.0.0.1:3306/dogfood'


db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), unique=False, nullable=False)
    content = db.Column(db.String(4096), unique=False, nullable=False)
    _search = db.Column(db.Text, nullable=False)
    def __init__(self, *args, **kwargs):
        self.title = kwargs.get('title')
        self.content = self.sanitize(kwargs.get('content')) # Sanitize
        self._search = self.buildSearch() # Create a index field for full text search
    # category_id = db.Column(db.Integer, nullable=True)
    # user_id = db.Column(db.Integer, nullable=True)
    # rating = db.Column(db.Float, nullable=True)
    def buildSearch(self):
        return self.title + ' ' + self.removeHTMLTag(self.content)
    def removeHTMLTag(self, html):
        return 'xxx'
    def sanitize(self, html):
        return 'xxx'

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


# |-------------------------------------------------------------------------
# | Due to repeated pattern of multiple sorted columns
# | Ex: A > x OR (A = x AND (B > y OR (B = y AND C > z)))
# | Ex: A > x OR (A = x AND (B > y OR (B = y AND (C > z OR (C = z AND (D>w))))))
# |-----------------------------------------------------------------------/
@app.route("/blog", methods=["GET"])
def blog_create():
    q = request.form.get('q')
    filter_category_ids = request.form.get('category_ids')
    filter_user_ids  = request.form.get('author_ids')
    filter_ratings = request.form.get('ratings')
    query = db.QueryBuilder("select * from blogs")
    if len(filter_category_ids) > 0:
        query.where("category_id IN (?)", filter_category_ids)
    
    if len(filter_user_ids) > 0:
        query.where("user_id IN (?)", filter_user_ids)
    
    if len(filter_ratings) > 0:
        query.where("rating IN (?)", filter_ratings)
    
    next = request.form.get('next_page_token')
    if next != "":
        sorts = json_decode(base64_decode(next))
    else:
        sorts   = request.form.get('sorts')
    for sort in sorts:
        if sort.asc == True:
            query.order_by(sort.column + " asc")
        else:
            query.order_by(sort.column + " desc")
    lastSort := last.last()
    if is_not_unique_column(lastSort.column):
        sorts.append(dict{
            column: 'id',
            asc: true,
            cursor: last.get(sort.column)
        })

    limit = request.form.get('limit')
    if limit > 100:
        limit = 100
    elif limit < 10:
        limit = 10

    data = [Blog(), Blog()] 

    last := data[len(data)-1]
    
    sorts = request.form.get('sorts')
    for sort in sorts:
        sort.cursor = last.get(sort.column)
    
    lastSort := last.last()
    if is_not_unique_column(lastSort.column):
        sorts.append(dict{
            column: 'id',
            asc: true,
            cursor: last.get(sort.column)
        })
    

    next_page_token = base64_encode(json_encode(sorts))

    db.session.add(blog)
    db.session.commit()
    return jsonify(
        id = blog.id,
        title=blog.title,
        content=blog.content
    )

@app.route("/blog/<int:id>", methods=["GET"])
def blog_get(id):
    blog = Blog.query.filter_by(id=id).first()
    return jsonify(
        id = blog.id,
        title=blog.title,
        content=blog.content
    )

@app.route("/blog/<int:id>", methods=["DELETE"])
def blog_delete(id):
    blog = Blog.query.filter_by(id=id).first()
    if blog is None:
        abort(404, "Not found") 
    db.session.delete(blog)
    db.session.commit()
    return jsonify(
        id=blog.id,
        title=blog.title,
        content=blog.content
    )


@app.route("/")
def index():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
