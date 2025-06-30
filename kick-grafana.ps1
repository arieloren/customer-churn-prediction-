<#  load-grafana.ps1  —  generates continuous traffic for Grafana/Prom  #>

param(
    [int]    $Minutes   = 10,                              # total run time
    [string] $ApiUrl    = "http://localhost:9999/predict",
    [int]    $RpmGood   = 60,                              # good reqs / min
    [int]    $RpmBad    = 6,                               # bad  reqs / min
    [int]    $BatchEach = 2                                # run batch every N minutes
)

Write-Host "⌛ Running for $Minutes minute(s)…`n"

$endAt = (Get-Date).AddMinutes($Minutes)
$nextBatch = Get-Date

while ((Get-Date) -lt $endAt) {

    # ── GOOD requests (success) ───────────────────────────
    1..$RpmGood | ForEach-Object {
        $body = @{
            customerID   = "PS-$([guid]::NewGuid().Guid.Substring(0,8))"
            tenure       = Get-Random -Minimum 1  -Maximum 72
            TotalCharges = [math]::Round((Get-Random -Minimum 50 -Maximum 3000), 2)
            Contract     = ('Month-to-month','One year','Two year' | Get-Random)
            PhoneService = ('Yes','No' | Get-Random)
        } | ConvertTo-Json
        try {
            Invoke-RestMethod -Uri $ApiUrl -Method Post -Body $body `
                              -ContentType 'application/json' | Out-Null
        } catch { }
    }

    # ── BAD requests (schema fail → 400) ──────────────────
    1..$RpmBad | ForEach-Object {
        try {
            Invoke-RestMethod -Uri $ApiUrl -Method Post `
                              -Body '{"customerID":"oops"}' `
                              -ContentType 'application/json'
        } catch { }      # swallow the expected error
    }

    # ── Batch job every $BatchEach minutes ────────────────
    if ((Get-Date) -ge $nextBatch) {
        Write-Host "🚀  Starting batch-runner ($(Get-Date -f HH:mm:ss))"
        docker compose run --rm batch-runner | Out-Null
        $nextBatch = (Get-Date).AddMinutes($BatchEach)
    }

    Start-Sleep -Seconds 60
}

Write-Host "`n✔  Finished.  Reload Grafana – all tiles should be populated."
