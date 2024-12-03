from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Resource, Api, fields, Namespace, abort

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Flask-RESTx API
api = Api(app)

# Define a namespace for users
post_ns = Namespace('posts', description='Blog post management operations')

# Database Model
class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"Post(title={self.title}, description={self.description})"

# Serializer (for marshalling data)
post_model = post_ns.model('Post', {
    'id': fields.Integer(readonly=True, description='Post ID'),
    'title': fields.String(required=True, description='Post title'),
    'description': fields.String(required=True, description='Post description')
})

# Parser for request payload validation
post_parser = post_ns.parser()
post_parser.add_argument('title', type=str, required=True, help='Title cannot be blank')
post_parser.add_argument('description', type=str, required=True, help='Description cannot be blank')

# Resource Classes
@post_ns.route('/')
class Posts(Resource):
    @post_ns.marshal_list_with(post_model)
    def get(self):
        """Get all users"""
        posts = PostModel.query.all()
        return posts

    @post_ns.expect(post_parser)
    @post_ns.marshal_with(post_model, code=201)
    def post(self):
        """Create a new user"""
        args = post_parser.parse_args()
        post = PostModel(title=args['title'], description=args['description'])
        db.session.add(post)
        db.session.commit()
        return post, 201


@post_ns.route('/<int:id>')
class Post(Resource):
    @post_ns.marshal_with(post_model)
    def get(self, id):
        """Get a post by ID"""
        post = PostModel.query.get(id)
        if not post:
            abort(404, 'Post not found')
        return post

    @post_ns.expect(post_parser)
    @post_ns.marshal_with(post_model)
    def patch(self, id):
        """Update a post"""
        args = post_parser.parse_args()
        post = PostModel.query.get(id)
        if not post:
            abort(404, 'Post not found')

        post.title = args['title']
        post.description = args['description']
        db.session.commit()
        return post

    @post_ns.marshal_with(post_model, code=200)
    def delete(self, id):
        """Delete a post"""
        post = PostModel.query.get(id)
        if not post:
            abort(404, 'Post not found')

        db.session.delete(post)
        db.session.commit()
        
        posts = PostModel.query.all()
        return posts, 200

# Add the namespace to the API
api.add_namespace(post_ns, path='/api/posts')

@app.route('/')
def home():
    return '<h1>Flask-RESTx API</h1>'

if __name__ == '__main__':
    # db.create_all()  # Create database tables
    app.run(debug=True)
