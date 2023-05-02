from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json

import sys
sys.path.insert(0, "/civil_calc/core")
from calculate import runCalculations
from show_results import showSteps
from models import app, db
from models import Calculation

CORS(app)

def format_calculation(calculation):
    return {
        "id": calculation.id,
        "problem": calculation.problem,
        "calculation_steps": calculation.calculation_steps,
        "answer": calculation.answer
    }

@app.route("/")
def hello():
    return "Please use URL: '127.0.0.1:5000/calculations'"

# create and perform calculation
@app.route("/calculations", methods = ["POST"])
def create_calculation():
    problem = request.json["problem"]

    result, calculation_target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr = runCalculations(problem)
    answer = json.dumps(result)
    # answer = request.json["answer"]

    if calculation_target == "Cr":
        kRatio_formula, kxRatio_num, kyRatio_num, lambdaK_formula, lambdaK_num, Cr_formula, Cr_num = showSteps(result, calculation_target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr)
        calculation_steps = f"{kRatio_formula},  {kxRatio_num},  {kyRatio_num},  {lambdaK_formula},  {lambdaK_num},  {Cr_formula},  {Cr_num}"
    else:
        lambda_formula, lambda_num, kRatio_formula, kRatio_num = showSteps(result, calculation_target, ratio_Kx, ratio_Ky, lambda_K, Lx, Ly, radius_gx, radius_gy, area, Cr)
        calculation_steps = f"{lambda_formula},  {lambda_num},  {kRatio_formula},  {kRatio_num}"

    calculation_steps = json.dumps(calculation_steps)
    # calculation_steps = request.json["calculation_steps"]

    calculation = Calculation(problem, calculation_steps, answer)
    db.session.add(calculation)
    db.session.commit()
    return format_calculation(calculation)

# get all calculations (unnecessary?)
@app.route("/calculations", methods = {"GET"})
def get_calculations():
    calculations = Calculation.query.order_by(Calculation.id.asc()).all()
    calculation_list = []
    for calculation in calculations:
        calculation_list.append(format_calculation(calculation))
    return {"calculations": calculation_list}

# get single calculation
@app.route("/calculations/<id>", methods = ["GET"])
def get_calculation(id):
    calculation = Calculation.query.filter_by(id=id).one()
    formatted_calculation = format_calculation(calculation)
    return {"calculation": formatted_calculation}

# delete one calculation
@app.route("/calculations/<id>", methods = ["DELETE"])
def delete_calculation(id):
    calculation = Calculation.query.filter_by(id=id).one()
    db.session.delete(calculation)
    db.session.commit()
    return f"Calculations deleted."

# delete all calculations
# @app.route("/calculations", methods = ["DELETE"])
# def delete_calculation():
#     Calculation.query.delete()
#     db.session.commit()
#     return f"Calculations deleted."

# edit calculation (unnecessary?)
# @app.route("/calculations/<id>", methods = ["PUT"])
# def update_calculation(id):
#     calculation = Calculation.query.filter_by(id=id)
#     description = request.json["description"]
#     calculation.update(dict(description = description))
#     db.session.commit()
#     return {"calculation": format_calculation(calculation.one())}

if __name__ == "__main__":
    app.run()