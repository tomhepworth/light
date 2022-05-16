from datetime import time as dtTime
from datetime import datetime

times = [dtTime(6, 36, 0), dtTime(1, 0, 0), dtTime(2, 30, 0), dtTime(3, 36, 0),
         dtTime(4, 0, 0), dtTime(5, 30, 0), ]

time_now = datetime.now()


def getTimeFromNow(now, time):
    hour_diff = (24 - now.hour + time.hour - 1) if (now.hour >
                                                    time.hour) else (time.hour - now.hour - 1)
    minute_diff = (60 - now.minute +
                   time.minute) if (now.minute > time.minute) else (time.minute - now.minute)
    return (hour_diff, minute_diff)


print(sorted(times, key=lambda z: getTimeFromNow(time_now, z)))
