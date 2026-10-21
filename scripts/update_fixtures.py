from pathlib import Path
import os
from django import utils, setup
import sys
import random
import math

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def main():
    from apps.rides.models.ride_event import RideEvent
    
    now = utils.timezone.now()
    random_seconds = random.uniform(0, 24 * 3600)
    random_dt = now - utils.timezone.timedelta(seconds = random_seconds)
    
    count = RideEvent.objects.all().count()
    random_pks = random.sample(range(1, count + 1 ), k = math.ceil(count / 2))
    
    RideEvent.objects.filter(pk__in = random_pks).update(
        created_at = random_dt
    )

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    setup()
    main()


