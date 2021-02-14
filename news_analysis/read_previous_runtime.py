import time
import pickle



with open("last_run_times.pkl", 'rb') as F:
    ts = pickle.load(F)

DATEFORMAT = '%H:%M  %Y-%m-%d  %Z'
# if you encounter a "year is out of range" error the timestamp
# may be in milliseconds, try `ts /= 1000` in that case
print("Current time:    ", time.strftime(DATEFORMAT, time.localtime(time.time())))

for k in ts.keys():
    print(f"Last {k:>7}:     {time.strftime(DATEFORMAT, time.localtime(ts[k])) if ts[k]> 0 else 'N/A':>40}")