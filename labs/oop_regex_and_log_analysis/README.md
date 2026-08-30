# OOP, regex, and log analysis

This topic uses polymorphic parser classes to count a selected IP and list requested paths from an
Apache combined log. It also searches an exact event timestamp, validates email addresses, and
implements a `Person` factory that calculates age.

```bash
python -m labs.oop_regex_and_log_analysis.solutions \
  --log labs/oop_regex_and_log_analysis/data/sample_apache_access.log \
  --emails labs/oop_regex_and_log_analysis/data/sample_emails.txt
```

The included data is synthetic and uses IANA documentation networks and `.test` domains.
