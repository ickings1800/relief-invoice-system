from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pos.models import OrderItem
import requests
import time
import csv
import os
from datetime import datetime, timedelta
from io import StringIO

class Command(BaseCommand):
    help = "Imports orderitems through Detrack CSV"

    def add_arguments(self, parser):
        parser.add_argument("--date", type=str, help="Date in format dd-mm-yyyy", required=True)

    def handle(self, *args, **options):
        self.stdout.write(settings.DETRACK_API_KEY)

        try:
            delivery_date_str = options.get('date', None)
            delivey_date_parse = datetime.strptime(delivery_date_str, "%d-%m-%Y")
        except ValueError:
            raise CommandError("Invalid date format. Please use dd-mm-yyyy.")
            return

        headers = {
            'X-API-KEY': settings.DETRACK_API_KEY,
            'Content-Type': 'application/json'
        }

        url = 'https://app.detrack.com/api/v2/exports/jobs'

        payload = {
            "data": {
                "query": {"type": "Delivery"},
                "date": delivey_date_parse.strftime("%d-%m-%Y"),
                "ids": [],
                "format": "csv",
                "document": "job",
                "with_items": True
            }
        }

        try:
            res = requests.post(url, headers=headers, json=payload)
            res.raise_for_status()
            download_obj = res.json()['data']
        except Exception as e:
            raise CommandError("Failed to initiate export:", e)
            return

        retries = 0
        while download_obj['status'] != "completed" and retries < 10:
            try:
                download_url = f"https://app.detrack.com/api/v2/exports/{download_obj['id']}"
                res = requests.get(download_url, headers=headers)
                res.raise_for_status()
                download_obj = res.json()['data']
            except Exception as e:
                raise CommandError("Retry error:", e)
                return
            
            time.sleep(5)
            retries += 1
            self.stdout.write(f"Retrying:: {retries}")

        if not download_obj.get('download_url'):
            raise CommandError("Export did not complete successfully due to timeout.")

        try:
            res = requests.get(download_obj['download_url'], headers=headers)
            decoded_content = res.content.decode('utf-8')
            with open('/tmp/detrack_import.csv', 'w+') as f:
                f.write(decoded_content)
            with open('/tmp/detrack_import.csv', 'r') as f:
                OrderItem.handle_detrack_import(f)
                self.stdout.write(self.style.SUCCESS("Success! Detrack import completed successfully."))
                return
        except Exception as e:
            raise CommandError("Download or parse error:", e)
            return
