from flask import Flask
import os

app = Flask(__name__)

ENV_NAME = os.getenv("ENV_NAME", "dev")

@app.route("/")
def home():
    return f"Hello Nitesh, app deployed by Jenkins to AWS EC2. Environment: {ENV_NAME}"

@app.route("/health")
def health():
    return {"status": "UP", "environment": ENV_NAME}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
