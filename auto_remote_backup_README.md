Performs automated backups to remote machine over ssh (rsync).

Keeps track of timing of each *successful* rsync in a log.



### Scheduling

**crontab**
```
SHELL=/bin/bash
1 11,17 * * 2,4,5 open -a Terminal /Users/errollloyd/bin/vpn_mac_pro_backup
3 10,12,14,16 * * 1,2,3,4,5 /Users/errollloyd/bin/backup_check
```

### Dependencies 
* Cisco AnyConnect + CLI (vpn)
	* connects to LAN of location of remote machine
* BSD Open general command

### Scripting

* **phd_mac_pro_backup** - performas rsync
* **vpn_mac_pro_backup** — Logs in over vpn, performs rsync, if successful, logs time
* **backup_check** - checks time of latest backup, checks if beyond defined threshold, and if so, calls vpn_mac_pro_backup.
	* relies on **backup_since** to retrieve latest backup time.


### Implementation

* Manual password entry is required.  
* Thus Open is used to start a new terminal window which effectively works as an operating system pop up.
	* This is used twice.  Once in the crontab directly, and also in the backup_check script for when the time since last backup has passed the threshold.
* A folder at $HOME is used to store the relevant time format and backup log for the particular remote machine.
	* It is anticipated that multiple machines would be used in the future with the same code.  Thus the separate folder specific to the backup machine.
	* The code would require further compartmentalisation to be used effectively with multiple machines:
		* Config files for locations of relevant files and directories and backup source and target locations
		* further separation of the VPN and rsync functions