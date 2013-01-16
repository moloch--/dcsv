#!/usr/bin/env python
'''

Display CSV files from the command line

'''

import os
import csv
import sys

from optparse import OptionParser
try:
    from prettytable import PrettyTable
except ImportError:
    print 'Error: Please install prettytable "easy_install prettytable"'
    os._exit(-1)

INFO = "\033[1m\033[36m[*]\033[0m "
WARN = "\033[1m\033[31m[!]\033[0m "

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

def extract_csv(field_name, file_path, verbose=False):
    results = []
    with open(file_path, 'rb') as csvfile:
        reader = csv.reader(csvfile,  dialect=csv.excel)
        for index, row in enumerate(reader):
            if index == 0:
                field_index = row.index(field_name)
                assert 0 <= field_index
            else:
                results.append(row[field_index])
    return results

def save_file(fpath, table_data, verbose=False):
    if verbose: 
        display_info('Saving data to %s ...' % fpath)
    with open(fpath, 'w') as outfile:
        outfile.write(table_data)
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
        "-x", "--extract",
        action="store_true",
        dest="extract", 
        help="Extract all values for a given field",
        default=False)
    (options, args) = parser.parse_args()
    if len(args) == 0:
        print WARN + 'Not enough arguments, see --help'
        os._exit(1)
    elif not os.path.exists(args[0]):
    	print WARN + 'File does not exist:', os.path.abspath(args[0])
    	os._exit(2)
    if options.verbose: 
        display_info('Reading %s, please wait...\n' % args[0])
    table = parse_csv(args[0], verbose=options.verbose)
    table_data = table.get_string(start=options.start)
    if options.console:
        if options.header:
            for name in table.field_names: print '\t%s' % name
        elif options.filter is not None:
            try:
                table_data = table.get_string(
                    start=options.start,
                    fields=options.filter.split(",")
                )
            except:
                print WARN + "Invalid filter argument, see --columns"
    print table_data
    if options.file is not None:
        save_file(options.file, table_data, options.verbose)
