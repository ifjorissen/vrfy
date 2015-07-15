"""
File for functions that interact with Tango
"""
from django.utils.text import slugify
from vrfy.settings import TANGO_ADDRESS, TANGO_KEY, TANGO_COURSELAB_DIR, MAKEFILE_NAME
import requests
import json

def _request(action, courselab, method, body=None, headers=None, outputfile=""):
  """
  function to be used by the other more specific functions to send data to Tango
  returns a requests response object (as opposed to a django response object)
  """
  url = TANGO_ADDRESS + action + "/" + TANGO_KEY + "/" + courselab + "/"
  if outputfile != "":
    url += outputfile + "/"
  
  r = requests.request(method, url, data=body, headers=headers)
  return r

def open(problem, problemset):
  """
  opens a new courselab given the name of the problem and problemset
  returns a requests response object
  """
  courselab = slugify(problemset) + "_" + slugify(problem)
  return _request("open", courselab, "GET")

def upload(problem, problemset, filename, file):
  """
  uploads a file to the courselab. all args are strings
  """
  courselab = slugify(problemset) + "_" + slugify(problem)
  header = {'Filename': filename}
  return _request("upload", courselab, "POST", body=file, headers=header)

def addJob(problem, problemset, files, jobName, output_file, image="autograding_image", timeout=100, max_kb=1000, callback_url=None):
  courselab = slugify(problemset) + "_" + slugify(problem)
  #add the makefile
  files.append({"localFile" : MAKEFILE_NAME, "destFile": "Makefile"})
  body = json.dumps({"image": image, "files": files, "jobName": jobName, "output_file": output_file, "timeout": timeout, "max_kb": max_kb})
  return _request("addJob", courselab, "POST", body=body)


