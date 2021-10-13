#!/usr/bin/env python3

import dev_backup as db
import datetime as dt

success_times = db.success_log_path.read_text().splitlines()
last_success = success_times[-1]

last_success_time = dt.datetime.fromisoformat(last_success)

time_since = dt.datetime.now().astimezone() - last_success_time.astimezone()

time_since_days = time_since.total_seconds() / (3600 * 24)

print(f'{time_since_days:.2f}')



