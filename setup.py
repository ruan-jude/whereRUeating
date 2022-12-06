import sys
import os

print("SYSTEM PATH 0: " + str(sys.path[0]))
print()

test_dir = sys.path[0] + "/test"

test_constants_path = os.path.join(test_dir, 'constants.py')
f = open(test_constants_path, "w")
f.write("PATH_TO_PROJECT = \"" + sys.path[0] + "\"")
f.write("\n")
f.write("PATH_TO_MODULES = \"" + sys.path[0] + "/server" + "\"")
