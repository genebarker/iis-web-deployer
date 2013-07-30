'''
@author: eugene.barker@wyo.gov
'''

import argparse
import getpass
import os
import re
import shutil
import smtplib
import socket
import subprocess
import sys
import time
from email.mime.text import MIMEText

#---
# set globals
#---
version_number = '1.0a'
config_filename = 'Web.config'
smtp_server = 'smtp.test.com'
program_name = os.path.basename(__file__)
server_name = socket.getfqdn()

#---
# define helper classes functions
#---
def valid_email(email):
	if email==None:
		return False
	return re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email)!=None

#---
# setup command line parser
#---
parser = argparse.ArgumentParser(prog=program_name,
									description='''
										deploy web application to IIS using Git.
									''',
									epilog='''
										notes: Git's bin and IIS's inetsrv folders must be in
										the command path. --path must point to a Git repository
										with its connection to the remote (shared) repository
										setup.
									 ''')
parser.add_argument('-w', '--website', required=True, help='IIS website name')
parser.add_argument('-p', '--path', required=True, help='physical path for website')
parser.add_argument('-c', '--config', help='source website config file to be copied to ' + config_filename)
parser.add_argument('-b', '--branch', required=True, help='branch in repository to deploy to website')
parser.add_argument('-u', '--user', required=True, help='user performing this deployment')
parser.add_argument('-a', '--address', nargs='+', help='email results to specified addresses')
parser.add_argument('-v', '--version', action='version', version=program_name + ' ' + version_number)
args = parser.parse_args()

#---
# context validate arguments
#---
if args.address:
	for e in args.address:
		if not valid_email(e):
			print 'ERROR: (' + e + ') is not a valid email address.'
			exit()

#---
# perform deployment process
#---
print 'Perform Git Based Auto Deployment'
print '- Deploy site (' + args.website + ') to IIS on (' + server_name + ')'
deployment_error = False
branch_loaded = False
try:
	print '- Execute step 1: set working directory to website path'
	os.chdir(args.path)

	print '- Execute step 2: stop website in IIS'
	subprocess.check_call('appcmd stop site /site.name:' + args.website)

	print '- Execute step 3: checkout branch of Git repository'
	subprocess.check_call('git checkout ' + args.branch)

	print '- Execute step 4: discard any local changes'
	subprocess.check_call('git reset --hard')
	if args.config and os.path.isfile(config_filename):
		os.remove(config_filename)

	print '- Execute step 5: get latest files from the remote repository'
	subprocess.check_call('git pull origin ' + args.branch)
	branch_loaded = True

	print '- Execute step 6: install config file'
	if args.config:
		shutil.copyfile(args.config, config_filename)

	print '- Execute step 7: start website in IIS'
	subprocess.check_call('appcmd start site /site.name:' + args.website)

	print '- Deployment process COMPLETED without error'

except Exception as e:
	print '- ERROR: step failed, deployment process aborted'
	print '- ERROR: exception - ', e
	print '- Deployment process FAILED'
	deployment_error = True

#---
# email results
#---
if args.address:
	sender = getpass.getuser() + '@' + server_name
	msg_text = """
deployment report
=================
- %s pushed the website (%s) to the deployment system
- deployment of the (%s) branch to (%s) server was initiated
""" % (args.user, args.website, args.branch, server_name)
	if deployment_error:
		subject_text = 'Deployment process FAILED for (' + args.website + ')'
		msg_text += '- deployment process failed, please check status of website immediately\n'
	else:
		subject_text = 'Deployment process COMPLETED for (' + args.website + ')'
		msg_text += '- deployment process completed without error\n'
	if branch_loaded:
		msg_text += '- see commit log entry below for further detail regarding this deployment\n\n'
		msg_text += subprocess.check_output('git log -1')
	msg = MIMEText(msg_text)
	msg['Subject'] = subject_text
	msg['From'] = sender
	msg['To'] = ','.join(e for e in args.address)
	s = smtplib.SMTP(smtp_server)
	s.sendmail(sender, args.address, msg.as_string())
	s.quit	

if deployment_error:
	sys.exit(1)
else:
	sys.exit(0)
