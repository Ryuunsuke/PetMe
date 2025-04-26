from flask import request, jsonify, Blueprint, session
from functions import fauth

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

            if fauth.check_email(email):  # Ensure this function checks if the user exists
                if fauth.check_pass(email) == password:  # Ensure this compares the password correctly
                    session["loggedin"] = True  # Store login status in session
                    session["user_id"], session["user_role"] = fauth.get_user_id(email)
                    print("User ID: ", session["user_id"])
                    print("User role: ", session["user_role"])
                    return jsonify({
                        "success": True,
                        "message": "Login Successful",
                        "loggedin": True
                    }), 200
                else:
                    return jsonify({"success": False, "message": "Incorrect username or password", "loggedin": False}), 401
            else:
                return jsonify({"success": False, "message": "User does not exist", "loggedin": False}), 404
            
        except Exception as e:
            # Log the error for debugging
            print(f"Error occurred: {str(e)}")
            return jsonify({"success": False, "message": f"Error: {str(e)}", "loggedin": False}), 500
    
@authenticator.route('/register', methods=['POST'])
def registerClient():
    if request.content_type != 'application/json':
        return jsonify({"success": False, "message": "Content-Type must be application/json"}), 415
    else:
        try:
            data = request.get_json()
            
            email = data.get('email')
            password = data.get('password')

            if fauth.check_email(email) == email:
                return jsonify({"success": False, "message": "Email already exist"}), 400
            else: 
                fauth.register(email, password)
                return jsonify({"success": True, "message": "Client registered successfully!"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500