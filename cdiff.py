import pandas as pd
from os import path
import pathlib
import re
import argparse
from datetime import datetime


outstr = ""
parser = argparse.ArgumentParser(
                    prog='cdiff',
                    description='Take a diff of an old and updated Cloudsploit report to look for changes')

parser.add_argument('file1', metavar="old_report", help="The older Cloudsploit report file, deduped in XLSX format.", type=pathlib.Path)
parser.add_argument('file2', metavar="new_report", help="The newer Cloudsploit report file, deduped in XLSX format.", type=pathlib.Path)
parser.add_argument('-o','--output', help="Output filename. Output is in Markdown format, so file should end with .md for maximum compatibility.", type=pathlib.Path)
parser.add_argument('--no-console', help="Skip output in stdout. Can only be used with --output.", action='store_true')
args = parser.parse_args()

if args.no_console and not args.output:
    print("[ERROR] The argument '--no-console' requires an output file with '--output'")
    exit(1)

def load_excel(file_path, sheet_name=0):
    return pd.read_excel(file_path, sheet_name=sheet_name)

def compare_titles(df1, df2, column_name="Title"):
    titles1 = set(df1[column_name])
    titles2 = set(df2[column_name])

    added_titles = sorted(titles2 - titles1)
    removed_titles = sorted(titles1 - titles2)

    differences = []

    if removed_titles:
        removed_titles_str = '\n'.join([f"{index + 1}. {removed_title}" for index, removed_title in enumerate(removed_titles)])
        differences.append(f"### Removed findings\n")
        differences.append(removed_titles_str)
    if added_titles:
        added_titles_str = '\n'.join([f"{index + 1}. {added_title}" for index, added_title in enumerate(added_titles)])
        differences.append(f"\n### Added findings\n")
        differences.append(added_titles_str)

    common_titles = titles1 & titles2

    return differences, common_titles

def compare_resources(df1, df2, titles, title_column="Title", resource_column="Resources and Regions"):
    differences = []

    for title in sorted(titles):
        resource1 = sorted(df1[df1[title_column] == title][resource_column].values)
        resource2 = sorted(df2[df2[title_column] == title][resource_column].values)

        if resource1[0] != resource2[0]:
            resources_regions_1 = set([r.strip() for r in resource1[0].split('\n\n') if r.strip()])
            resources_regions_2 = set([r.strip() for r in resource2[0].split('\n\n') if r.strip()])

            added_rrs = sorted(resources_regions_2 - resources_regions_1)
            removed_rrs = sorted(resources_regions_1 - resources_regions_2)

            

            if removed_rrs or added_rrs:
                differences.append(f"### {title}\n")
            if removed_rrs:
                removed_rrs_str = '\n'.join([f"{index + 1}. {removed_rr}" for index, removed_rr in enumerate(removed_rrs)])
                differences.append(f"#### Removed\n{removed_rrs_str}\n")
            if added_rrs:
                added_rrs_str = '\n'.join([f"{index + 1}. {added_rr}" for index, added_rr in enumerate(added_rrs)])
                differences.append(f"#### Added\n{added_rrs_str}\n")

    return differences

def compare_excel_files(file1, file2, title_column="Title", resource_column="Resources and Regions"):
    df1 = load_excel(file1)
    df2 = load_excel(file2)

    # Compare the titles first
    title_differences, common_titles = compare_titles(df1, df2, title_column)

    # Compare the resources for common titles
    resource_differences = compare_resources(df1, df2, common_titles, title_column, resource_column)

    return title_differences, resource_differences

def output(msg="", end=False):
    global outstr

    if args.output:
        if end:
            try:
                with open(args.output, "w") as f:
                    f.write(outstr)
            except:
                print(f"Cannot write to file {args.output}")
        else:
            outstr += msg

    if args.no_console:
        return
    
    print(msg, end='')

def confirm_files(file1, file2):
    modtime_file1 = path.getmtime(file1)
    modtime_file2 = path.getmtime(file2)
    choice = ""
    if modtime_file1 > modtime_file2:
        while not re.match('[1-3]',choice):
            print("[WARNING] Second file should be newer.")
            print("1. I know. Continue.")
            print("2. Swap the order")
            print("3. Exit")
            choice = input()
        
        if choice == "2":
            file1_tmp = file1
            file1 = file2
            file2 = file1_tmp
        elif choice == "3":
            exit(0)

    return file1, file2

def file_mod_date(filename):
    mod_time = path.getmtime(filename)
    mod_datetime = datetime.fromtimestamp(mod_time)
    return mod_datetime.strftime('%Y-%m-%d')

def main():
    file1 = args.file1
    file2 = args.file2

    file1, file2 = confirm_files(file1, file2)

    title_differences, resource_differences = compare_excel_files(file1, file2)
    
    output("# Cloudsploit Report Comparison\n")

    i=1
    for file in [file1,file2]:
        output(f"{i}. {path.basename(file)} - {file_mod_date(file)}\n")
        i += 1

    output("\n## Title Differences:\n")
    for difference in title_differences:
        output(difference)

    output("\n\n## Resource Differences:\n")
    for difference in resource_differences:
        output(difference)

    output(end=True)

    return 0


if __name__ == "__main__":
    main()