#! /usr/bin/env python3

import subprocess
import sys
import os
import soundcloud
import io

def main():

  modules = arg_parse()
  modules = get_pip_modules(modules)
  write_requirements(modules)
  print("'requirements.txt' file has been written.")

def write_requirements(modules):
  """
  Write modules in the requirements.txt file used by pip.
  ---
  args:   A dict of used modules and their versions.
  return: None.
  io:     Write the file requirements.txt
  ---
  """

  fi = open('requirements.txt', 'w+')
  for item in modules.items():
    fi.write("%s>=%s\n" % (item[0], item[1]))
  fi.close()

def get_pip_modules(modules):
  """
  Get pip module install, by default use pip3.
  ---
  args:   Dict of used modules in the .py file.
  return: A dict with installed modules as keys, and their version as value.
  ---
  """

  mpipe = subprocess.Popen("pip3 list",
                           shell=True,
                           stdout=subprocess.PIPE)
  try:
    mout, _ = mpipe.communicate()
  except:
    return None

  lines = io.StringIO(mout.decode('utf-8')).readlines()
  for line in lines:
    if line.split(' ')[0] in modules:
      modules[line.split(' ')[0]] = line.split(' ')[1]

  modules = { k : v.lstrip('(').rstrip(')\n') for k, v in modules.items() if v != '' }

  return modules

def arg_parse():
  """
  Parse argument, and read all files whose path name end with '.py'.
  ---
  args:   None.
  return: A dictionnary of module, key is module name, value is empty string.
  ---
  """

  modules = {}
  for i in range(1, len(sys.argv)):
    name = sys.argv[i]
    if os.path.isfile(name) and name.endswith('.py'):
      tmp, bo = open_file(name)
      if bo:
        modules.update(tmp)
    elif os.path.isdir(name):
      modules = nested_folder(modules, name)
  return modules

def nested_folder(modules, folder):
  """
  Open folder recursively and search for python files.
  ---
  args:   Dict of modules and folder path.
  return: Updated dict.
  ---
  """

  for name in os.listdir(folder):
    name = os.path.join(folder, name)
    if os.path.isfile(name) and name.endswith('.py'):
      tmp, bo = open_file(name)
      if bo:
        modules.update(tmp)
    elif os.path.isdir(name):
      modules = nested_folder(modules, name)
  return modules

def open_file(name):
  """
  Open python file.
  ---
  args:   Path name of python file.
  return: A tuple of module dict (see above) and a boolean set to False if
          an error happened.
  ---
  """

  try:
    fi = open(name, 'r')
  except:
    print("%s could not be opened." % name);
    return None, False

  modules = read_file(fi)
  fi.close()
  return modules, True

def read_file(fi):
  """
  Read python file, try to detect modules names that have been imported.
  ---
  args:   A python object corresponding to an opened python file.
  return: A dict of found modules, value (their version number) is set to empty
          string by default.
  ---
  """

  modules = {}
  lines = fi.readlines()
  for line in lines:
    if line.find('import ') != -1 and line.find('(') == -1 and len(line.split(' ')) > 1:
      modules.update({line.split(' ')[1].rstrip(): ''})
  return modules

if __name__ == '__main__':
  main()
