# CDiff - The Cloudspoit Report Diffing Tool

## Installation
1. `git clone https://github.com/FWDSEC/cloudsploit-differ.git`
2. `cd cloudsploit-differ`
3. `python3 -m pip install .`

## Usage
1. Dedupe the Cloudsploit reports with [The Cloudsploit Super De-duper](https://github.com/FWDSEC/cloudsploit-deduper/)
2. `python3 cdiff.py /path/to/old-cloudsploit-report.xlsx /path/to/new-cloudsploit-report.xlsx`

### Outputs to Markdown format.

## Understand the results

**Removed findings** are titles which exist on the older report but not on the newer one. Presumably this means the issue was fixed, or the resources were deleted.

**Added findings** are Titles found on the newer report which did not exist on the older one. 

**Removed resources** appear when the Title exists in both the new and old report but resources that were in the old report no longer appear. Presumably because the issue was fixed for those resources, or those resources were deleted.

**Added resources** appear when the Title exists in both the new and old report but new resources appear under said Title.

```
usage: cdiff [-h] [-o OUTPUT] [--no-console] old_report new_report

Take a diff of an old and updated Cloudsploit report to look for changes

positional arguments:
  old_report            The older Cloudsploit report file, deduped in XLSX format.
  new_report            The newer Cloudsploit report file, deduped in XLSX format.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output filename. Output is in Markdown format, so file should end with .md for maximum compatibility.
  --no-console          Skip output in stdout. Can only be used with --output.
  ```