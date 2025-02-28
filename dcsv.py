#!/usr/bin/env python
'''

Display CSV files from the command line

'''

import os
import csv
import sys
import platform

from optparse import OptionParser
try:
    from prettytable import PrettyTable
except ImportError:
    print 'Error: Please install prettytable "easy_install prettytable"'
    os._exit(-1)

if platform.system().lower() in ['linux', 'darwin']:
    INFO = "\033[1m\033[36m[*]\033[0m "
    WARN = "\033[1m\033[31m[!]\033[0m "
else:
    INFO = "[*] "
    WARN = "[!] "

def display_info(msg):
    sys.stdout.write(chr(27) + '[2K')
    sys.stdout.write('\r' + INFO + msg)
    sys.stdout.flush()

def parse_csv(file_path, verbose=False):
    table = None
    with open(file_path, 'rb') as csvfile:
        reader = csv.reader(csvfile,  dialect=csv.excel)
        for index, row in enumerate(reader):
            if index == 0:
                table = PrettyTable(row)
            elif 0 < len(row):
                table.add_row(row)
                if verbose: 
                    display_info("Parsed row: %d" % index)
    if verbose: 
        display_info("Parsed all rows successfully.\n")
        display_info("Rendering, please wait...\n")
    return table

def extract_csv(file_path, field_name, verbose=False):
    results = []
    with open(file_path, 'rb') as csvfile:
        reader = csv.reader(csvfile,  dialect=csv.excel)
        for index, row in enumerate(reader):
            if index == 0:
                try:
                    field_index = row.index(field_name)
                except ValueError:
                    print WARN + '%s is an invalid column name.' % field_name
                    os._exit(5)
            elif 0 < len(row):
                results.append(row[field_index])
    return results

def save_table(fpath, table, start=0, end=None, fields=None, html=False, verbose=False):
    if verbose: 
        display_info('Saving data to %s ...' % fpath)
    with open(fpath, 'w') as outfile:
        if fields is None: 
            fields = table.field_names
        else:
            fields = filter(lambda field: field in table.field_names, fields.split(","))
        if html:
            outfile.write("<html>\n")
            outfile.write(table.get_html_string(start=start, end=end, fields=fields))
            outfile.write("\n</html>\n")
        else:
            outfile.write(table.get_string(start=start, end=end, fields=fields) + '\n')
    if verbose: 
        display_info('Saving data to %s ... done!\n' % fpath)

def save_data(fpath, data, start=0, end=None, verbose=False):
    if verbose: 
        display_info('Saving data to %s ...' % fpath)
    if end is None:
        save = data[start:]
    else:
        save = data[start:end]
    with open(fpath, 'w') as outfile:
        for line in save:
            outfile.write('%s\n' % line)
    if verbose:
        display_info('Saving data to %s ... done!\n' % fpath)

if __name__ == '__main__':
    parser = OptionParser(usage="%prog <file.csv> [options]")
    parser.add_option(
        "-o", "--output", 
        dest="file", 
        help="Write output to a file", 
        default=None)
    parser.add_option(
        "-v", "--verbose", 
        action="store_true", 
        dest="verbose", 
        help="Enable verbose console output",
        default=False)
    parser.add_option(
        "-t", "--no-table", 
        action="store_false", 
        dest="console", 
        help="Do not display table in console",
        default=True)
    parser.add_option(
        "-f", "--filter", 
        dest="filter", 
        help="Only display specified columns; col1,col2",
        default=None)
    parser.add_option(
        "-c", "--columns",
        action="store_true",
        dest="header", 
        help="Display column header information only",
        default=False)
    parser.add_option(
        "-s", "--start",
        type="int",
        dest="start", 
        help="Display table starting at a given index",
        default=0)
    parser.add_option(
        "-e", "--end",
        type="int",
        dest="end", 
        help="Display table ending at a given index",
        default=None)
    parser.add_option(
        "-m", "--html",
        action="store_true",
        dest="html", 
        help="Write output file as HTML",
        default=False)
    parser.add_option(
        "-x", "--extract",
        dest="extract", 
        help="Pull a single column",
        default=None)
    (options, args) = parser.parse_args()
    if len(args) == 0:
        print WARN + 'Not enough arguments, see --help'
        os._exit(1)
    elif not os.path.exists(args[0]):
        print WARN + 'File does not exist:', os.path.abspath(args[0])
        os._exit(2)
    if options.verbose: 
        display_info('Reading %s, please wait...\n' % args[0])
    if options.extract is not None:
        extracted_data = extract_csv(args[0], options.extract, options.verbose)
    else:
        table = parse_csv(args[0], verbose=options.verbose)
    if options.console:
        if options.extract is not None:
            for index, line in enumerate(extracted_data):
                print "%d. %s" % (index + 1, line)
        else:
            if options.header:
                for index, name in enumerate(table.field_names): 
                    print '%d. %s' % (index +1, name)
            elif options.filter is not None:
                filter_names = []
                for name in options.filter.split(","):
                    if name not in table.field_names and options.verbose:
                        print WARN + "Invalid column name:", name
                    elif name in table.field_names:
                        filter_names.append(name)
                if options.end is not None:
                    print table.get_string(
                        start=options.start, 
                        end=options.end, 
                        fields=filter_names)
                else:
                    print table.get_string(
                        start=options.start, 
                        fields=filter_names)
            else:
                if options.end is not None: 
                    print table.get_string(
                        start=options.start, 
                        end=options.end)
                else: 
                    print table.get_string(start=options.start)
    # Save to file if requested
    if options.file is not None:
        if options.extract is not None:
            save_data(options.file, extracted_data, 
                start=options.start, 
                end=options.end, 
                verbose=options.verbose)
        else:
            save_table(options.file, table, 
                start=options.start, 
                end=options.end,
                fields=options.filter,
                html=options.html,
                verbose=options.verbose)
