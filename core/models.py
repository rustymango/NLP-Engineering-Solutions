from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:facetrol1@localhost:5433/civil_calc"
db = SQLAlchemy(app)

class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem = db.Column(db.String(10000), nullable=False)
    calculation_steps = db.Column(db.String(10000), nullable=True)
    answer = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Problem: {self.problem}"
    
    def __init__(self, problem, calculation_steps, answer):
        self.problem = problem
        self.calculation_steps = calculation_steps
        self.answer = answer