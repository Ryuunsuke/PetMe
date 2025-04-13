from flask import request, jsonify, Blueprint, session
from functions import auth

authenticator = Blueprint('authenticator', __name__)

@authenticator.route('/login', methods=['POST'])
def loginClient():
    if request.content_type != 'application/json':
        return jsonify({"success": False, "message": "Content-Type must be application/json"}), 415
    else:
        try:
            data = request.get_json()  # Extract JSON data correctly
            print(f"Received data: {data}")  # Log the incoming data for debugging
            
            email = data.get('email')
            password = data.get('password')

            if email == "" or password == "":
                session["loggedin"] = False
                return jsonify({
                    "success": True, 
                    "message": "No email nor password, Client is not logged in.",
                    "loggedin": False
                    }), 200

            if auth.check_email(email):  # Ensure this function checks if the user exists
                if auth.check_pass(email) == password:  # Ensure this compares the password correctly
                    session["loggedin"] = True  # Store login status in session
                    return jsonify({
                        "success": True,
                        "message": "Login Successful",
                        "loggedin": True
                    }), 200
                else:
                    return jsonify({"success": False, "message": "Incorrect username or password"}), 401
            else:
                return jsonify({"success": False, "message": "User does not exist"}), 404
            
        except Exception as e:
            # Log the error for debugging
            print(f"Error occurred: {str(e)}")
            return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
    
@authenticator.route('/register', methods=['POST'])
def registerClient():
    if request.content_type != 'application/json':
        return jsonify({"success": False, "message": "Content-Type must be application/json"}), 415
    else:
        try:
            data = request.get_json()
            
            email = data.get('email')
            password = data.get('password')

            if auth.check_email(email) == email:
                return jsonify({"success": False, "message": "Email already exist"}), 400
            else: 
                auth.register(email, password)
                return jsonify({"success": True, "message": "Client registered successfully!"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500