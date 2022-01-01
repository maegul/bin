#!/usr/bin/env python3

import dev_backup as db
import datetime as dt

success_times = db.success_log_path.read_text().splitlines()
last_success = success_times[-1]

last_success_time = dt.datetime.fromisoformat(last_success)

# now will be in local timezone
# last_success_time will be in whatever recorded in isoformat
# python will use timezone differences to get accurate delta
# timezone naive is not permitted here!
time_since = dt.datetime.now().astimezone() - last_success_time.astimezone()

time_since_days = time_since.total_seconds() / (3600 * 24)

if __name__ == '__main__':
	print(f'{time_since_days:.2f}')




