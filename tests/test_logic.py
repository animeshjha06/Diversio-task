# Import the functions we want to test.

from logic import check_employees
from logic import find_managers_for_employees
from logic import find_root_employees
from logic import find_cycles


# HELPER FUNCTION
def make_row(
    row_number, employee_id, email, manager_id="", manager_email="", name=None
):
    if name is None:
        employee_name = employee_id
    else:
        employee_name = name

    employee = {}

    employee["row_number"] = row_number
    employee["employee_id"] = employee_id
    employee["employee_name"] = employee_name
    employee["email"] = email
    employee["manager_id"] = manager_id
    employee["manager_email"] = manager_email
    employee["department"] = "Eng"

    return employee


# Test 1----------------------
def test_duplicate_employee_id_is_rejected():

    rows = []

    employee1 = make_row(2, "E1", "e1@x.com")
    employee2 = make_row(3, "E1", "e1-again@x.com")

    rows.append(employee1)
    rows.append(employee2)

    good_rows, errors = check_employees(rows)

    assert good_rows == []
    assert len(errors) == 2


# Test 2------------
def test_employee_with_no_manager_fields_is_a_root():

    employee = make_row(2, "E1", "e1@x.com")

    rows = []
    rows.append(employee)

    manager_of, errors, bad = find_managers_for_employees(rows)

    roots = find_root_employees(rows, manager_of, bad)

    assert len(roots) == 1
    assert roots[0]["employee_id"] == "E1"


# Test 3------------------------
def test_cycle_is_detected():

    manager_of = {}

    manager_of["A"] = "B"
    manager_of["B"] = "A"

    cyclic_ids = find_cycles(manager_of)

    expected_cycles = {"A", "B"}

    assert cyclic_ids == expected_cycles
