import squidgirl
from threading import Thread

job = Thread(target=squidgirl.run)
job.start()
