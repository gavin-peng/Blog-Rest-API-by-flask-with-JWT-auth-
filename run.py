from flask import Flask, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from data import blogs


app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
    db.create_all()


import resources, models

# Clear blogs table and insert data to blogs table
@app.before_first_request
def init_db():
    db.session.query(models.BlogModel).delete()
    for blog in blogs:
        new_blog = resources.BlogModel(
            author = blog['author'], 
            title = blog['title'],
            content =blog['content']
        )
        try:
            new_blog.save_to_db()
        except:
            print('message: Something went wrong')

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)



api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.SecretResource, '/secret')
api.add_resource(resources.BlogListAPI, resources.list_route, endpoint = 'blogs')
api.add_resource(resources.BlogItemAPI, resources.item_route, endpoint = 'blog')

@app.errorhandler(404)
def not_found(error):
    return (jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return (jsonify({'error': 'Bad request'}), 400)

