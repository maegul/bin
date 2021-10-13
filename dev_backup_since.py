#!/usr/bin/env python3

import dev_backup as db
import datetime as dt

success_times = db.success_log_path.read_text().splitlines()
last_success = success_times[-1]

last_success_time = dt.datetime.fromisoformat(last_success)

print(f'{dt.datetime.now().astimezone() - last_success_time.astimezone()}')



