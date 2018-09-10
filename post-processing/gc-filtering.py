#!/usr/bin/python

import sys
import csv

'''
Filters the context-switches and the CPU csv files, by eliminating the values obtained while GC collection was active

The output are two files called filtered-cs.csv and filtered-cpu.csv, containing filtered context-switches and CPU measurements values respectevely

Usage: ./path/to/gc-filtering.py path/to/context-switches.csv path/to/cpu.csv path/to/gc.csv

Parameters:
-> path/to/context-switches.csv: the csv file containing context-switches data to be filtered
-> path/to/cpu.csv: the csv file containing CPU data to be filtered
-> path/to/gc.csv: the csv file containing the GC collection data on which the filtering of context-switches and CPU data is based.
Note: files 'path/to/context-switches.csv', 'path/to/cpu.csv', and 'path/to/gc.csv' should be produced by the same tgp analysis.
'''

#The file containing context-switches measurements
cs_file = sys.argv[1]
#The file containing CPU measurements
cpu_file = sys.argv[2]
#The file containing garbage collection's activity records
gc_file = sys.argv[3]

#The array containing context-switches data before filtering
cs_data_array_bf = []
#The array containing context-switches data after filtering
cs_data_array = []

#The array containing CPU data before filtering
cpu_data_array_bf = []
#The array containing CPU data before filtering
cpu_data_array = []

#The array containing garbage collection data
gc_data_array = []

'''
A class containing context-switches data from the csv file
'''
class CSData:
    def __init__(self, timestamp, context_switches):
        self.timestamp = timestamp
        self.context_switches = context_switches

'''
A class containing CPU data from the csv file
'''
class CPUData:
    def __init__(self, timestamp, user, system):
        self.timestamp = timestamp
        self.user = user
        self.system = system

'''
A class containing GC data from the csv file
'''
class GCData:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time

'''
Checks whether the input string contains letters
string: the input string to perform the check on
Returns true if the string contains letters, false otherwise
'''
def contains_letters(string):
    for s in string:
        if s.isalpha():
            return True
    return False

'''
Reads the input csv file, and sets up the input data structure.
Depending on the data type, a new instance of CSData, CPUData, or GCData will be created and added to the target array
input_csv_file: the csv file to read
target_array: the array where to write the content of the csv file
data_type: the data which will be read
file_delimiter: the delimiter used by the file
'''
def read_csv(input_csv_file, target_array, data_type, file_delimiter):
    csv_line_counter = 0
    with open(input_csv_file) as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=file_delimiter)
        old_gc = 0
        gc_counter = 0
        for row in csv_reader:
            #Reads and writes context-switches data
            if data_type == "CS" and csv_line_counter > 1:
                if row[0][0] != "-" and row[1][0] != "-" and contains_letters(row[0]) == False and contains_letters(row[1]) == False:
                    new_cs = CSData(float(row[0]), float(row[1]))
                    cs_data_array_bf.append(new_cs)
            #Reads and writes CPU data                  
            elif data_type == "CPU" and csv_line_counter != 0:
                if len(row[0]) > 0 and len(row[1]) > 0 and len(row[2]) > 0 and row[0][0] != "-" and row[1][0] != "-" and row[2][0] != "-" and contains_letters(row[0]) == False and contains_letters(row[1]) == False and contains_letters(row[2]) == False:
                    new_cpu = CPUData(long(row[0]), float(row[1]), float(row[2]))
                    cpu_data_array_bf.append(new_cpu)
            #Reads and writes GC data
            elif data_type == "GC":
                if gc_counter == 1:
                    if old_gc[0] != "-" and row[1][0] != "-" and contains_letters(old_gc) == False and contains_letters(row[1]) == False:
                        new_gc = GCData(long(old_gc), long(row[1]))
                        gc_data_array.append(new_gc)
                else:
                    old_gc = row[1]
                gc_counter = (gc_counter + 1) % 2
            csv_line_counter = csv_line_counter + 1

'''
Filters the context-switches array and writes the valid context-switches data into the filtered array.
To determine whether a context-switch is valid, said context-switch timestamp is checked against GC start and end timestamps: if the timestamp does not fall in any GC time interval, then the
context-switch is valid
'''
def filter_cs():
    for cs_data in cs_data_array_bf:
        found = False
        for gc_data in gc_data_array:
            if cs_data.timestamp >= gc_data.start_time and cs_data.timestamp <= gc_data.end_time:
                found = True
                break
        if found == False:
            cs_data_array.append(cs_data)

'''
Filters the CPU array and writes the valid CPU data into the filtered array.
To determine whether a CPU measurement is valid, said CPU timestamp is checked against GC start and end timestamps: if the timestamp does not fall in any GC time interval, then the
CPU measurement is valid
'''
def filter_cpu():
    for cpu_data in cpu_data_array_bf:
        found = False
        for gc_data in gc_data_array:
            if cpu_data.timestamp >= gc_data.start_time and cpu_data.timestamp <= gc_data.end_time:
                found = True
                break
        if found == False: 
            cpu_data_array.append(cpu_data)

'''
Writes the filtered context-switches array into a new csv file called filtered-cs.csv
'''
def write_cs_csv():
    with open ('filtered-cs.csv', 'w') as csvfile:
        fieldnames = ['Timestamp (ns)', 'Context Switches']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cs_data in cs_data_array:
            writer.writerow({'Timestamp (ns)': cs_data.timestamp, 'Context Switches': cs_data.context_switches})

'''
Writes the filtered CPU array into a new csv file called filtered-cpu.csv
'''
def write_cpu_csv():
    with open ('filtered-cpu.csv', 'w') as csvfile:
        fieldnames = ['Timestamp (ns)', 'CPU utilization (user)', 'CPU utilization (system)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for cpu_data in cpu_data_array:
            writer.writerow({'Timestamp (ns)': cpu_data.timestamp, 'CPU utilization (user)': cpu_data.user, 'CPU utilization (system)': cpu_data.system})   
            
read_csv(cs_file, cs_data_array, "CS", ',')
read_csv(cpu_file, cpu_data_array, "CPU", ',')
read_csv(gc_file, gc_data_array, "GC", ',')

print("")
print("Number of valid context-switches: %s" % str(len(cs_data_array_bf)))
print("Number of valid CPU samplings: %s" % str(len(cpu_data_array_bf)))


filter_cs()

filter_cpu()

print("")
print("Number of valid context-switches after filtering: %s" % str(len(cs_data_array)))
print("Number of valid CPU sampling after filtering: %s" % str(len(cpu_data_array)))
print("")

write_cs_csv()

write_cpu_csv()