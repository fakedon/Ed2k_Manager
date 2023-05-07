

from datetime import datetime


def get_time(format='%Y-%m-%d %H:%M:%S',trans_to_filename=False):
   
   if trans_to_filename:
      format = "%Y-%m-%d_%H.%M.%S"
   time_now = datetime.now().strftime(format)

   return time_now
