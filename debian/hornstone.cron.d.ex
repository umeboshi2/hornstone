#
# Regular cron jobs for the hornstone package
#
0 4	* * *	root	[ -x /usr/bin/hornstone_maintenance ] && /usr/bin/hornstone_maintenance
