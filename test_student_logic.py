"""Automated checks for the 9 required test cases (run: python test_student_logic.py)."""
import student_logic as sl

results = []

def check(name, condition):
    results.append((name, condition))
    print(("PASS  " if condition else "FAIL  ") + name)

def raises(func, *args):
    try:
        func(*args)
    except ValueError:
        return True
    return False

data = []

# TC8 - display with empty list
check("TC8  Display on empty list shows a message",
      sl.display_students(data) == ["No student records found."])

# TC1 - add valid
sl.add_student(data, "S101", "Amina Rahman", "Computer Science", "3.75")
check("TC1  Add a valid student", len(data) == 1 and data[0]["cgpa"] == 3.75)

# TC2 - duplicate ID
check("TC2  Duplicate Student ID rejected", raises(sl.add_student, data, "S101", "X", "Y", "3.0") and len(data) == 1)

# TC3 - CGPA > 4.00 (plus other invalid input)
check("TC3  CGPA 4.5 rejected", raises(sl.add_student, data, "S999", "X", "Y", "4.5"))
check("TC3b CGPA -1 / 'abc' / '' / 'nan' rejected",
      all(raises(sl.add_student, data, "S999", "X", "Y", v) for v in ("-1", "abc", "", "nan")))
check("TC3c Empty ID / name / major rejected",
      raises(sl.add_student, data, " ", "X", "Y", "3") and raises(sl.add_student, data, "S9", "", "Y", "3")
      and raises(sl.add_student, data, "S9", "X", "  ", "3"))

# load the rest of the sample data -> 5 records
sl.load_sample_data(data)
check("     Five sample records present", len(data) == 5)

# TC4 / TC5 - search
r = sl.search_student(data, "S103")
check("TC4  Search existing ID returns the right record", r is not None and r["name"] == "Maria Lopez")
check("TC5  Search missing ID returns None (not found)", sl.search_student(data, "S999") is None)

# TC6 - update
sl.update_student(data, "S104", major="Software Engineering", cgpa="3.20")
r = sl.search_student(data, "S104")
check("TC6  Update changes selected fields only",
      r["major"] == "Software Engineering" and r["cgpa"] == 3.2 and r["name"] == "John Carter")
before = dict(r)
check("TC6b Invalid update leaves record unchanged",
      raises(sl.update_student, data, "S104", "New Name", None, "9") and sl.search_student(data, "S104") == before)

# TC9 - average CGPA (3.75 + 3.40 + 3.90 + 3.20 + 3.65) / 5 = 3.58
total, avg, hi, lo = sl.show_statistics(data)
check("TC9  Average CGPA is correct (3.58)", total == 5 and abs(avg - 3.58) < 1e-9 and hi == 3.9 and lo == 3.2)

# TC7 - delete
sl.delete_student(data, "S102")
check("TC7  Delete removes the record", sl.search_student(data, "S102") is None and len(data) == 4)
check("TC7b Delete of missing ID rejected", raises(sl.delete_student, data, "S102"))

print()
print("%d of %d checks passed" % (sum(1 for _, ok in results if ok), len(results)))
raise SystemExit(0 if all(ok for _, ok in results) else 1)
