import google.generativeai as genai
import os, json
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient



# ---------------- ENV & API SETUP ----------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------------- DATABASE CONFIG ----------------
app.config["MONGO_URI"] = "mongodb://localhost:27017/wellness"
mongo = PyMongo(app)
users_collection = mongo.db.users
profiles_collection = mongo.db.profiles
yoga_col = mongo.db.yoga
meditation_col = mongo.db.meditation
routine_col = mongo.db.routine
user_routines = mongo.db.user_routines

# ---------------- DATABASE ----------------


# ---------------- CONTEXT PROCESSOR ----------------
@app.context_processor
def inject_user():
    if "user_id" in session:
        user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
        if user:
            profile = profiles_collection.find_one({"user_id": ObjectId(session["user_id"])})
            if profile:
                user['dosha'] = profile.get('dosha', None)
        return dict(user=user)
    return dict(user=None)

# ---------------- ROUTES ----------------

@app.route("/")
def landing():
    return render_template("landingpage.html")

# ----------- SIGN UP -----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("signup"))

        if users_collection.find_one({"email": email}):
            flash("User already exists! Please Sign In.")
            return redirect(url_for("signin"))

        hashed_pw = generate_password_hash(password)

        user_id = users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw
        }).inserted_id

        session["user_id"] = str(user_id)
        session["username"] = username
        flash("Sign Up successful!")
        return redirect(url_for("dashboard"))

    return render_template("signup.html")

# ----------- SIGN IN -----------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()

        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            flash("Sign In successful!")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("signin"))

    return render_template("signin.html")

# ----------- DASHBOARD -----------
# ✅ SAVE ROUTINE
@app.route("/api/save-routine", methods=["POST"])
def save_routine():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    user_id = session["user_id"]

    mongo.db.user_routines.update_one(
        {"user_id": user_id},
        {"$set": {"routine": data}},
        upsert=True
    )

    return jsonify({"message": "Saved successfully"})


# ✅ GET ROUTINE
@app.route("/api/get-user-routine")
def get_user_routine():
    if "user_id" not in session:
        return jsonify([])

    user_id = session["user_id"]

    routine = mongo.db.user_routines.find_one({"user_id": user_id})

    return jsonify(routine["routine"] if routine else [])
from bson import ObjectId

@app.route("/api/save-dosha", methods=["POST"])
def save_dosha():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    dosha = data.get("dosha")
    user_id = session["user_id"]

    mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"dosha": dosha}}
    )

    return jsonify({"message": "Dosha saved"})
from bson import ObjectId
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email").strip()
        new_password = request.form.get("password").strip()

        user = users_collection.find_one({"email": email})

        if not user:
            flash("User not found")
            return redirect(url_for("forgot_password"))

        hashed_pw = generate_password_hash(new_password)

        users_collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_pw}}
        )

        flash("Password updated successfully! Please login.")
        return redirect(url_for("signin"))

    return render_template("forgot_password.html")

@app.context_processor
def inject_user():
    if "user_id" in session:
        user = mongo.db.users.find_one({
            "_id": ObjectId(session["user_id"])
        })
        return dict(user=user)
    
    return dict(user=None)
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    user = users_collection.find_one({"_id": ObjectId(session["user_id"])})
    return render_template("dashboard.html", user=user)

# ----------- LOGOUT -----------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("landing"))

# ----------- PROFILE -----------
@app.route("/myprofile", methods=["GET", "POST"])
def myprofile():
    if "user_id" not in session:
        return redirect(url_for("signin"))

    user_id = ObjectId(session["user_id"])
    user = users_collection.find_one({"_id": user_id})
    profile = profiles_collection.find_one({"user_id": user_id})

    if request.method == "POST":
        profile_data = {
            "user_id": user_id,
            "name": request.form.get("name"),
            "email": user["email"],
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "weight": request.form.get("weight"),
            "height": request.form.get("height"),
            "activity": request.form.get("activity"),
            "sleep": request.form.get("sleep"),
            "stress": request.form.get("stress"),
            "allergies": request.form.get("allergies"),
            "conditions": request.form.get("conditions"),
            "goals": request.form.get("goals"),
            "diet": request.form.get("diet"),
            "foods": request.form.get("foods"),
            "fitness": request.form.get("fitness"),
            "dosha": request.form.get("dosha")
        }

        if profile:
            profiles_collection.update_one({"_id": profile["_id"]}, {"$set": profile_data})
        else:
            profiles_collection.insert_one(profile_data)

        flash("Profile saved successfully!")
        return redirect(url_for("dashboard"))

    return render_template("myprofile.html", profile=profile, user=user)

# ----------- REMEDIES -----------
@app.route("/remedies", methods=["GET", "POST"])
def remedies():
    query = request.form.get("query", "").strip()
    results = []

    if query:
        try:
            prompt = f"""
            Give 2–3 Ayurvedic remedies for {query} in JSON format.
            Use keys: disease, ingredients, method, frequency, dosha, category.
            """
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "")
            results = json.loads(text)
        except Exception as e:
            flash(f"Error fetching remedies: {e}", "error")

    return render_template("remedies.html", query=query, results=results)
# ----------- RECIPES PAGE -----------
@app.route("/recipes", methods=["GET", "POST"])
def recipes():
    query = request.form.get("query", "").strip()
    results = []

    if query:
        try:
            prompt = f"""
            User query: {query}

            Give exactly 3 Ayurvedic recipes.

            STRICT RULES:
            - Return ONLY JSON
            - No explanation
            - No text outside JSON

            Format:
            [
              {{
                "name": "...",
                "ingredients": ["...", "..."],
                "instructions": ["...", "..."],
                "benefits": ["...", "..."],
                "dosha": "..."
              }}
            ]
            """

            # ✅ CORRECT MODEL
            model = genai.GenerativeModel("gemini-2.5-flash")

            response = model.generate_content(prompt)

            text = response.text.strip().replace("```json", "").replace("```", "")

            print("RAW GEMINI RESPONSE:\n", text)

            import re
            try:
                json_text = re.search(r'\[.*\]', text, re.DOTALL).group()
                results = json.loads(json_text)
            except:
                print("JSON ERROR:", text)
                results = []

        except Exception as e:
            print("ERROR:", e)
            flash(f"Error fetching recipes: {e}")

    return render_template("recipes.html", query=query, results=results)

# ----------- DIET PAGE -----------
@app.route("/diet")
def diet():
    return render_template("diet.html")

# ----------- API (IMPORTANT 🔥) -----------
@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    import json, re

    search = request.args.get("search", "").strip()
    dosha = request.args.get("dosha", "").strip()

    try:
        prompt = f"""
        User query: "{search}"

        The user may enter:
        - an ingredient (like potato, milk)
        - OR a recipe name (like khichdi, dal)

        TASK:
        Generate exactly 3 Ayurvedic recipes based on the query.

        RULES:
        - If ingredient → recipes using that ingredient
        - If recipe name → explain that recipe
        - Include Ayurvedic perspective
        - Keep it practical and real

        OUTPUT FORMAT (STRICT JSON ONLY):
        [
          {{
            "name": "Recipe name",
            "ingredients": ["item1", "item2"],
            "process": ["step1", "step2"],
            "benefits": ["benefit1", "benefit2"],
            "dosha": "Vata/Pitta/Kapha"
          }}
        ]

        EXTRA:
        - If dosha "{dosha}" is provided, prefer recipes suitable for that dosha
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "")

        print("RAW GEMINI RESPONSE:\n", text)

        match = re.search(r"\[.*\]", text, re.DOTALL)

        if match:
            recipes = json.loads(match.group())
        else:
            recipes = []

        return jsonify(recipes)

    except Exception as e:
        print("ERROR:", e)
        return jsonify([])
# ----------- OTHER PAGES -----------
@app.route("/dosh")
def dosh():
    return render_template("dosh.html")

@app.route("/api/questions")
def get_questions():
    questions = list(mongo.db.dosh_test.find({}, {"_id": 0}))
    return jsonify(questions)

@app.route("/routine")
def routine():
    return render_template("routine.html")

@app.route("/api/routine")
def get_routine():
    routines = list(routine_col.find({}, {"_id": 0}))
    return jsonify(routines)

@app.route("/panchakarma")
def panchakarma():
    return render_template("panchkarma.html")

# ✅ YOGA PAGE
@app.route("/yoga")
def yoga():
    return render_template("yoga.html")

# ✅ API (THIS IS MAIN PART 🔥)
@app.route("/api/data")
def get_data():
    yoga = list(yoga_col.find({}, {"_id": 0}))
    meditation = list(meditation_col.find({}, {"_id": 0}))

    return jsonify({
        "yoga": yoga,
        "meditation": meditation
    })

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)