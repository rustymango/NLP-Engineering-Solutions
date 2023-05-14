from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:facetrol1@localhost:5433/civil_calc_2"
db = SQLAlchemy(app)

class Calculation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem = db.Column(db.String(10000), nullable=False)
    # calculation_steps = db.Column(db.String(10000), nullable=True)
    formula_1 = db.Column(db.String(1000), nullable=False)
    values_1 = db.Column(db.String(1000), nullable=False)
    formula_2 = db.Column(db.String(1000), nullable=False)
    values_2 = db.Column(db.String(1000), nullable=False)
    formula_3 = db.Column(db.String(1000), nullable=False)
    values_3 = db.Column(db.String(1000), nullable=False)
    answer = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Problem: {self.problem}"
    
    def __init__(self, problem, formula_1, values_1, formula_2, values_2, formula_3, values_3, answer):
        self.problem = problem
        # self.calculation_steps = calculation_steps
        self.formula_1 = formula_1
        self.values_1 = values_1
        self.formula_2 = formula_2
        self.values_2 = values_2
        self.formula_3 = formula_3
        self.values_3 = values_3
        self.answer = answer