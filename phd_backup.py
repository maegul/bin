#!/usr/bin/env python3
"""Back up all phd related content to multiple targets
"""

import subprocess as sp
from pathlib import Path
import os
import signal
import logging
from logging import handlers
import datetime as dt
from collections import namedtuple
import argparse

tm_fmt = Path('~/.phd_backup/backup_time_format').expanduser().read_text()
current_time = lambda : dt.datetime.now().strftime(tm_fmt)

BackUpPaths = namedtuple('BackUpPath', ['local', 'dest', 'type', 'name'])

# # Logging
main_logger = logging.getLogger('phd_backup')
main_logger.setLevel(10)
success_logger = logging.getLogger('phd_backup_success')
success_logger.setLevel(10)

log_path = Path('~/.phd_backup/backup_log')
# log_path = Path('~/.phd_backup/test_log')
success_log_path = Path('~/.phd_backup/backup_success_times')
# success_log_path = Path('~/.phd_backup/test_success_log')

# log_handler = logging.FileHandler(log_path.expanduser())
log_handler = handlers.RotatingFileHandler(
        log_path.expanduser(),
        maxBytes=5_000_000, backupCount=4
    )
log_handler.setFormatter(
        logging.Formatter('{asctime} {levelname:8s} {message}', style='{')
    )
log_handler.setLevel(10)
# success_time_handler = logging.FileHandler(success_log_path.expanduser())
success_time_handler = handlers.RotatingFileHandler(
        success_log_path.expanduser(),
        maxBytes=500, backupCount=8
    )
success_time_handler.setLevel(10)

main_logger.addHandler(log_handler)
success_logger.addHandler(success_time_handler)


# # Paths config
# S3_BUCKET = 's3://errol-backup-bucket/'
# PHD_PREFIX = 'phd_backup/'
mk_s3_path = 's3://errol-backup-bucket/phd_backup/{}'.format
AWS_BACKUP_PROFILE = 'maegul_backup'

mk_rysnc_path = 'rsync_net:science_backup/{}'.format

# local path: s3 path
back_up_paths = (
    # using os.path.expanduser in order to retain trailing slash?
    BackUpPaths(
        local= os.path.expanduser("~/Dropbox (Personal)/Science/"),
        dest = mk_s3_path("Science/"), 
        type='s3',
        name='science work'),  # all of science main
    BackUpPaths(
        local = "/Volumes/MagellanSG/PhD/Data/",
        dest = mk_s3_path("Data/"),
        type = 's3',
        name='science data'),  # actively analysed data
    BackUpPaths(
        local = "/Volumes/MagellanSG/Zotero/",
        dest = mk_s3_path("Zotero/"),
        type= 's3',
        name='zotero'),  # zotero papers repository (pdfs and database)
    BackUpPaths(
        local= os.path.expanduser("~/Dropbox (Personal)/Science/"),
        dest = mk_rysnc_path("science/"),
        type='rsync_net',
        name='science work'),  # all of science main
    BackUpPaths(
        local = "/Volumes/MagellanSG/PhD/Data/",
        dest = mk_rysnc_path("data/"),
        type = 'rsync_net',
        name='science data'),  # actively analysed data
    BackUpPaths(
        local = "/Volumes/MagellanSG/Zotero/",
        dest = mk_rysnc_path("zotero/"),
        type= 'rsync_net',
        name='zotero'),  # zotero papers repository (pdfs and database)
)


# # Functions
def backup_s3(paths: BackUpPaths):
    "Sync local path to destination path on aws s3"

    output = sp.check_output([
                    'aws', 's3', 'sync',
                    paths.local, paths.dest,
                    "--profile", AWS_BACKUP_PROFILE,
                    '--no-progress'
                ])

    return output


def backup_rsync_net(paths: BackUpPaths):
    '''Sync local path to destination path on rsync.net

    Relies on ~/.ssh/config having an alias for rsync.net ssh access
    '''

    output = sp.check_output([
                    'rsync', '-avz',
                    paths.local, paths.dest
                ])

    return output

backup_funcs = {
    's3': backup_s3,
    'rsync_net': backup_rsync_net
}

backup_successes = {}


# # Main backup function
def backup(backup_type=None):

    for paths in back_up_paths:

        if backup_type is not None and paths.type != backup_type:
            continue

        # dest_path = S3_BUCKET + PHD_PREFIX + dest_prefix
        # print(f'Backing up: \n{path} -->\n{dest_path}')
        main_logger.info(f'{paths.type.upper()}: Backing up {paths.local} --> {paths.dest}')
        backup_successes[paths] = False

        # ## ensure zotero is closed before copying data (to prevent corruption)
        # ### !SHOULD BE WRAPPED UP INTO SOME CALLBACK STRUCTURE
        if paths.name.lower() == 'zotero':
            zotero_pid = None  # initialise
            try:
                # get process id (unix only)
                zotero_pid = sp.check_output(['pgrep', '-i', 'zotero'])
            except sp.CalledProcessError as e:
                # check exit codes
                # 2 and 3 = invalid or error (ie failed to get pid)
                # BSD or macOS specific exit codes?
                if e.returncode == 2 or e.returncode == 3:
                    # therefore move on and this is a failure
                    main_logger.critical(f'Failed to locate Zotero application pid, cannot close zotero and backup data')
                    continue
                # 1 means application pid simply not found
                elif e.returncode == 1:
                    # application isn't running
                    zotero_pid = None
                    main_logger.info('Zotero application is not running')
            else:
                main_logger.info(f'Zotero application running, pid: {zotero_pid}')

            # if application is running
            if zotero_pid is not None:
                # try to kill
                try:
                    # convert to int
                    # will fail if multiple pids come back (separated by new line) ... NOT HANDLED HERE!
                    to_kill_pid = int(zotero_pid)
                    # kill!
                    os.kill(to_kill_pid, signal.SIGKILL)
                except Exception as e:
                    main_logger.critical(f'Failed to close Zotero application, cannot backup')
                    # can't kill, therefore failure and move on
                    main_logger.exception('')  # log exception
                    continue
                else:
                    main_logger.info(f'Killed zotero application with pid {to_kill_pid}')

        # ## attempt backup
        try:
            output = backup_funcs[paths.type](paths)

            main_logger.debug('\n'+output.decode())
            backup_successes[paths] = True

        except sp.CalledProcessError as e:
            # ## handle aws s3 return codes
            # returncode 2 for aws s3 means file skipped: https://docs.aws.amazon.com/cli/latest/topic/return-codes.html
            if paths.type == 's3' and e.returncode == 2:
                main_logger.warning(f'Files skipped (exit status 2) for {paths.type.upper()}')
            else:
                main_logger.exception(f'Failed to backup {paths.local} to {paths.type}')
            # print(f'Failed to backup {path}')
            # print(e)
        except Exception as e:
            main_logger.critical(f'Program failed to backup {paths.local} to {paths.type}',
                exc_info=True)


        # ## Restart Zotero if closed?
        if paths.name.lower() == 'zotero' and (zotero_pid is not None):  #  if zotero was running (and presumably closed?)
            try:
                # get process id (unix only)
                main_logger.info('Attempting to reopen zotero as was closed for backup')
                _ = sp.check_output(['open', '-a', 'Zotero'])
            except Exception as e:
                main_logger.exception('Failed to reopen Zotero')
            else:
                new_zotero_pid = sp.check_output(['pgrep', '-i', 'zotero'])
                main_logger.info(f'Zotero running again with pid {new_zotero_pid}')





    if all(backup_successes.values()):
        success_logger.info(current_time())
    else:
        for k,v in backup_successes.items():
            main_logger.info(f'{"SUCCESS" if v else "FAILED"}: {k.type}:{k.local}')


# # Argument parsing and running
parser = argparse.ArgumentParser(description='Backup PhD materials')

parser.add_argument('-t', '--type',
                    default=None,
                    choices=['s3', 'rsync_net'],
                    help='Which type of backup, ie, which cloud provider etc'
    )

args = parser.parse_args()
backup(backup_type=args.type)

