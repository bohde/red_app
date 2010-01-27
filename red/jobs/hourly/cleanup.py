from django_extensions.management.jobs import HourlyJob
from ide.red.models import MatrixSet
import datetime

hour = datetime.timedelta(hours=1)

class Job(HourlyJob):
    help = "Cleans up the temporary database"

    def execute(self):
        an_hour_ago = datetime.datetime.now() - hour
        for ms in MatrixSet.objects.filter(temp=True).filter(creation__lt=an_hour_ago).all():
                ms.delete()

                
