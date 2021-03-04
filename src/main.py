"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
# from datetime import date, time, datetime
from models import db, User, Order
from flask_jwt_simple import (JWTManager, jwt_required, create_jwt, get_jwt_identity)
from passlib.hash import sha256_crypt


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = "jd"
jwt = JWTManager(app)

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg" : "Missing JSON info request"}),400

    params = request.get_json()
    user_name = params.get('user_name', None)
    password = params.get('password', None)

    if not user_name:
        return jsonify({"msg" : "Missing user_name parameter"}),400

    if not password:
        return jsonify({"msg" : "Missing password parameter"}),400

    specific_user = User.query.filter_by(
        user_name=user_name
    ).one_or_none()

    if isinstance(specific_user,User):
        if sha256_crypt.verify(password, specific_user.password):
            response={
                "jwt" : create_jwt(identity=specific_user.id)
            }
            return jsonify(response,specific_user.serialize()),200 
        else:
            return jsonify({"msg" : "Wrong Password"}),400

    else:
        return jsonify({"msg" : "User not found"}),400

@app.route('/signup', methods=['POST'])
def handle_signup():

    params = request.get_json()
    user_name = params.get('user_name', None)
    password = params.get('password', None)
    first_name = params.get('first_name', None)
    last_name = params.get('last_name', None)
    user_type = params.get('user_type', None)
    phone_number = params.get('phone_number', None)

    if not user_name:
        return jsonify({"msg" : "Missing user_name"}),400

    if not password:
        return jsonify({"msg" : "Missing password"}),400
    
    if not first_name:
        return jsonify({"msg" : "Missing first name"}),400
    
    if not last_name:
        return jsonify({"msg" : "Missing last name"}),400
    
    if not phone_number:
        return jsonify({"msg" : "Missing phone number"}),400

    specific_user = User.query.filter_by(
        user_name=user_name
    ).one_or_none()

    if isinstance(specific_user,User):
        return jsonify({"msg" : "User name already in use"}),400
    else:
        new_user= User(
            user_name = user_name,
            password = sha256_crypt.encrypt(str(password)),
            first_name = first_name,
            last_name = last_name,
            user_type = user_type,
            phone_number = phone_number
        )       
        db.session.add(new_user)
        try:
            db.session.commit()
            response={
                "jwt" : create_jwt(identity=new_user.id),
                "user_name": new_user.user_name
            }
            return jsonify(response),200

        except Exception as error:
            db.session.rollback()
            return jsonify({"msg" : error}),500

@app.route('/newOrder', methods=['POST'])
@jwt_required
def newOrder():
    specific_user_id = get_jwt_identity()
    user = User.query.get(specific_user_id)
    input_data = request.json
    
    new_order= Order(
        data = input_data,
        user_id = specific_user_id,
        working_id=0
    )
    db.session.add(new_order)  
    db.session.commit()
    return jsonify(new_order.id),200

@app.route('/working', methods=['POST'])
@jwt_required
def working():
    specific_user_id = get_jwt_identity()
    input_data = request.json
    order = Order.query.get(input_data["id"]) 

    order.working_id=specific_user_id
    order.status = "Working"
    db.session.commit()
    return jsonify(order.status),200

@app.route('/done', methods=['POST'])
@jwt_required
def doneRequest():
    specific_user_id = get_jwt_identity()
    input_data = request.json
    order = Order.query.get(input_data["id"])
    if input_data["notes"]:
        order.notes=input_data["notes"]
    order.working_id=specific_user_id
    order.status = "Done"
    db.session.commit()
    return jsonify(order.notes),200

@app.route('/allOrders', methods=['GET'])
def get_all_orders():
    order_query = Order.query.all()
    user_query = User.query.all()
    order_list = list(map(lambda each: each.serialize(), order_query))    
    user_list = list(map(lambda each: each.serialize(), user_query)) 
    response={
        "orders" : order_list,
        "users": user_list
    }  
    return jsonify(response), 200




# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
