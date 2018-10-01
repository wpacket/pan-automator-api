#!/usr/bin/env python

import urllib
import urllib2
import ssl
import argparse
import re
from jinja2 import Environment, FileSystemLoader
import yaml
import sys
import os


def api_request(url, values):

    data = urllib.urlencode(values)
    context = ssl._create_unverified_context()

    try:
        request = urllib2.Request(url, data)
        return urllib2.urlopen(request, context=context).read()

    except urllib2.URLError:
        print("\n\033[1;31;40m[Error] : Connecting to {url}. Check IP address.".format(url=url)+"\033[0m")
        return None


def keygen(username, password, ip):

  url="https://"+ip+"/api/?type=keygen&user="+username+"&password="+password
  context = ssl._create_unverified_context()
	
  try:
    request = urllib2.Request(url)
    response = urllib2.urlopen(request, context=context)
    data = response.read()
    key = re.search(r"(<key>)(.*)</key>",data)
    return key.group(2)
		
  except urllib2.URLError:
    print("\n\033[1;31;40m[Error] : Connecting to "+ip+" to get API KEY failed. Check URL/IP/Login/Password.\033[0m")
    return None
	
def parse_response_code(api_element,api_response):

  response = re.search(r"<msg>(.*)</msg></response>",api_response)
  response_string = response.group(1)
	
  if response_string != "command succeeded":
    print "\n\033[1;31;40m[Error] : Panorama was not able to execute the API request below. Verify your YAML configuration file\033[0m"
    print "Element :"+str(api_element),
    print "Reponse :"+str(response_string)+'\n',
    tmp_configuration(tmpfile,"delete")
    sys.exit(0)

def tmp_configuration(tmpfile,action):

  if action == "create":  
    try:
      filename = "./"+tmpfile
      file_ = open(filename, 'a+')
      file_.write(template.render(config))
      file_.close()
      print "\n\033[1;32;40m[SUCCESS]\033[0m : Creation of the temporary local configuration file"
    except IOError:
      print("ERROR   : when creating "+filename+" locally. Check the privileges of the user running the script")
      sys.exit(0)

  if action == "delete":
    if os.path.isfile("./"+tmpfile):
      os.remove("./"+tmpfile)
      print "\n\033[1;32;40m[SUCCESS]\033[0m : Removal of the temporary local configuration file\n"



if __name__ == '__main__':


  usage = 'pan-automator-api -pi <panorama_ip> -pl <panorama_api_login> -pp <panorama_api_password> -ym <yaml file>\n'


  panorama_api_login = ''
  panorama_api_password = ''
  panorama_ip	= ''
  yaml_file=''
  tmpfile = ".jinjatmp"
  
  parser = argparse.ArgumentParser(usage=usage)
  parser.add_argument('-pi', action='store',required=True, help='Panorama FQDN/IP')
  parser.add_argument('-pl', action='store',required=True, help='Panorama API Login')
  parser.add_argument('-pp', action='store',required=True, help='Panorama API Password')
  parser.add_argument('-ym', action='store',required=True, help='YAML file')
  results = parser.parse_args()

  panorama_ip	=  results.pi
  panorama_api_login =  results.pl
  panorama_api_password =  results.pp
  yaml_file =  results.ym
  
  url = "https://{ip}/api".format(ip=panorama_ip)
  api_key = keygen(panorama_api_login, panorama_api_password, panorama_ip)
  tmp_configuration(tmpfile,"delete") 

  try:

    config = yaml.load(open(yaml_file))
    env = Environment(loader = FileSystemLoader('./'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('panorama_DG.j2')
  except IOError:
    print"\n\033[1;31;40m[Error] : Make sure panorama_DG.j2 and "+yaml_file+" are reachable.\033[0m"
    sys.exit(0)
    
  tmp_configuration(tmpfile,"create")
  print "\n\033[1;32;40m[SUCCESS]\033[0m : Connecting to Panorama and pushing the configuration. The action should not exceed 1 min\n"

  with open(tmpfile) as f:
    for line in f:
      api_url,api_element = line.split(";")
      api_call = {'type': 'config', 'action': 'set', 'Key': api_key, 'xpath': api_url, 'element': api_element}
      response = api_request(url,api_call)
      parse_response_code(api_element,response)
      sys.stdout.write('.')
      sys.stdout.flush()
  
  print "\n\n\033[1;32;40m[SUCCESS]\033[0m : The template has been created on Panorama"
  print "\n\033[1;32;40m[SUCCESS]\033[0m : The stack has been created on Panorama"
  print "\n\033[1;32;40m[SUCCESS]\033[0m : The device group has been created on Panorama"
  
  tmp_configuration(tmpfile,"delete")
