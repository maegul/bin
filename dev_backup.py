#!/usr/bin/env python3

import os
import shutil
import logging
from logging import handlers
import subprocess as sp
import datetime as dt
from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Optional
from contextlib import contextmanager

# # main path
main_path = Path('~/.dev_backup').expanduser()

if not main_path.exists():
	main_path.mkdir()

# # logger setup
main_logger = logging.getLogger('dev_backup')
main_logger.setLevel(10)
success_logger = logging.getLogger('dev_backup_success')
success_logger.setLevel(10)

log_path = main_path / 'backup_log'
success_log_path = main_path / 'backup_success_times'

log_handler = handlers.RotatingFileHandler(
		log_path.expanduser(),
		maxBytes=5_000_000, backupCount=4
	)
log_handler.setFormatter(
		logging.Formatter('{asctime} {levelname:8s} {message}', style='{')
	)
log_handler.setLevel(10)
success_time_handler = handlers.RotatingFileHandler(
		success_log_path.expanduser(),
		maxBytes=500, backupCount=8
	)
success_time_handler.setLevel(10)

main_logger.addHandler(log_handler)
success_logger.addHandler(success_time_handler)


# # Utils

def current_time():
	return dt.datetime.now().astimezone(dt.timezone.utc).isoformat()


@contextmanager
def temp_dir(new_dir: Path):
	old_dir = os.getcwd()
	try:
		os.chdir(new_dir.expanduser())
		yield
	finally:
		os.chdir(old_dir)

@dataclass
class DevDir:
	name: str
	path: Path

# encrypts with openssl, retrieving a password from macOS keychain using security CLI
# then copies to an icloud destination
# should double with an S3 backup too
@dataclass
class EncryptedICloudBackup:
	name: str
	path: Path
	dest: Path
	pw_name: str
	pw_account: str = "errollloyd"

	def backup(self):
		if self.dest is None:
			raise ValueError("Must provide destination path (none provided)!")

		# copy database file for safe keeping
		path = self.path.expanduser()
		dest = self.dest.expanduser()
		shutil.copy(path, Path("/tmp/preserved_zekell_backup"))

		# get encryption password
		pw = sp.check_output([
				"security", "find-generic-password", "-w",
				'-s', self.pw_name, '-a', self.pw_account
			])
		pw = pw.decode().strip()

		# Encrypt to dest path
		_ = sp.check_output([
				"openssl", "enc", "-aes-256-cbc",
				"-in", path, "-out", dest,
				"-pass", f"pass:{pw}"
			])

		return f"Encrypted to {dest}"



class GenericGitBackup(DevDir):

	def backup(self):
		"""
		Git returns a non-zero status code for everything apart from
		complete success (or so it seems)
		So ... any problems should raise an exception (by subprocess) and result
		in a success status of False
		"""

		with temp_dir(self.path):
			# only if changes made
			check = sp.check_output(['git', 'status', '--porcelain'])
			# check if untracked files
			untracked = sp.check_output(['git', 'ls-files', '--others', '--exclude-standard'])

			if check:
				if untracked:
					# just add them all ... probably a better/safer/more direct way to do this
					_ = sp.check_output(['git', 'add', '.'])
				_ = sp.check_output([
						"git", "commit", "-am", f"AUTO update on {dt.date.today().isoformat()}"])

			# presumes that there is a remote!
			output = sp.check_output([
					"git", "push"],
					stderr=sp.STDOUT
					)

			return output.decode()
			# else:
			# 	return 'No changes to commit'

# # Backup dirs

dev_dirs = [
	GenericGitBackup(
		'sublime_user_config',
		Path("~/Library/Application Support/Sublime Text/Packages/User")
		),
	GenericGitBackup(
		'user binaries and scripts',
		Path("~/bin")
		),
	GenericGitBackup(
		'dotfiles',
		Path('~/.dotfiles/')
		),
	# might want to create a better backup situation around this
	# !! as copying an open sqlite database can be corrupting??
	# at least the files are there!
	# Cancel storing on github ... inappropriate for personal information
	# GenericGitBackup(
	# 	'my zettelkasten',
	# 	Path('~/zekell/')
	# 	),
	EncryptedICloudBackup(
		name = "my zekell backup",
		path = Path("~/zekell/zekell.db"),
		dest = Path(
			"~/Library/Mobile Documents/com~apple~CloudDocs/backups/zekell_backup.db"),
		pw_name = "zekell_backup_pw"
		),
	GenericGitBackup(
		'my hammerspoon config',
		Path('~/.hammerspoon/')
		),
]


def main():

	successes = {dd.name: False for dd in dev_dirs}

	for dd in dev_dirs:
		main_logger.info(f'Backing up {dd.name} ({dd.path})')
		result = None
		try:
			result = dd.backup()
		except Exception:
			main_logger.debug(f'Output: {result}')
			main_logger.critical(f'Failed to backup {dd.name}', exc_info=True)
		else:  # on success
			main_logger.debug(f'Output: {result}')
			successes[dd.name] = True

	if all(successes.values()):
		success_logger.info(current_time())


if __name__ == '__main__':
	main()
