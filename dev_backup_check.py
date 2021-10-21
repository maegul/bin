#!/usr/bin/env python3

import datetime as dt
import subprocess as sp
import getpass

import dev_backup_since as dbs

threshold = dt.timedelta(days=7)

user = getpass.getuser()

if dbs.time_since > threshold:
	output = sp.check_output(
			["mail", "-s", "No recent Dev backup", user],
			input=(f'Last backup {dbs.time_since_days} days ago'.encode())
			)
