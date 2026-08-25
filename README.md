# HRIS Import Preview

Upload an HRIS CSV export and see, before anything is saved:
- how many rows were in the file, and how many were accepted
- validation errors, tied to the original row number
- root employees (no manager)
- managers and how many people report to them
- employees stuck in a reporting cycle (e.g. A reports to B, B reports to A)

## Files

```
app.py              # Flask routes: GET / (form), POST /analyze (results)
logic.py             # all the CSV reading + validation + hierarchy logic
templates/index.html # one page: the upload form and the results
tests/test_logic.py  # tests for logic.py
sample_hris.csv       # sample file to try the app with
```

`logic.py` doesn't import Flask at all - it just takes plain data in and
returns plain data out, which is why it's easy to test on its own.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 and upload `sample_hris.csv`.

## Run the tests

```bash
pytest -v
```

## How the tricky part works (cycle detection)

Every employee has at most one manager, so if you follow the chain of
managers starting from any employee, one of two things happens:
- you reach someone with no manager (a root) - no cycle
- you loop back to someone you already passed on this same walk - that's
  a cycle, and only the employees from that point onward are part of it

That's it - just following a chain and remembering what you've seen, so
it's fast even for a very large file.
