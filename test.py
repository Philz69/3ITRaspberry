from database import *
from datetime import datetime
from datetime import timezone
from datetime import timedelta

startMS = 1000
endMS = 2123

timeDelta = (endMS - startMS)/255
timeDelta = timedelta(milliseconds=timeDelta)


timestamp = datetime.now(timezone.utc)

for i in range(0, 255):
    print(timestamp + timeDelta*i)