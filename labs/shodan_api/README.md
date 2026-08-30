# Shodan API

This topic retrieves host geolocation and indexed ports and performs the original anonymous-FTP
search. Calls require `--live`; the key is read only from `SHODAN_API_KEY`.

PowerShell:

```powershell
$env:SHODAN_API_KEY = "your-new-key"
python -m labs.shodan_api.solutions host --target scanme.nmap.org --live
python -m labs.shodan_api.solutions search --query "port:21 Anonymous user logged in" --live
```

Bash:

```bash
export SHODAN_API_KEY="your-new-key"
python -m labs.shodan_api.solutions host --target scanme.nmap.org --live
```

Some free API keys cannot use search filters and may receive `403 Forbidden`. This is reported as an
account-plan limitation rather than a code failure. Never place a key in source code or screenshots.
