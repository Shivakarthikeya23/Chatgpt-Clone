from flask import Flask, render_template, jsonify, request, session
from flask_pymongo import PyMongo
from transformers import BlenderbotForConditionalGeneration, BlenderbotTokenizer
from datetime import timedelta

# Flask setup
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://shivakarthikeya5:shiva2311@chatgpt.pygnzrz.mongodb.net/chatgpt"
app.secret_key = "shiva_secret"
app.permanent_session_lifetime = timedelta(minutes=30)
mongo = PyMongo(app)

# Load BlenderBot
model_name = "facebook/blenderbot-3B"
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(model_name)

# Home page
@app.route("/")
def home():
    print("[HOME] Serving Home Page")
    chats = mongo.db.chats.find({})
    return render_template("index.html", myChats=list(chats))

# Chat API
@app.route("/api", methods=["POST"])
def qa():
    print("[API] Received POST /api")

    try:
        data = request.get_json()
        print("[API] Request JSON:", data)

        question = data.get("question")
        if not question:
            print("[API] No question provided.")
            return jsonify({"error": "No question provided"}), 400

        # Generate answer
        inputs = tokenizer(question, return_tensors="pt")
        reply_ids = model.generate(**inputs, max_length=300)
        answer = tokenizer.decode(reply_ids[0], skip_special_tokens=True)

        # Save to DB
        mongo.db.chats.insert_one({"question": question, "answer": answer})

        # Save to session memory
        session.setdefault("chat_history", []).append({"question": question, "answer": answer})
        session.modified = True

        print("[API] Answer generated successfully.")
        return jsonify({"question": question, "answer": answer})

    except Exception as e:
        print("[ERROR] Exception in /api:", str(e))
        return jsonify({"error": str(e)}), 500

# Prevent GET on /api
@app.route("/api", methods=["GET"])
def block_api_get():
    print("[WARNING] GET /api is not allowed.")
    return jsonify({"error": "GET not allowed on /api"}), 405

# Clear chat history
@app.route("/reset", methods=["POST"])
def reset():
    print("[RESET] Clearing session + MongoDB chat history")
    session["chat_history"] = []
    mongo.db.chats.delete_many({})
    return jsonify({"message": "Chat cleared."})

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5001)
