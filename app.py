from flask import Flask,render_template,request

from logic import read_csv_file
from logic import check_employees
from logic import find_managers_for_employees
from logic import find_root_employees
from logic import find_managers
from logic import find_cycles

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# ANALYZE CSV
@app.route("/analyze", methods=["POST"])
def analyze():

    # upload the file
    uploaded_file = request.files.get("file")

    if uploaded_file is None:
        return render_template(
            "index.html",
            error="Please choose a CSV file to upload."
        )

    # read the file
    try:
        rows = read_csv_file(uploaded_file)
    except ValueError as error:
        return render_template(
            "index.html",
            error=str(error)
        )
    
    #check employee
    good_employees, identity_errors = check_employees(rows)

    #check employee manager
    (manager_of,manager_errors,employees_with_manager_error) = find_managers_for_employees(good_employees)

    #find root employee
    roots = find_root_employees(good_employees,manager_of,employees_with_manager_error)

    # find managers
    managers = find_managers(good_employees,manager_of)

    #find id of employee that are part of the reporting cycle
    cyclic_ids = find_cycles(manager_of)

    #find complete employee info from cycle
    cyclic_employees = []

    for employee in good_employees:
        employee_id = employee["employee_id"]
        if employee_id in cyclic_ids:
            cyclic_employees.append(employee)



    #combine all the error
    all_errors = []

    for error in identity_errors:
        all_errors.append(error)

    for error in manager_errors:
        all_errors.append(error)


    #send everyhting to index.html
    return render_template(
        "index.html",
        total_rows=len(rows),
        accepted_count=len(good_employees),
        errors=all_errors,
        roots=roots,
        managers=managers,
        cyclic_employees=cyclic_employees
    )

if __name__ == "__main__":
    app.run(debug=True)
