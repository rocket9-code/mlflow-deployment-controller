"""
__author__ = "Raghul Krishna"
__copyright__ = ""
__credits__ = ""
__license__ = ""
__version__ = ""
__maintainer__ = "raghul Krishna"
__email__ = "rrkraghulkrishna@gmail.com"

"""
from time import sleep
import logging
from mlflow_controller.controller import DeployConroller
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler


logging.getLogger("apscheduler").setLevel(logging.ERROR)


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    controller = DeployConroller()
    scheduler.add_job(
        controller.deploy_controller, CronTrigger.from_crontab("* * * * *")
    )
    scheduler.start()
    while True:
        sleep(1)
