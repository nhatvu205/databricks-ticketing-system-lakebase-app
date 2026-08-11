# Troubleshooting

## App deployment crashes before the page opens

- Confirm the App has a Lakebase **Database** resource with key `postgres`.
- Confirm the selected project, `production` branch, and `databricks_postgres` database still exist.
- Open the App **Logs** tab. Do not paste its environment values into source control.
- The first request after scale-to-zero can take a short time. Refresh once after waiting for the App status to return to **Running**.

## `Lakebase application resource is not configured`

The app was deployed without the resource binding or the resource key is not `postgres`. Add or correct the resource in App settings, then redeploy.

## Database unavailable page

Lakebase may be waking after scale-to-zero or the App resource authorization did not complete. Wait briefly, retry, then check that the App resource permission is **Can connect and create**.

## Git deployment cannot read the repository

The documented path uses a public repository. Recheck the exact HTTPS repository URL and `main` branch. A private repository requires a Git credential for the App service principal.

## App URL does not open for another person

Databricks Apps require Databricks account access. The assignment submission should include the URL and screenshots; do not try to bypass the sign-in boundary with public credentials.

## App stopped after working earlier

Free Edition automatically stops Apps after 24 hours. Open the App overview page and start it again before presenting or taking final screenshots.
