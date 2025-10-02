from django.core.management.base import BaseCommand
from analyzer.utils.cluster_accidents import retrain_dbscan

class Command(BaseCommand):
    help = 'Retrain DBSCAN model with latest accident data'

    def handle(self, *args, **kwargs):
        self.stdout.write("📊 Retraining DBSCAN model...")
        retrain_dbscan()
        self.stdout.write("✅ DBSCAN retraining complete.")
