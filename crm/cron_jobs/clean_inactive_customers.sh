#!/bin/bash

# Navigate to project root (adjust if manage.py is elsewhere)
PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

DELETED_COUNT=$(cd "$PROJECT_DIR" && python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
qs = Customer.objects.filter(order__isnull=True, created_at__lt=one_year_ago)
count = qs.count()
qs.delete()
print(count)
")

echo \"[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers\" >> /tmp/customer_cleanup_log.txt

