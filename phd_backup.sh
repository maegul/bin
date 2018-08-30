now=$(date +'%Y_%m_%d_%H_%M')

rsync -avb --backup-dir=old_files/$now /Users/errollloyd/Dropbox/Science/ /Volumes/External_100GB/macbookpro_backup/Science/

rsync -avb --backup-dir=old_files/$now /Users/errollloyd/Documents/  /Volumes/External_100GB/macbookpro_backup/Documents/ 

