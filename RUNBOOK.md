# Dear Wishlist — Troubleshooting Runbook

## Incident: Wishlist Item Does Not Save

**Application:** Dear Wishlist  
**Technology:** Python, Flask, SQLite  
**Database:** wishlist.db

### 1. Observable Symptoms

A user submits a new wishlist item, but the item does not appear on the homepage. The application may display an error, or the terminal may show an unsuccessful request.

### 2. How to Confirm the Problem

1. Open the Dear Wishlist application.
2. Attempt to add a new wishlist item using valid information.
3. Check whether the item appears on the homepage.
4. Open the terminal and review the structured logs.
5. Find the request ID associated with the operation.
6. Check for the `add_item_started`, `add_item_success`, or `add_item_failed` events.
7. Review the HTTP response status and any database errors.

### 3. Possible Causes

- The SQLite database is unavailable.
- The `items` table is missing.
- The database is locked or cannot be written to.
- An error occurred while saving the wishlist item.

### 4. Troubleshooting Steps

**Step 1: Check the structured logs.**

Locate the request ID for the failed operation and review all related log entries.

**Step 2: Check the SQLite database.**

Verify that the `wishlist.db` file exists in the project directory.

**Step 3: Check the database table.**

Run the following command from the project directory:

```bash
python3 -c "import sqlite3; c=sqlite3.connect('wishlist.db'); print(c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name='items'\").fetchall()); c.close()"
```

The result should contain `items`.

**Step 4: Investigate the error.**

If the database is locked, check for another process using it. If a table is missing, preserve the database and investigate the schema before making changes.

**Step 5: Correct the confirmed issue.**

Resolve the identified database or application error. Restart the Flask server if necessary.

Do not delete or overwrite `wishlist.db`, because it may contain saved wishlist items.

### 5. Verify the Fix

1. Restart the application if needed.
2. Add a new test wishlist item.
3. Confirm that it appears on the homepage.
4. Refresh the page to verify that the item remains saved.
5. Confirm that the logs show `add_item_success`.
6. Run `python3 -m pytest -v` and confirm the tests pass.

### 6. Escalation

If the problem continues, record the error message, request ID, time of failure, and troubleshooting steps attempted. Provide this information to the application maintainer.

### Expected Result

The application should successfully save wishlist items in SQLite and generate structured logs showing the operation's progress.