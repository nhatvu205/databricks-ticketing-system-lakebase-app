# Submission checklist

- [ ] The Databricks App is running and its URL is copied.
- [ ] The initial page shows three seeded tickets with multiple statuses.
- [ ] A new high-priority ticket named `Submission persistence check` was created.
- [ ] A distinctive message was added to that ticket.
- [ ] Its status was changed from `open` to `in_progress`.
- [ ] A browser refresh still shows the ticket, message, and new status.
- [ ] `/healthz` returns `{"status":"ok"}`.
- [ ] A wide app screenshot shows statistics, filters, the selected ticket, its message, and its status.
- [ ] A Lakebase screenshot shows `tickets`, `ticket_messages`, and the SQL query result with message counts.
- [ ] GitHub Actions **Tests** is green.
- [ ] `python scripts/package_submission.py` created `lakebase-support-ticketing-source.zip`.
- [ ] The ZIP and GitHub repository contain no passwords, tokens, API keys, `.env`, or copied connection strings.
- [ ] The reflection was personalized and is between three and five sentences.
