import os
import logging
import datetime
import psycopg2
from flask import Flask, jsonify, request, g
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt,
    create_refresh_token, get_jwt_identity
)
from config import Config
from db import FDataBase


app = Flask(__name__)
app.config.from_object(Config)
dbase = None
jwt = JWTManager(app)
base_url = "/api/v1"
if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    handlers=[
        logging.FileHandler(f"logs/log_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")}.log"), 
        logging.StreamHandler()
    ]
)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "link_db"):
        g.link_db.close()

@app.before_request
def before_request():
    global dbase
    if not hasattr(g, "link_db"):
        con = psycopg2.connect(Config.DATABASE_URI)
        con.autocommit = True
        g.link_db = con
    dbase = FDataBase(g.link_db)

@app.route(base_url+"/oauth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    if dbase.is_user_exists(username):
        return jsonify({"message": "User already exists"}), 400
    password = data.get("password")
    role = data.get("role", "user") 
    if dbase.post_user(username, password, role):
        return jsonify({"message": "User created successfully"}), 201
    return jsonify({"message": "Database error"}), 500

@app.route(base_url+"/oauth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity() 
    claims = get_jwt() 
    new_access_token = create_access_token(
        identity=current_user,
        additional_claims={"role": claims["role"]}  
    )
    return jsonify(access_token=new_access_token), 200

@app.route(base_url+"/oauth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not dbase.auth_user_by_pswd(username, password):
        return jsonify({"message": "Invalid credentials"}), 401
    user = dbase.get_user(username, password)
    access_token = create_access_token(
        identity=username, 
        additional_claims={"role": user["role"]} 
    )
    refresh_token = create_refresh_token(
        identity=username,
        additional_claims={"role": user["role"]} 
    )
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route(base_url+"/list-article", methods=["GET"])
@jwt_required(optional=True)  
def list_article():
    current_user = get_jwt_identity()  
    if current_user:
        claims = get_jwt() 
        if claims["role"] == "admin":
            table, err = dbase.get_article_list("private")
        else: 
            table, err = dbase.get_article_list("need_login")
    else:
        table, err = dbase.get_article_list("public")
    if not(table):
        logging.error(str(err))
        return jsonify({"message": "error during get list of articles", "id_err": err["logger_message_id"]}), 500
    return jsonify(table), 200

@app.route(base_url+"/article/<int:article_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def exist_article_operation(article_id):
    article, err = dbase.get_article(article_id)
    if not(article):
        return jsonify({"message": "unknown article_id"}), 404
    claims = get_jwt() 
    is_admin = claims["role"] == "admin"
    if request.method == "GET":
        if not(is_admin) and (article["privacy"] != "public"):
            return jsonify({"message": "Forbidden article"}), 403
        return jsonify({
            "id": article["id"],
            "title": article["title"],
            "value": article["value"],
            "privacy": article["privacy"],
            "author_id": article["insered_by"]
        }), 200
    if claims["role"] != "admin":
        return jsonify({"message": "Forbidden action"}), 403
    if request.method == "DELETE":
        article, err = dbase.delete_article(article_id)
        if not(article):
            logging.error(str(err))
            return jsonify({"message": "error during deleting", "id_err": err["logger_message_id"]}), 500
        return jsonify({"deleted": article}), 200
    data = request.get_json()
    title = data.get("title", article["title"])
    value = data.get("value", article["value"])
    privacy = data.get("privacy", article["privacy"])
    article, err = dbase.put_article(article_id, title, value, privacy)
    if not(article):
            logging.error(str(err))
            return jsonify({"message": "error during putting", "id_err": err["logger_message_id"]}), 500
    return jsonify({"puted": article}), 200

@app.route(base_url+"/article", methods=["POST"])
@jwt_required()
def post_article():
    claims = get_jwt() 
    if claims["role"] != "admin":
        return jsonify({"message": "Forbidden action"}), 403
    data = request.get_json()
    title = data.get("title")
    value = data.get("value")
    privacy = data.get("privacy")
    author_id = data.get("insered_by")
    article, err = dbase.post_article(title, value, privacy, author_id)
    if not(article):
        return jsonify({"message": "error during post", "id_err": err["logger_message_id"]}), 500
    return jsonify({"posted": article}), 200
    


if __name__ == "__main__":
    app.run(port=1235, debug=True)
