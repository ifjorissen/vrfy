import unittest 
import requests
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from django.utils.text import slugify

import sys
sys.path.append("../")
import vrfy.settings

class AdminTests(unittest.TestCase):
  
  def setUp(self):
    self.driver = webdriver.Firefox()

  #helper function that logs in to the admin side
  def _login(self):
    self.driver.find_element_by_id("id_username").send_keys("admin")
    pw = self.driver.find_element_by_id("id_password")
    pw.send_keys("password")
    pw.send_keys(Keys.RETURN)

  #helper function that fills out a form for a new problem set
  def _new_ps(self):
    name = "test_ps_" + str(random.randint(1,10000))
    self.driver.find_element_by_id("id_title").send_keys(name)
    self.driver.find_element_by_id("id_description").send_keys("This is a description")
    problems = Select(self.driver.find_element_by_id('id_problems'))
    problems.select_by_value("2")
    
    self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[1]/div/p/span[1]/a[1]").click()
    self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[1]/div/p/span[2]/a[1]").click()
    self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[2]/div/p/span[1]/a[1]").click()
    self.driver.find_element_by_xpath("/html/body/div[1]/div[3]/div/form/div/fieldset[3]/div[2]/div/p/span[2]/a[1]").click()

    self.driver.find_element_by_name("_save").click()

    return name

  def test_new_problem_set_opens_courselab(self):
    self.driver.get("http://localhost:8000/admin/course/problemset/add/")
    self._login()
    name = self._new_ps()
    
    url = vrfy.settings.TANGO_ADDRESS + "open/" + vrfy.settings.TANGO_KEY + "/" + slugify(name) + "/"
    response = requests.get(url)
    #if this command creats the courselab, then it wasn't created by the admin app
    self.assertNotEqual(response.json()["statusMsg"], "Created directory")

  def tearDown(self):
    self.driver.close()
  

if __name__ == "__main__":
    unittest.main()
