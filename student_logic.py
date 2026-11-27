"""
student_logic.py
Data layer for the Student Management System.

Data structures
---------------
* students : a Python LIST that holds every student record (ordered collection).
* record   : a Python DICTIONARY for one student with the keys
             'student_id', 'name', 'major' and 'cgpa'.

The GUI (student_management_gui.py) and the console menu
(student_management_cli.py) both call the functions in this file, so the
rules (validation, linear search, statistics) are written only once.
"""

from decimal import Decimal, ROUND_HALF_UP

# The main collection: a list of dictionaries (kept in memory while running).
students = []

# Sample records used for testing and for the demonstration.
SAMPLE_DATA = [
    {"student_id": "S101", "name": "Amina Rahman", "major": "Computer Science", "cgpa": 3.75},
    {"student_id": "S102", "name": "Daniel Smith", "major": "Cybersecurity", "cgpa": 3.40},
    {"student_id": "S103", "name": "Maria Lopez", "major": "Computer Science", "cgpa": 3.90},
    {"student_id": "S104", "name": "John Carter", "major": "Information Systems", "cgpa": 3.10},
    {"student_id": "S105", "name": "Carol", "major": "Data Science", "cgpa": 3.65},
]


def format_cgpa(value):
    """Format a CGPA/average to 2 decimals using normal half-up rounding (3.575 -> 3.58)."""
    d = Decimal(str(round(value, 8))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return str(d)


# ---------------------------------------------------------------- validation
def validate_cgpa(value):
    """Return the CGPA as a float rounded to 2 places, or raise ValueError."""
    try:
        cgpa = float(str(value).strip())
    except ValueError:
        raise ValueError("CGPA must be a number (for example 3.75).")
    if cgpa != cgpa:  # rejects NaN, which float("nan") would otherwise allow
        raise ValueError("CGPA must be a number (for example 3.75).")
    if cgpa < 0.0 or cgpa > 4.0:
        raise ValueError("CGPA must be between 0.00 and 4.00.")
    return round(cgpa, 2)


def validate_text(value, label):
    """Return the stripped text, or raise ValueError if it is empty."""
    text = str(value).strip()
    if text == "":
        raise ValueError(label + " cannot be empty.")
    return text


# ------------------------------------------------------------ linear search
def find_index(student_list, student_id):
    """
    Linear search: look at the records one by one from the start of the list.
    Returns the index of the matching record, or -1 if the list ends first.
    Time complexity: O(n).
    """
    wanted = str(student_id).strip().casefold()
    for i in range(len(student_list)):
        if student_list[i]["student_id"].casefold() == wanted:
            return i
    return -1


# --------------------------------------------------------------------- CRUD
def add_student(student_list, student_id, name, major, cgpa):
    """Validate the four fields, build a dictionary and append it. O(n) because of
    the duplicate-ID check (the append itself is O(1))."""
    student_id = validate_text(student_id, "Student ID")
    name = validate_text(name, "Student name")
    major = validate_text(major, "Major")
    cgpa = validate_cgpa(cgpa)
    if find_index(student_list, student_id) != -1:
        raise ValueError("Student ID '" + student_id + "' already exists.")
    record = {"student_id": student_id, "name": name, "major": major, "cgpa": cgpa}
    student_list.append(record)
    return record


def display_students(student_list):
    """Traverse the list and return the records as formatted text lines. O(n)."""
    if len(student_list) == 0:
        return ["No student records found."]
    lines = ["{:<10}{:<24}{:<24}{:>6}".format("ID", "Name", "Major", "CGPA")]
    lines.append("-" * 64)
    for s in student_list:
        lines.append("{:<10}{:<24}{:<24}{:>6.2f}".format(
            s["student_id"], s["name"], s["major"], s["cgpa"]))
    return lines


def search_student(student_list, student_id):
    """Return the record dictionary for a Student ID, or None if not found. O(n)."""
    index = find_index(student_list, student_id)
    if index == -1:
        return None
    return student_list[index]


def update_student(student_list, student_id, name=None, major=None, cgpa=None):
    """
    Update name, major and/or CGPA of an existing student.
    A field passed as None (or an empty string) keeps its old value.
    The Student ID is the key and is not changed. O(n) for the search.
    """
    index = find_index(student_list, student_id)
    if index == -1:
        raise ValueError("Student ID '" + str(student_id).strip() + "' was not found.")
    record = student_list[index]
    # Validate everything first so a bad value never leaves a half-updated record.
    new_name = record["name"] if name is None or str(name).strip() == "" else validate_text(name, "Student name")
    new_major = record["major"] if major is None or str(major).strip() == "" else validate_text(major, "Major")
    new_cgpa = record["cgpa"] if cgpa is None or str(cgpa).strip() == "" else validate_cgpa(cgpa)
    record["name"], record["major"], record["cgpa"] = new_name, new_major, new_cgpa
    return record


def delete_student(student_list, student_id):
    """Search for the ID, then remove the record with pop(). The search is O(n)
    and pop(i) shifts later elements left, so the whole delete is O(n)."""
    index = find_index(student_list, student_id)
    if index == -1:
        raise ValueError("Student ID '" + str(student_id).strip() + "' was not found.")
    return student_list.pop(index)


def show_statistics(student_list):
    """Return (total, average_cgpa, highest_cgpa, lowest_cgpa) using one traversal. O(n)."""
    total = len(student_list)
    if total == 0:
        return 0, 0.0, 0.0, 0.0
    running_sum = 0.0
    highest = lowest = student_list[0]["cgpa"]
    for s in student_list:
        running_sum += s["cgpa"]
        if s["cgpa"] > highest:
            highest = s["cgpa"]
        if s["cgpa"] < lowest:
            lowest = s["cgpa"]
    return total, running_sum / total, highest, lowest


def load_sample_data(student_list):
    """Add the five sample records that are not already present. Returns how many were added."""
    added = 0
    for s in SAMPLE_DATA:
        if find_index(student_list, s["student_id"]) == -1:
            student_list.append(dict(s))
            added += 1
    return added
