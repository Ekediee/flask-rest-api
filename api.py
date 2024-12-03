from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app) 
api = Api(app)

class PostModel(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self): 
        return f"Post(title = {self.title}, description = {self.description})"

post_args = reqparse.RequestParser()
post_args.add_argument('title', type=str, required=True, help="Title cannot be blank")
post_args.add_argument('description', type=str, required=True, help="Description cannot be blank")

postFields = {
    'id':fields.Integer,
    'title':fields.String,
    'description':fields.String,
}

class Posts(Resource):
    @marshal_with(postFields)
    def get(self):
        posts = PostModel.query.all() 
        return posts 
    
    @marshal_with(postFields)
    def post(self):
        args = post_args.parse_args()
        post = PostModel(title=args["title"], description=args["description"])
        db.session.add(post) 
        db.session.commit()
        posts = PostModel.query.all()
        return posts, 201
    
class Post(Resource):
    @marshal_with(postFields)
    def get(self, id):
        post = PostModel.query.filter_by(id=id).first() 
        if not post: 
            abort(404, message="post not found")
        return post 
    
    @marshal_with(postFields)
    def patch(self, id):
        args = post_args.parse_args()
        post = PostModel.query.filter_by(id=id).first() 
        if not post: 
            abort(404, message="post not found")
        post.title = args["title"]
        post.description = args["description"]
        db.session.commit()
        return post 
    
    @marshal_with(postFields)
    def delete(self, id):
        post = PostModel.query.filter_by(id=id).first() 
        if not post: 
            abort(404, message="Post not found")
        db.session.delete(post)
        db.session.commit()
        posts = PostModel.query.all()
        return posts

    
api.add_resource(Posts, '/api/posts/')
api.add_resource(Post, '/api/posts/<int:id>')

@app.route('/')
def home():
    return '<h1>Flask REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True) 