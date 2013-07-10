#!/usr/bin/env python2
# encoding: utf-8
"""
# Reliance Login Script for Python 2.x v1.0
# 
# Copyright (c) 2009 Kunal Dua, http://www.kunaldua.com/blog/?p=330
# Copyright (c) 2012 Anoop John, http://www.zyxware.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
"""
 
import urllib2
import urllib
import cookielib
import time
import re
import sys
import getpass
import argparse

# Default value definitions
username = 'username'
password = 'password'
internet_on_test_url='http://google.com'
internet_off_test_string='reliance'
# Constant definitions
reliance_start_portal_url="http://reliancebroadband.co.in/reliance/startportal_isg.do"
reliance_login_url='http://reliancebroadband.co.in/reliance/login.do'
reliance_logout_url='http://reliancebroadband.co.in/reliance/logout.do'
user_agent_string='Mozilla/5.0 (Windows NT 6.1; U; ru; rv:5.0.1.6) Gecko/20110501 Firefox/5.0.1 Firefox/5.0.1'

'''You don't normally have to edit anything below this line'''
debug = False
check_interval = 600

def parse_args():
  parser = argparse.ArgumentParser(description='Reliance AutoLogin')
  parser.add_argument('-u', '--user', dest='username', help='Reliance username. Will be prompted if not provided', required=False)
  parser.add_argument('-p', '--pass', dest='password', help='Reliance password. Will be prompted if not provided', required=False)
  parser.add_argument('--login', dest='login', action='store_true', help='Login without keep-alive', required=False)
  parser.add_argument('--logout', dest='logout', action='store_true', help='Logout', required=False)
  parser.add_argument('--no-keepalive', dest='nokeepalive', action='store_true', help='No Keepalive', required=False)
  parser.add_argument('--internet-test-url', dest='internet_on_test_url', help='Internet test URL. Default: http://google.com', required=False)
  parser.add_argument('--internet-off-test-string', dest='internet_off_test_string', help='If this string is found in the test URL\'s reply, we know that internet is not connected. Default: \'reliance\'', required=False)
  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Enable verbose log printing', required=False)
  args = parser.parse_args()
  print "Command line arguments =",args
  return args

def get_url(url, data=None, timeout=60, opener=None):
  '''get_url accepts a URL string and return the server response code, response headers, and contents of the file'''
  '''ref: http://pythonfilter.com/blog/changing-or-spoofing-your-user-agent-python.html'''
  if debug: print "get_url:",url,"data:",data,"opener:",opener
  req_headers = {
    'User-Agent': user_agent_string
  }
  request = urllib2.Request(url, headers=req_headers)
  if not opener:
    jar = cookielib.FileCookieJar("cookies")
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
  response = opener.open(request, data)
  code = response.code
  headers = response.headers
  html = response.read()
  return code, headers, html, opener

def is_internet_on(test_url, test_string):
  '''test if the machine is connected to the internet'''
  if debug: print "Checking if internet is connected"
  try:
    code, headers, html, opener = get_url(test_url, timeout=10)
    if debug: print html
    if re.search(test_string, html):
      return False
    else:
      return True
  except Exception as e: 
    if debug: print "Error"
    print 'Error checking internet connection :', e
    print 'Assuming internet connection to be off'
    return False
  return False

def internet_connect(username, password, portal_url, login_url):
  '''try to connect to the internet'''
  if debug: print "Connecting to internet"
  try:
    code, headers, html, cur_opener = get_url(portal_url, timeout=10)	# Why are we doing this?
    if debug: print html
    login_data = urllib.urlencode({'userId' : username, 'password' : password, 'action' : 'doLoginSubmit'})
    code, headers, html, cur_opener = get_url(login_url, data=login_data, opener=cur_opener)
    if debug: print html
    return True
  except Exception as e:
    print 'Error connecting to internet :', e
    return False
  
def internet_disconnect(logout_url):
  '''try to disconnect from the internet'''
  if debug: print "Disconnecting from the internet"
  code, headers, html, cur_opener = get_url(reliance_login_url, timeout=10)
  if debug: print html
  code, headers, html, cur_opener = get_url(logout_url, opener=cur_opener)
  if debug: print html

def internet_keep_alive(test_url, test_string, username, password, portail_url, login_url):
  '''login and keep the connection live'''
  print "Verbose=",debug
  while True:
    if debug: print "Internet keepalive"
    if not is_internet_on(test_url, test_string):
      if debug: print "Not connected"
      while not internet_connect( username, password, portail_url, login_url):
	print "Not connected, retrying"
	pass
    else:
      if debug: print "Connected"
      print "Connected"
      pass
    time.sleep(check_interval)

def main():
  args = parse_args()
  if args.verbose:
    debug=True
  if args.logout:
    internet_disconnect(reliance_logout_url)
    sys.exit(0)
  if not args.username:
    args.username=raw_input("Username: ")
    if not args.username:
      print "Username is required"
      sys.exit(1)
  if not args.password:
    args.password=getpass.getpass()
    if not args.password:
      print "Password is required"
      sys.exit(1)
  if args.internet_on_test_url:
    internet_on_test_url=args.internet_on_test_url
  if args.internet_off_test_string:
    internet_off_test_string=args.internet_off_test_string
  username=args.username
  password=args.password
  #if debug: print "Username=",username
  #if debug: print "Password=",password
  if debug: print "internet_on_test_url=",internet_on_test_url
  if debug: print "internet_off_test_string=",internet_off_test_string
  if args.login:
    internet_connect(internet_on_test_url, internet_off_test_string)
    keep_alive = False
  elif args.nokeepalive:
    keep_alive = False
  else:
    keep_alive = True
  ''' default action without any arguments - keep alive'''
  if keep_alive:
    if debug: print "Starting keepalive"
    internet_keep_alive(internet_on_test_url, internet_off_test_string, username, password, reliance_start_portal_url, reliance_login_url);

if __name__ == '__main__':
  main()