# Linux Temperature and Load Monitoring

In short, this is a helper script that I created to log relevant information for troubleshooting my overheating machine, which was causing CPU throttling and a less-than-desirable computing experience.

This script does the following:

- Retrieve and log CPU core temperatures
- Retrieve and log computer fan speed
- Retrieve and log system load for the past minute
- Retrieve and log any systemd journal entries indicating a throttled CPU condition
- Notify (GNOME desktop environment) if a throttled CPU condition has been met

This script makes a handful of assumptions (primarily because this was made for my environment):

- Using systemd (for throttle log entries)
- Using GNOME (for desktop notifications)
- The `lm_sensors` package must be installed (on Fedora: `$ sudo dnf install -y lm_sensors`)

### Scheduling the script

I have scheduled this script to run every minute. This is the crontab entry to accomplish this (`crontab -e`):

```
* * * * * /home/trstringer/dev/python/temp-monitor/app.py
```
