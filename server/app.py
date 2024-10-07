#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_all_heroes():
    heroes = Hero.query.all()
    heroes_data = [hero.to_dict() for hero in heroes]
    return jsonify(heroes_data)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.filter_by(id=id).first()

    if not hero:
        return make_response({"error": "Hero not found"}, 404)

    return jsonify(hero.to_dict(rules=('-power.hero', '-hero_powers.hero')))

@app.route('/powers', methods=['GET'])
def get_all_powers():
    powers = Power.query.all()
    
    powers_data = [power.to_dict() for power in powers]
    
    return make_response(jsonify(powers_data), 200)

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.filter_by(id=id).first()
    
    if not power:
        return make_response(jsonify({"error": "Power not found"}), 404)
    
    power_data = power.to_dict()
    
    return make_response(jsonify(power_data), 200)

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.filter_by(id=id).first()

    if not power:
        return make_response(jsonify({"error": "Power not found"}), 404)

    data = request.get_json()

    if "description" in data:
        description = data["description"]
        if len(description) < 20:
            return make_response(jsonify({
                "errors": ["validation errors"]}), 400)

        power.description = description
        db.session.commit()

        return make_response(jsonify(power.to_dict()), 200)
    
    return make_response(jsonify({"errors": ["Invalid data provided"]}), 400)


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.json

    strength = data.get('strength')
    if strength not in ["Strong", "Weak", "Average"]:
        return jsonify({'errors': ["validation errors"]}), 400

    hero_id = data.get('hero_id')
    power_id = data.get('power_id')

    if not Hero.query.get(hero_id):
        return jsonify({'errors': ["Hero not found"]}), 404
    if not Power.query.get(power_id):
        return jsonify({'errors': ["Power not found"]}), 404

    hero_power = HeroPower(
        hero_id=hero_id,
        power_id=power_id,
        strength=strength
    )

    db.session.add(hero_power)
    db.session.commit()

    response = {
        'id': hero_power.id,
        'hero_id': hero_power.hero_id,
        'power_id': hero_power.power_id,
        'strength': hero_power.strength,
        'hero': Hero.query.get(hero_power.hero_id).name,
        'power': Power.query.get(hero_power.power_id).name
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
