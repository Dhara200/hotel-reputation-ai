from flask import Blueprint, request, jsonify
from flask import session
from flask import render_template
from flask import redirect

from app.services.database_service import (
    get_connection,
    user_owns_business
)

business_bp = Blueprint("businesses", __name__)

@business_bp.route("/create-business")
def create_business_page():

    if "user_id" not in session:

        return redirect("/login-page")

    return render_template(
        "create_business.html"
    )
    
@business_bp.route(
    "/create-business-ui",
    methods=["POST"]
)
def create_business_ui():

    try:

        if "user_id" not in session:

            return redirect("/login-page")

        business_name = request.form.get(
            "business_name"
        )

        business_type = request.form.get(
            "business_type"
        )

        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get("country")

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO businesses
            (
                user_id,
                business_name,
                business_type,
                city,
                state,
                country
            )
            VALUES
            (%s,%s,%s,%s,%s,%s)
            """,
            (
                session["user_id"],
                business_name,
                business_type,
                city,
                state,
                country
            )
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(
            "/my-businesses"
        )

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500

@business_bp.route("/businesses", methods=["POST"])
def create_business():

    try:

        if "user_id" not in session:

            return jsonify({
                "message": "Please login first"
            }), 401

        data = request.get_json()

        user_id = session["user_id"]

        business_name = data.get("business_name")
        business_type = data.get("business_type")
        city = data.get("city")
        state = data.get("state")
        country = data.get("country")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO businesses
            (
                user_id,
                business_name,
                business_type,
                city,
                state,
                country
            )
            VALUES
            (%s,%s,%s,%s,%s,%s)
            """,
            (
                user_id,
                business_name,
                business_type,
                city,
                state,
                country
            )
        )

        conn.commit()

        business_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Business created successfully",
            "business_id": business_id
        }), 201

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500


@business_bp.route("/my-businesses", methods=["GET"])
def my_businesses():
 
    try:

        if "user_id" not in session:

            return redirect("/login-page")

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM businesses
            WHERE user_id=%s
            ORDER BY id DESC
            """,
            (session["user_id"],)
        )

        businesses = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template(
            "my_businesses.html",
            businesses=businesses,
            user_name=session["user_name"]
        )

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500
        
@business_bp.route("/upload-reviews/<int:business_id>")
def upload_reviews_page(business_id):

    try:

        if "user_id" not in session:

            return redirect("/login-page")

        if not user_owns_business(
            session["user_id"],
            business_id
        ):

            return "Access denied", 403

        conn = get_connection()

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                business_name,
                business_type
            FROM businesses
            WHERE id=%s
            """,
            (business_id,)
        )

        business = cursor.fetchone()

        cursor.close()
        conn.close()

        return render_template(
            "upload_reviews.html",
            business=business,
            business_id=business_id
        )

    except Exception as e:

        return jsonify({
            "message": str(e)
        }), 500
   