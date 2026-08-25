import csv
import io

REQUIRED_COLUMNS = [
    "employee_id",
    "employee_name",
    "email",
    "manager_id",
    "manager_email",
    "department",
]


# 1. Read csv----------------
def read_csv_file(uploaded_file):

    # Read the uploaded CSV file
    file_content = uploaded_file.read()

    # Convert the CSV text into an dictionary.
    text = file_content.decode("utf-8-sig")
    file_object = io.StringIO(text)
    reader = csv.DictReader(file_object)

    # Stop early if the file has no header row.
    if reader.fieldnames is None:
        raise ValueError("The CSV file does not have headers.")

    headers = []

    # Remove extra spaces from the column names
    for header in reader.fieldnames:
        clean_header = header.strip()
        headers.append(clean_header)

    # Check whether all required columns exist.
    for required_column in REQUIRED_COLUMNS:
        if required_column not in headers:
            raise ValueError(f"Missing required column: {required_column}")

    rows = []
    row_number = 1

    # Clean each row and standardize field formats.
    for raw_row in reader:
        row_number = row_number + 1

        employee = {}
        employee["row_number"] = row_number

        # Normalize the employee ID field.
        employee_id = raw_row.get("employee_id")

        if employee_id is None:
            employee_id = ""

        employee["employee_id"] = employee_id.strip()

        # Normalize the employee name field.
        employee_name = raw_row.get("employee_name")

        if employee_name is None:
            employee_name = ""

        employee["employee_name"] = employee_name.strip()

        # Normalize and lowercase the employee email field.
        email = raw_row.get("email")

        if email is None:
            email = ""

        employee["email"] = email.strip().lower()

        # Normalize the manager ID field.
        manager_id = raw_row.get("manager_id")

        if manager_id is None:
            manager_id = ""

        employee["manager_id"] = manager_id.strip()

        # Normalize and lowercase the manager email field.
        manager_email = raw_row.get("manager_email")

        if manager_email is None:
            manager_email = ""

        employee["manager_email"] = manager_email.strip().lower()

        # Normalize the department field.
        department = raw_row.get("department")

        if department is None:
            department = ""

        employee["department"] = department.strip()

        # Keep the cleaned employee row for later validation.
        rows.append(employee)

    return rows


# 2. Find duplicate values------------------


def find_duplicate_values(rows, field_name):

    # Dictionary to store how many times each value appears.
    counts = {}

    for row in rows:
        value = row[field_name]
        if value != "":
            if value not in counts:
                counts[value] = 0

            counts[value] = counts[value] + 1

    duplicates = set()

    # Collect values that appear more than once.
    for value in counts:

        count = counts[value]
        if count > 1:
            duplicates.add(value)

    return duplicates


# # 3. Check exployee--------------------
#     Check every employee.

#     We check:

#     1. employee_id is not empty.
#     2. employee_id is not duplicated.
#     3. email is not empty.
#     4. email is not duplicated.

#     Return:

#     good_rows = valid employees
#     errors = invalid employee information


def check_employees(rows):
    # Identify duplicate employee IDs and emails first.
    duplicate_ids = find_duplicate_values(rows, "employee_id")
    duplicate_emails = find_duplicate_values(rows, "email")

    good_rows = []
    errors = []

    for row in rows:
        problems = []

        # check emp id.
        if row["employee_id"] == "":
            problems.append("employee_id is missing")
        else:
            if row["employee_id"] in duplicate_ids:
                problems.append("duplicate employee_id: " + row["employee_id"])

        # check email
        if row["email"] == "":
            problems.append("email is missing")
        else:
            if row["email"] in duplicate_emails:
                problems.append("duplicate email: " + row["email"])

        # Save errors or valid employee
        if len(problems) > 0:
            for problem in problems:
                error = {"row_number": row["row_number"], "message": problem}
                errors.append(error)
        else:
            good_rows.append(row)

    return good_rows, errors


# 4. Findmanagaer----------------------


def find_managers_for_employees(employees):
    # Create a dictionary where employee ID is the key.
    employee_by_id = {}

    for employee in employees:
        employee_id = employee["employee_id"]
        employee_by_id[employee_id] = employee

    # Create another dictionary where email is the key.
    employee_by_email = {}

    for employee in employees:
        email = employee["email"]
        employee_by_email[email] = employee

    manager_of = {}
    errors = []

    employees_with_manager_error = set()

    for employee in employees:
        employee_id = employee["employee_id"]
        manager_id = employee["manager_id"]
        manager_email = employee["manager_email"]

        # Skip employees who do not reference a manager.
        if manager_id == "" and manager_email == "":
            continue

        found_by_id = None

        # Try to find manager using manager_id.
        if manager_id != "":
            if manager_id in employee_by_id:
                found_by_id = employee_by_id[manager_id]

        found_by_email = None

        # Try to find manager using manager_email.
        if manager_email != "":
            if manager_email in employee_by_email:
                found_by_email = employee_by_email[manager_email]


        #  manager_id exists but doesn't match anyone.
        if manager_id != "" and found_by_id is None:
            error = {
                "row_number": employee["row_number"],
                "message": (
                    "manager_id '" + manager_id + "' does not match any employee"
                ),
            }
            errors.append(error)
            employees_with_manager_error.add(employee_id)
            continue

        #  manager_email exists but doesn't match anyone.
        if manager_email != "" and found_by_email is None:
            error = {
                "row_number": employee["row_number"],
                "message": (
                    "manager_email '" + manager_email + "' does not match any employee"
                ),
            }
            errors.append(error)
            employees_with_manager_error.add(employee_id)
            continue

        # If both manager references exist, they must point to the same person.
        if found_by_id is not None:
            if found_by_email is not None:
                id_person = found_by_id["employee_id"]
                email_person = found_by_email["employee_id"]

                if id_person != email_person:
                    error = {
                        "row_number": employee["row_number"],
                        "message": (
                            "manager_id and manager_email "
                            "point to different employees"
                        ),
                    }
                    errors.append(error)
                    employees_with_manager_error.add(employee_id)
                    continue

        # find manager
        manager = None
        if found_by_id is not None:
            manager = found_by_id
        else:
            manager = found_by_email

        # Employee cannot be their own manager
        manager_employee_id = manager["employee_id"]

        if manager_employee_id == employee_id:
            error = {
                "row_number": employee["row_number"],
                "message": "employee cannot be their own manager",
            }
            errors.append(error)
            employees_with_manager_error.add(employee_id)
            continue

        # Record the employee-to-manager relationship.
        manager_of[employee_id] = manager_employee_id

    return (manager_of, errors, employees_with_manager_error)


# 5. Find root employees------------------


def find_root_employees(employees, manager_of, employees_with_manager_error):

    # Collect employees who are not assigned a valid manager.
    roots = []

    for employee in employees:
        employee_id = employee["employee_id"]

        if employee_id not in manager_of:
            if employee_id not in employees_with_manager_error:
                roots.append(employee)

    return roots


# 6. Finf manager and count their reports-----------------


def find_managers(employees, manager_of):

    # create a dictionary:
    # employee id -> employee information

    employee_by_id = {}

    for employee in employees:
        employee_id = employee["employee_id"]
        employee_by_id[employee_id] = employee

    # count how many direct reports each manager has.
    report_counts = {}

    for employee_id in manager_of:
        manager_id = manager_of[employee_id]
        if manager_id not in report_counts:
            report_counts[manager_id] = 0
        report_counts[manager_id] += 1

    #create the final manager list
    managers = []

    for manager_id in report_counts:
        count = report_counts[manager_id]

        manager_employee = employee_by_id[manager_id]
        manager = {"employee": manager_employee, "report_count": count}
        managers.append(manager)

    return managers


# 7. Find reporting cycle--------------------------
def find_cycles(manager_of):

    # set store employees who are part of a reporting cycle.
    cyclic_ids = set()
    # set store employess we have already chceked
    finished_ids = set()

    for start_id in manager_of:
        if start_id in finished_ids:
            continue

        chain = []
        seen_this_walk = {}

        current_id = start_id

        while True:
            if current_id not in manager_of:
                break
            if current_id in finished_ids:
                break
            if current_id in seen_this_walk:
                cycle_start = seen_this_walk[current_id]

                for index in range(cycle_start, len(chain)):
                    cyclic_employee = chain[index]
                    cyclic_ids.add(cyclic_employee)
                break

            position = len(chain)
            seen_this_walk[current_id] = position

            chain.append(current_id)
            current_id = manager_of[current_id]

        for employee_id in chain:
            finished_ids.add(employee_id)

    return cyclic_ids
