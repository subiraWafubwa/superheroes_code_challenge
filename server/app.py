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
            return make_response(jsonify({"errors": ["Description must be at least 20 characters long"]}), 400)

        power.description = description
        db.session.commit()

        return make_response(jsonify(power.to_dict()), 200)
    
    return make_response(jsonify({"errors": ["Invalid data provided"]}), 400)


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    strength = data.get('strength')
    power_id = data.get('power_id')
    hero_id = data.get('hero_id')

    allowed_strengths = ['Strong', 'Weak', 'Average']
    if strength not in allowed_strengths:
        return make_response(jsonify({"errors": ["Strength must be one of: 'Strong', 'Weak', 'Average'"]}), 400)

    hero = Hero.query.filter_by(id=hero_id).first()
    power = Power.query.filter_by(id=power_id).first()

    if not hero or not power:
        return make_response(jsonify({"errors": ["Hero or Power not found"]}), 404)

    hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)

    try:
        db.session.add(hero_power)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"errors": ["Failed to create HeroPower"]}), 400)

    # Return the new HeroPower data
    response_data = {
        "id": hero_power.id,
        "hero_id": hero.id,
        "power_id": power.id,
        "strength": hero_power.strength,
        "hero": hero.to_dict(),
        "power": power.to_dict()
    }

    return make_response(jsonify(response_data), 201)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
