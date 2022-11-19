import sys
import os

print("SYSTEM PATH: " + str(sys.path))
print()

print("RUNNING UNIT TESTS")
os.system('python3 -m unittest')
