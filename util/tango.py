"""
File for functions that interact with Tango
"""
from django.utils.text import slugify
from vrfy.settings import TANGO_ADDRESS, TANGO_KEY, TANGO_COURSELAB_DIR, MAKEFILE_NAME
import requests
import json
import shutil
import os

def _request(action, courselab, method, body=None, headers=None, outputFile=""):
  """
  function to be used by the other more specific functions to send data to Tango
  returns a requests response object (as opposed to a django response object)
  """
  url = TANGO_ADDRESS + action + "/" + TANGO_KEY + "/" + courselab + "/"
  if outputFile != "":
    url += outputFile + "/"
  
  r = requests.request(method, url, data=body, headers=headers)
  return r

def _get_courselab(problem, problemset):
  return slugify(problemset) + "_" + slugify(problem)

def open(problem, problemset):
  """
  opens a new courselab given the name of the problem and problemset
  returns a requests response object
  """
  courselab = _get_courselab(problem, problemset)
  return _request("open", courselab, "GET")

def upload(problem, problemset, filename, file):
  """
  uploads a file to the courselab. all args are strings
  """
  courselab = _get_courselab(problem, problemset)
  header = {'Filename': filename}
  return _request("upload", courselab, "POST", body=file, headers=header)

def addJob(problem, problemset, files, jobName, output_file, image="autograding_image", timeout=10, max_kb=1000, callback_url=None):
  courselab = _get_courselab(problem, problemset)
  #add the makefile
  files.append({"localFile" : MAKEFILE_NAME, "destFile": "Makefile"})
  body = json.dumps({"image": image, "files": files, "jobName": jobName, "output_file": output_file, "timeout": timeout, "max_kb": max_kb})
  return _request("addJob", courselab, "POST", body=body)

def poll(problem, problemset, outputFile):
  courselab = _get_courselab(problem, problemset)
  return _request("poll", courselab, "GET", outputFile=outputFile)

def delete(problem, problemset, filename=""):
  """
  deletes a courselab or file in a courselab
  """
  path = TANGO_COURSELAB_DIR + _get_courselab(problem, problemset)
  if filename == "":
    shutil.rmtree(path)
  else:
    path += "/" + filename
    os.remove(path)

