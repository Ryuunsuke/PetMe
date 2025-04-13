from flask import request, jsonify, Blueprint, session

authenticator = Blueprint('authenticator', __name__)

@authenticator.route('/login', methods=['POST'])
def loginUser():
    pass
    
@authenticator.route('/register', methods=['POST'])
def registerUser():
    pass