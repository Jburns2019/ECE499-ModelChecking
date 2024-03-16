import os
import sys
from pdoc import html

project_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
documentation_dir = os.path.join(project_dir, "docs")
if not os.path.isdir(documentation_dir):
    os.mkdir(documentation_dir)

files = os.listdir(project_dir)
for file_name in files:
    if '.py' in file_name:
        file_name = file_name.replace('.py', '')

        f = open(os.path.join(documentation_dir, file_name + ".html"), "w")
        f.write(html(file_name))
        f.close()