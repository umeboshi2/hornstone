#
# Regular cron jobs for the chert package
#
0 4	* * *	root	[ -x /usr/bin/chert_maintenance ] && /usr/bin/chert_maintenance
