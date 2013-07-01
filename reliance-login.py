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
#import argparse - TODO : use argparse to handle arguments, take username and password as agruments

# Default value definitions
username = 'username'
password = 'password'

# Constant definitions
internet_on_test_url='http://google.com'
internet_off_test_string='reliance'
reliance_start_portal_url="http://reliancebroadband.co.in/reliance/startportal_isg.do"
reliance_login_url='http://reliancebroadband.co.in/reliance/login.do'
reliance_logout_url='http://reliancebroadband.co.in/reliance/logout.do'
user_agent_string='Mozilla/5.0 (Windows NT 6.1; U; ru; rv:5.0.1.6) Gecko/20110501 Firefox/5.0.1 Firefox/5.0.1'

'''You don't normally have to edit anything below this line'''
debug = True
check_interval = 600

if ((len(sys.argv) > 2) and (sys.argv[2] == '-d')): debug = True

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

def is_internet_on():
  '''test if the machine is connected to the internet'''
  if debug: print "Testing"
  try:
    code, headers, html, opener = get_url(internet_on_test_url, timeout=10)
    if debug: print html
    if re.search(internet_off_test_string, html):
      return False
    else:
      return True
  except: 
    if debug: print "Error"
    return False
  return False

def internet_connect():
  '''try to connect to the internet'''
  code, headers, html, cur_opener = get_url(reliance_start_portal_url, timeout=10)	# Why are we doing this?
  if debug: print html
  login_data = urllib.urlencode({'userId' : username, 'password' : password, 'action' : 'doLoginSubmit'})
  code, headers, html, cur_opener = get_url(reliance_login_url, data=login_data, opener=cur_opener)
  if debug: print html

def internet_disconnect():
  '''try to disconnect from the internet'''
  code, headers, html, cur_opener = get_url(reliance_login_url, timeout=10)
  if debug: print html
  code, headers, html, cur_opener = get_url(reliance_logout_url, opener=cur_opener)
  if debug: print html

def internet_keep_alive():
  '''login and keep the connection live'''
  while True:
    if not is_internet_on():
      if debug: print "Not connected"
      internet_connect()
    else:
      if debug: print "Connected"
      pass
    time.sleep(check_interval)

def print_usage():
  print "Reliance Netconnect AutoLogin"
  print "-----------------------------"
  print "usage:" + sys.argv[0] + " [login|logout]\n" 
  print "If there are no arguments it runs in an infinite loop and will try to remain connected to the internet."

def main():
  keep_alive = True
  if (len(sys.argv) > 1):
    op = sys.argv[1]
    if op == 'login':
      internet_connect()
      keep_alive = False
    elif op == 'logout':
      internet_disconnect()
      keep_alive = False
    elif op == 'keep-alive':
      keep_alive = True
      pass
    else:
      print_usage()
      keep_alive = False
  
  ''' default action without any arguments - keep alive'''
  if keep_alive:
    internet_keep_alive();

if __name__ == '__main__':
  main()
