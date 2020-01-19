import sys
import subprocess
import re
from os import listdir
from os.path import isfile, join

class colors:
    HEADER = '\033[95m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'

    ENDC = '\033[0m'

class icons:
    PASS  = colors.GREEN + 'Y' + colors.ENDC
    FAIL  = colors.RED + 'N' + colors.ENDC
    MAYBE = colors.YELLOW + '?' + colors.ENDC

def err(message):
    print colors.BOLD + colors.RED + "ERROR" + colors.ENDC + ": " + message
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
    summary = ""
    first_line_has_multiple_tokens = False

    bold("\nRunning samples...")
    for sample in sorted(sample_files):
        first_line = open("tests/{}.in".format(sample), 'r').read().split("\n")[0]
        if (len(first_line.strip().split(" ")) > 1):
            first_line_has_multiple_tokens = True

        if run("./{} < tests/{}.in > tests/{}.my".format(fname, sample, sample)):
            err("Run-time error on " + sample)

        print "\nExpected output on {}:".format(sample)
        has_output = True
        try:
            out = open("tests/{}.out".format(sample), 'r').read()
            print out
        except IOError:
            print "File \'tests/{}.out\' not found\n".format(sample)
            has_output = False

        my = open("tests/{}.my".format(sample), 'r').read()
        print "Your output on {}:".format(sample)
        print my

        if not has_output:
            warn(sample + " failed (missing \'tests/{}.out\')".format(sample))
            failed.append(sample)
            summary += icons.MAYBE
            continue

        proc = subprocess.Popen("diff tests/{}.out tests/{}.my".format(sample, sample),\
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o,e = proc.communicate()

        if o.decode('ascii') == "":
            bold(sample + " passed")
            summary += icons.PASS
        else:
            proc = subprocess.Popen("diff -b tests/{}.out tests/{}.my".format(sample, sample),\
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            o,e = proc.communicate()
            if o.decode('ascii') == "":
                bold(sample + " passed (ignored whitespace)")
                summary += icons.PASS
            else:
                my_output = open("tests/{}.my".format(sample)).readlines()
                my_tokens = [token for line in my_output for token in line.split()]

                exp_output = open("tests/{}.out".format(sample)).readlines()
                exp_tokens = [token for line in exp_output for token in line.split()]

                match = True
                if len(my_output) != len(exp_output):
                    match = False
                else:
                    for i in xrange(0, len(my_output)):
                        if my_output[i] == exp_output[i]:
                            continue
                        try:
                            my_val  = float( my_output[i])
                            exp_val = float(exp_output[i])
                            if abs(my_val - exp_val) / max(1, abs(exp_val)) > 1e-9:
                                raise ValueError
                        except ValueError:
                            match = False
                            break

                if match:
                    bold(sample + " passed (ignored whitespace, float tolerance 1e-9)")
                    summary += icons.PASS
                else:
                    warn(sample + " failed")
                    failed.append(sample)
                    summary += icons.FAIL

    if failed:
        print
        print summary + ": FAILED samples " + str(failed)
    elif not sample_files:
        print
        warn("No sample inputs found in tests/")
    else:
        print
        print summary + colors.BOLD + ": ALL SAMPLES OK!" + colors.ENDC

    if first_line_has_multiple_tokens:
        warn("First line of input has multiple tokens. Check their order carefully.")

if __name__ == "__main__": main()
