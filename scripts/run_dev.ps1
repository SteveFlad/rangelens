param(
  [switch]$Mock = $true
)

python -m app.main $(if ($Mock) { '--mock' })
