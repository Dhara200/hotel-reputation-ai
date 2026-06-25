from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.services.database_service import get_connection
from flask import render_template
from flask import redirect
from flask import request
from flask import session
from flask import url_for

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register-page", methods=["GET"])
def register_page():

    return render_template(
        "register.html"
    )
    
@auth_bp.route("/register-page", methods=["POST"])
def register_form():
    
  try:

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    if not all([name, email, password]):
        return "All fields are required"

    password_hash = generate_password_hash(password)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (name, email, password_hash)
        VALUES (%s, %s, %s)
        """,
        (
            name,
            email,
            password_hash
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/login-page")

  except Exception as e:

     return str(e), 500

@auth_bp.route("/login-page", methods=["GET"])
def login_page():

    return render_template(
        "login.html"
    )

@auth_bp.route("/login-page", methods=["POST"])
def login_form():

    try:

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:

            return "Invalid credentials"

        if not check_password_hash(
            user["password_hash"],
            password
        ):

            return "Invalid credentials"

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id
            FROM businesses
            WHERE user_id=%s
            LIMIT 1
            """,
            (user["id"],)
    )

        business = cursor.fetchone()

        cursor.close()
        conn.close()

        if business:

            return redirect(
            "/my-businesses"
    )

        return redirect(
        "/create-business"
    )

    except Exception as e:

        return str(e), 500
    
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/login-page"
    )
    
    
@auth_bp.route("/register", methods=["POST"])
def register():

    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not all([name, email, password]):
            return jsonify({
                "message": "All fields are required"
            }), 400

        password_hash = generate_password_hash(password)

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (name, email, password_hash)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "message": "User registered successfully"
        }), 201

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500
        
from werkzeug.security import check_password_hash

@auth_bp.route("/login", methods=["POST"])
def login():

    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return jsonify({
                "message": "Invalid email or password"
            }), 401

        if not check_password_hash(
                user["password_hash"],
                password):

            return jsonify({
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user["id"],
            "name": user["name"]
        })

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500
        