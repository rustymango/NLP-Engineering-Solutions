from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from models import app, db
from models import Calculation

def format_calculation(calculation):
    return {
        "id": calculation.id,
        "problem": calculation.problem,
        "calculation_steps": calculation.calculation_steps,
        "answer": calculation.answer
    }

@app.route("/")
def hello():
    return "Hey"

# create and perform calculation
@app.route("/calculations", methods = ["POST"])
def create_calculation():
    problem = request.json["problem"]
    calculation_steps = request.json["calculation_steps"]
    answer = request.json["answer"]

    calculation = Calculation(problem, calculation_steps, answer)
    db.session.add(calculation)
    db.session.commit()
    return format_calculation(calculation)

# get all calculations
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

# delete calculation
@app.route("/calculations/<id>", methods = ["DELETE"])
def delete_calculation(id):
    calculation = Calculation.query.filter_by(id=id).one()
    db.session.delete(calculation)
    db.session.commit()
    return f"Calculation(id: {id}) deleted."

# edit calculation
@app.route("/calculations/<id>", methods = ["PUT"])
def update_calculation(id):
    calculation = Calculation.query.filter_by(id=id)
    description = request.json["description"]
    calculation.update(dict(description = description))
    db.session.commit()
    return {"calculation": format_calculation(calculation.one())}

if __name__ == "__main__":
    app.run()