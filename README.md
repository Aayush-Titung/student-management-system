# Student Management System  web edition

A browser-based academic demonstration of Python lists, dictionaries, linear search, CRUD operations and CGPA statistics. `student_logic.py` is retained unchanged from the original project. The HTML/CSS/JavaScript client calls a Python WSGI service; it does not duplicate the data algorithms.

## Run locally

Install Python 3.10 or newer. Open a terminal in this folder and run:

```sh
python app.py
```

Open http://127.0.0.1:8000 in your browser. Use Load sample data to add the five fictional records. No package installation is needed for local use. Stop with Ctrl+C.

## Deploy on Render

1. Create a GitHub repository (private if desired) and upload the **contents** of this folder, keeping the `static` subfolder intact. Do not upload the ZIP itself or a containing folder. Do not publish the assignment report, personal details, or actual student records.
2. Visit https://dashboard.render.com/ and connect your GitHub account. Choose New > Web Service and select the repository.
3. Set runtime to Python 3, branch to main (or your repository's default), and leave Root Directory blank if files are at repository root.
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn --workers 1 --threads 4 --bind 0.0.0.0:$PORT app:application`
6. Select Free instance type if available. Under Advanced, health check path: `/health` (optional). Deploy.
7. Copy the HTTPS URL shown on the Render service dashboard. Open it in a private browser window to ensure it works without your account. The free instance can sleep after inactivity, so a first request can be slow.
8. Run the manual browser checks below; add actual screenshots to the report and insert the actual deployed URL before resubmitting. Submit the URL in the Canvas comment/website field as well as the updated ZIP if permitted.

Official documentation: https://render.com/docs/your-first-deploy and https://render.com/docs/web-services

## Automated tests

```sh
python test_student_logic.py
python test_web.py
```

Original logic: 14 checks. Web integration: 12 tests covering static files, HTTP actions, validation, statistics and separate sessions. `node --check static/script.js` optionally checks JS syntax if Node is installed. These are not a substitute for checking the deployed site in a browser.

## Manual browser verification (after hosting)

- Start a fresh private window; open the site and verify the empty state.
- Load sample data: total 5, average 3.56, highest 3.90, lowest 3.10. Load again; count stays 5.
- Add S106, Alex Morgan, Software Engineering, 3.80. Verify six rows and updated statistics.
- Try duplicate s106 and CGPA 4.5 for a new ID. Both should be rejected. Try an empty required field.
- Search S103, then S999. Verify one matching row and not-found message respectively; click View all.
- Edit S104; change major to Software Engineering and CGPA to 3.20; verify row changes. Student ID remains fixed.
- Edit S102; click Delete student; cancel once, then confirm. Verify the row is removed.
- Refresh the page and verify current session records remain. Open a new private session and verify the original session's records are not shared. Check a narrow mobile viewport.
- Capture screenshots of these results with the real website URL visible. Update the report and submit the actual link, not localhost or a GitHub source URL.

## Files

- `app.py`: WSGI web service and session management
- `student_logic.py`: unchanged Python list/dictionary algorithms
- `static/`: HTML, CSS, JavaScript web interface
- `test_student_logic.py`: original automated checks
- `test_web.py`: HTTP integration tests
- `requirements.txt`: Gunicorn deployment server only

## Limitations

Academic demo only; no database or authentication. Each browser has a temporary in-memory session, limited to 200 fictional records; sessions expire after one hour without API activity or may be evicted at the server session limit. A server restart or free-host sleep can reset records. Keep one Gunicorn worker so in-memory sessions remain consistent. No actual student records or personal data should be entered. No guarantee of uninterrupted free hosting. Public deployment and full interactive browser testing must be completed by the student.
