from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # This looks into the templates folder for index.html
    return render_template('index.html')

import os

if __name__ == "__main__":
    # Cloud platforms provide a dynamic PORT variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)