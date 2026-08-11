# Databricks Free Edition deployment guide

## Before you start

1. Confirm that your Free Edition account has fewer than three Apps and either no Lakebase project or a project you can reuse. Free Edition permits one Lakebase project and three Apps.
2. Create an empty public GitHub repository named `lakebase-support-ticketing`. Do not add a GitHub-generated README because this folder already contains one.
3. From this folder, publish the code:

```powershell
git init -b main
git add .
git commit -m "Build Lakebase support ticketing app"
git remote add origin https://github.com/<your-github-user>/lakebase-support-ticketing.git
git push -u origin main
```

4. Confirm the **Tests** GitHub Action passes. The workflow uses a disposable PostgreSQL 17 service and contains no production credentials.

## Create Lakebase

1. In the Databricks app switcher, select **Lakebase Postgres**.
2. Select **New project** and enter `support-ticketing`.
3. Keep PostgreSQL 17 and the default scale-to-zero setting, then create the project.
4. Wait for compute to become active. Keep the generated `production` branch and `databricks_postgres` database.

Do not create a native password, copy a connection string, create a service-principal role, or run the schema manually. The App resource and this project's startup migration do that safely.

## Create and deploy the app

1. Open the app switcher → **Databricks Apps** → **Create app** → **Create a custom app**.
2. Name it `lakebase-support-tickets`. App names cannot be changed after creation.
3. In **Configure Git**, enter the public GitHub repository URL, select GitHub, and set the Git reference to `main`. Leave source-code path empty and do not enable automatic deployment.
4. In **Configure** → **App resources**, choose **Add resource** → **Database**:
   - Lakebase Autoscaling project: `support-ticketing`
   - Branch: `production`
   - Database: `databricks_postgres`
   - Permission: **Can connect and create**
   - Resource key: `postgres`
5. Keep the default App compute option and click **Create app**.
6. From the App overview page choose **Deploy** → **From Git** → branch `main` → **Deploy**.
7. Wait for the status to become **Running**, open **Logs**, and verify no deployment error is shown. Then open the generated App URL.

On its first startup the application creates `support_app.tickets` and `support_app.ticket_messages`, then inserts the deterministic sample records. Later restarts and deployments preserve records and do not duplicate seeds.

## Update the deployed app

1. Commit and push the changes to `main`.
2. Open the existing Databricks App and click **Deploy** → **From Git** → branch `main` → **Deploy**.
3. Open the new deployment logs and smoke-test `/healthz` plus one ticket action.

## Workspace-folder fallback

If direct Git deployment is unavailable, install the Databricks CLI, authenticate, and sync this folder:

```powershell
databricks auth login
databricks sync . /Workspace/Users/<your-databricks-email>/lakebase-support-tickets
```

In the existing App use the arrow next to **Deploy**, select **Deploy using a different source**, select that workspace folder, and deploy. Keep the original `postgres` App resource bound to this same App.

## Inspect the database and capture evidence

Open Lakebase → `support-ticketing` → `production` → SQL Editor, then run:

```sql
SELECT
    t.ticket_id,
    t.title,
    t.status,
    t.priority,
    t.created_by,
    COUNT(m.message_id) AS message_count
FROM support_app.tickets AS t
LEFT JOIN support_app.ticket_messages AS m
    ON m.ticket_id = t.ticket_id
GROUP BY
    t.ticket_id,
    t.title,
    t.status,
    t.priority,
    t.created_by,
    t.created_at
ORDER BY t.created_at;
```

Take the screenshot with the Lakebase schema browser visible so both tables and the records are evident.
