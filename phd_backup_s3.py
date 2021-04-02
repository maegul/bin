#! /usr/bin/env python3
"""Back up all phd related content to aws s3 buckets

Using aws s3 sync, which synchronises based on file names/paths and modified time
sync is recursive by nature (I think)

# TODO
> aws client errors and how to handle ...
    > eg, for now deleted files or bad links etc
> pipe output of aws command to a file for live viewing when desired
    > Probably overwrite everytime
> Use logging rather than printing to console
    > have a logs folder similar to ~/bin folder for all user scritps/processes
> set up a cron job
    > run every day to check for frequency threshold
    > log time for when *complete* backup has been done
> Update time logging to work with the prompt system
    > C

"""

import subprocess as sp
from pathlib import Path
import logging
import datetime as dt

tm_fmt = Path('~/.phd_backup/backup_time_format').expanduser().read_text()
current_time = lambda : dt.datetime.now().strftime(tm_fmt)

main_logger = logging.getLogger('phd_backup')
main_logger.setLevel(10)
success_logger = logging.getLogger('phd_backup_success')
success_logger.setLevel(10)

log_path = Path('~/.phd_backup/backup_log')
# log_path = Path('~/.phd_backup/test_log')
success_log_path = Path('~/.phd_backup/backup_success_times')
# success_log_path = Path('~/.phd_backup/test_success_log')

log_handler = logging.FileHandler(log_path.expanduser())
log_handler.setFormatter(
    logging.Formatter('{asctime} {levelname:8s} {message}', style='{')
    )
log_handler.setLevel(10)
success_time_handler = logging.FileHandler(success_log_path.expanduser())
success_time_handler.setLevel(10)
main_logger.addHandler(log_handler)
success_logger.addHandler(success_time_handler)


# S3_BUCKET = 's3://errol-backup-bucket/'
# PHD_PREFIX = 'phd_backup/'
mk_s3_path = 's3://errol-backup-bucket/phd_backup/{}'.format
BACKUP_PROFILE = 'maegul_backup'

# local path: s3 path
back_up_paths = (
    (Path("~/Dropbox (Personal)/Science/").expanduser(), mk_s3_path("Science/")),  # all of science main
    (Path("/Volumes/MagellanX/PhD/Data/"), mk_s3_path("Data/")),  # actively analysed data
    (Path("/Volumes/MagellanX/Zotero/"), mk_s3_path("Zotero/"))  # zotero papers repository (pdfs and database)
)

backup_successes = {}

for path, dest_path in back_up_paths:
    # dest_path = S3_BUCKET + PHD_PREFIX + dest_prefix
    # print(f'Backing up: \n{path} -->\n{dest_path}')
    main_logger.info(f'S3: Backing up {path} --> {dest_path}')
    backup_successes[path] = False

    try:
        output = sp.check_output([
                        'aws', 's3', 'sync',
                        path, dest_path,
                        "--profile", BACKUP_PROFILE,
                        '--no-progress'
                    ])
        # output = sp.check_output(['ls', '-haltF', '/Users/errollloyd/Downloads'])
        main_logger.debug('\n'+output.decode())
        backup_successes[path] = True

    except sp.CalledProcessError as e:
        # returncode 2 for aws s3 means file skipped: https://docs.aws.amazon.com/cli/latest/topic/return-codes.html
        if e.returncode == 2:
            main_logger.warning('Files skipped (exit status 2)')
        else:
            main_logger.exception(f'Failed to backup {path}')
        # print(f'Failed to backup {path}')
        # print(e)

if all(backup_successes.values()):
    success_logger.info(current_time())
else:
    for k,v in backup_successes.items():
        main_logger.info(f'{"SUCCESS" if v else "FAILED"}: {k}')
