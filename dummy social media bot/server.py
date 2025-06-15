from flask import Flask, request, jsonify, make_response
import json
from lambda_function import lambda_handler
from flask_cors import CORS
from scheduler import scheduler_task 


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://marketing-bot-frontend.s3-website.ap-south-1.amazonaws.com"}})

@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/trigger-scheduler', methods=["POST"])  # ✅ new endpoint
def trigger_scheduler():
    try:
        scheduler_task()  # Trigger the scheduler task directly
        return jsonify({"status": "Scheduler successfully triggered"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def handle_request(path):
    print("Incoming Headers:", request.headers)
    event = {
        "path": f"/{path}",
        "httpMethod": request.method,
        "headers": dict(request.headers),
        "queryStringParameters": request.args.to_dict(),
        "body": request.data.decode("utf-8") if request.data else None,
        "isBase64Encoded": False
    }

    response = lambda_handler(event, None)

    if isinstance(response["body"], str) and response["body"].strip():
        response_body = json.loads(response["body"])
    else:
        response_body = response["body"] if response["body"] is not None else {}

    flask_response = make_response(jsonify(response_body), response["statusCode"])
    flask_response.headers["Access-Control-Allow-Origin"] = "*"
    flask_response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    flask_response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return flask_response
# ✅ Background scheduler startup (not ideal for production)
import threading
from scheduler import run_scheduler
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)