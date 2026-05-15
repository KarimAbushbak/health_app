# Publish this project to GitHub (run after: gh auth login)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$repo = "healthcare-analytics-dashboard"

gh repo create $repo --public --source=. --remote=origin --push --description "Streamlit healthcare analytics dashboard with synthetic data, KPIs, and data quality insights"

Write-Host "Done. Repo: https://github.com/$(gh api user -q .login)/$repo"
