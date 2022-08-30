"""
__author__ = "Raghul Krishna"
__copyright__ = ""
__credits__ = ""
__license__ = ""
__version__ = ""
__maintainer__ = "raghul Krishna"
__email__ = "rrkraghulkrishna@gmail.com"

"""
import logging
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from mlflow_controller.controller import DeployConroller

logging.getLogger("apscheduler").setLevel(logging.ERROR)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    controller = DeployConroller()
    # scheduler.add_job(
    #     controller.deploy_controller, CronTrigger.from_crontab("* * * * *")
    # )
    scheduler.add_job(
        id='controller', func=controller.deploy_controller, trigger='interval', seconds=15
    )
    scheduler.start()
    while True:
        sleep(1)
