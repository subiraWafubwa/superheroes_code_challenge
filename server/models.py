from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower',  back_populates='hero')

    # add serialization rules
    serialize_rules = ('-power.hero', '-hero_powers',)

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship('HeroPower',  back_populates='power')

    # add serialization rules
    serialize_rules = ('-hero.power', '-hero_powers', )

    # add validation
    @validates('description')
    def validate_description(self, key, value):
        if not value or len(value) < 20:
            raise ValueError('Description must be at least 20 characters long')
        return value

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    # add relationships
    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    # add serialization rules
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers',)

    # add validation
    @validates('strength')
    def validate_strength(self, key, value):
        allowed_strengths = ['Strong', 'Weak', 'Average']
        if value not in allowed_strengths:
            raise ValueError(f'Strength must be one of: {allowed_strengths}')
        return value

    def __repr__(self):
        return f'<HeroPower {self.id}>'
