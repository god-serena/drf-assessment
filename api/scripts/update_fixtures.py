from pathlib import Path
import os
from django import utils, setup
from django.db.models import Count, F, Max
import sys
import random
import math

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def main():
    from apps.rides.models import RideEvent

    now = utils.timezone.now()
    ride_ids = list(
        RideEvent.objects.order_by().values_list('ride_id', flat=True).distinct()
    )
    if not ride_ids:
        return

    target_count = math.ceil(len(ride_ids) / 2)
    first_multi_event_ride_id = (
        RideEvent.objects.values('ride_id')
        .annotate(event_count=Count('pk'))
        .filter(event_count__gte=2)
        .order_by('ride_id')
        .values_list('ride_id', flat=True)
        .first()
    )

    recent_ride_ids = (
        [first_multi_event_ride_id]
        if first_multi_event_ride_id is not None
        else []
    )
    remaining_ride_ids = [
        ride_id for ride_id in ride_ids if ride_id not in recent_ride_ids
    ]
    additional_count = target_count - len(recent_ride_ids)
    recent_ride_ids.extend(
        random.sample(remaining_ride_ids, k=additional_count)
    )

    for ride_id in recent_ride_ids:
        latest_event_at = RideEvent.objects.filter(
            ride_id=ride_id
        ).aggregate(latest=Max('created_at'))['latest']
        if latest_event_at is None:
            continue

        target_latest_at = now - utils.timezone.timedelta(
            seconds=random.uniform(0, 24 * 3600)
        )
        shift = target_latest_at - latest_event_at

        RideEvent.objects.filter(ride_id=ride_id).update(
            created_at=F('created_at') + shift
        )


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    setup()
    main()


