Performs automated backups to remote machine over ssh (rsync).

Keeps track of timing of each *successful* rsync in a log.


### Scripting

* `phd_rsync_net_backup` - backup phd folders to `rsyn_net`
* `backup_check` - checks time of latest backup
	- If above defined threshold ... runs backup
* `backup_since` - like `backup_check` but prints time since backup in nice format
* Main directory: `.phd_backup`
	- `backup_success_times` - times of successful backups
	- `backup_lob` - output of `rsync` commands with datetime and directory info added
	- 

#### Old Uni VPN system

* **phd_mac_pro_backup** - performas rsync
* **vpn_mac_pro_backup** — Logs in over vpn, performs rsync, if successful, logs time
* **backup_check** - checks time of latest backup, checks if beyond defined threshold, and if so, calls vpn_mac_pro_backup.
	* relies on **backup_since** to retrieve latest backup time.

### Scheduling

**crontab**

* 3 past 3AM every weekday

```
SHELL=/bin/bash
3 3 * * 1,2,3,4,5 /Users/errollloyd/bin/backup_check
```

### Dependencies

* SSH setup for connection to rsync.net service
	- see `~/.ssh/config` for alias

#### Old Uni VPN

* Cisco AnyConnect + CLI (vpn)
	* connects to LAN of location of remote machine
* BSD Open general command

### Implementation

* Manual password entry is required.  
* Thus Open is used to start a new terminal window which effectively works as an operating system pop up.
	* This is used twice.  Once in the crontab directly, and also in the backup_check script for when the time since last backup has passed the threshold.
* A folder at $HOME is used to store the relevant time format and backup log for the particular remote machine.
	* It is anticipated that multiple machines would be used in the future with the same code.  Thus the separate folder specific to the backup machine.
	* The code would require further compartmentalisation to be used effectively with multiple machines:
		* Config files for locations of relevant files and directories and backup source and target locations
		* further separation of the VPN and rsync functions
