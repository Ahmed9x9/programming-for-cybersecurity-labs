# Modules, files, and exceptions

This topic implements the Euclidean algorithm as an importable package, adds two lists with
`map`/`lambda`, and performs the odd/even file exercises without hard-coded Desktop paths.

```bash
python -m labs.modules_files_and_exceptions.solutions --output-dir generated_files
python -m labs.modules_files_and_exceptions.gcd.cli 252 105
```

The generated directory is ignored by Git. Functions accept `pathlib.Path` values and use context
managers so files are closed even when errors occur.
