# Publish this project to GitHub (run after: gh auth login)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$repo = "health_app"
$remote = "https://github.com/KarimAbushbak/health_app.git"

git remote remove origin 2>$null
git remote add origin $remote
git branch -M main
git push -u origin main

Write-Host "Done. Repo: https://github.com/KarimAbushbak/$repo"
