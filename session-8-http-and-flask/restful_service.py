from flask import Flask, render_template, jsonify, request
from models import db, Product
from products_service import products_bp

app = Flask(__name__)

app.config.from_object('db_config')

db.init_app(app)

app.register_blueprint(products_bp)

@app.route('/')  # Root path
def home():
    return 'hello world'

if __name__ == '__main__':
    app.run(debug=True)
