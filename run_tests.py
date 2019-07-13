import sys
import subprocess
import re
from os import listdir
from os.path import isfile, join

class colors:
    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def err(message):
    print colors.BOLD + colors.FAIL + "ERROR" + colors.ENDC + ": " + message
    exit(1)

def warn(message):
    print colors.BOLD + colors.HEADER + "WARN" + colors.ENDC + ": " + message

def bold(message):
    print colors.BOLD + message + colors.ENDC

def run(cmd):
    return subprocess.call(['/bin/bash', '-i', '-c', cmd])

def main():
    if len(sys.argv) < 2:
        err("Program expected as argument")

    fname = sys.argv[1]
    if fname[-4:] == ".cpp":
        fname = fname[:-4]

    bold("Compiling " + fname + " ...")
    if run("build " + fname):
        err("Compilation failed")
    if run("build-g " + fname + " >/dev/null 2>&1"):
        err("Compilation failed")

    sample_input = re.compile("sample.*[.]in")
    sample_files = [f[:-3] for f in listdir("tests/") if sample_input.match(f)]
    failed = []

    bold("\nRunning samples...")
    for sample in sorted(sample_files):
        if run("./{} < tests/{}.in > tests/{}.my".format(fname, sample, sample)):
            err("Run-time error on " + sample)

        my_file = open("tests/{}.my".format(sample), 'r')
        out_file = open("tests/{}.out".format(sample), 'r')
        my, out = my_file.read(), out_file.read()
        my_file.close(), out_file.close()

        print "\nExpected output on {}:".format(sample)
        print out
        print "Your output on {}:".format(sample)
        print my

        if my == out:
            bold(sample + " passed")
        elif [x.strip() for x in my] == [x.strip() for x in out]:
            bold(sample + " passed (with leading or trailing whitespace)")
        else:
            warn(sample + " failed")
            failed.append(sample)

    if failed:
        print
        err("Failed samples " + str(failed))
    elif not sample_files:
        print
        err("No sample inputs found in tests/")
    else:
        print
        bold("ALL SAMPLES OK!")

if __name__ == "__main__": main()