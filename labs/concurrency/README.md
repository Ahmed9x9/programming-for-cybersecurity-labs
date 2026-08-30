# Concurrency

The thread exercise starts ten workers that report sleeping and waking. The ping exercise uses a
bounded thread pool and requires `--live` plus an explicit IP range. The perfect-number exercise can
run sequentially or with a process pool and reports elapsed time.

```bash
python -m labs.concurrency.solutions threads --count 10 --delay 5
python -m labs.concurrency.solutions perfect --limit 100000 --parallel
python -m labs.concurrency.solutions ping --start 192.0.2.1 --end 192.0.2.5 --live
```

Only ping systems you are authorized to test. Tests replace ping with a deterministic fake and use
small perfect-number limits.
