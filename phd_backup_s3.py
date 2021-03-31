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
# from pathlib import Path

S3_BUCKET = 's3://errol-backup-bucket/'
BACKUP_PROFILE = 'maegul_backup'
PHD_PREFIX = 'phd_backup/'

# local path: s3 path
back_up_paths = {
    "/Users/errollloyd/Dropbox (Personal)/Science/": "Science/",  # all of science main
    "/Volumes/MagellanX/PhD/Data/": "Data/",  # actively analysed data
    "/Volumes/MagellanX/Zotero/": "Zotero/"  # zotero papers repository (pdfs and database)
}

for path, dest_prefix in back_up_paths.items():
    dest_path = S3_BUCKET + PHD_PREFIX + dest_prefix
    print(f'Backing up: \n{path} -->\n{dest_path}')
    try:
        sp.check_output([
            'aws', 's3', 'sync',
            path, dest_path,
            "--profile", BACKUP_PROFILE
        ])
    except Exception as e:
        print(f'Failed to backup {path}')
        print(e)
