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
import os
from time import sleep

from apscheduler.schedulers.background import BackgroundScheduler

from mlflow_controller.gitops import GitopsMDC
from mlflow_controller.mlflow_direct import DeployConroller

logging.getLogger("apscheduler").setLevel(logging.ERROR)

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    controller = DeployConroller()
    giopsmdc = GitopsMDC()
    # scheduler.add_job(
    #     controller.deploy_controller, CronTrigger.from_crontab("* * * * *")
    # )
    # scheduler.add_job(
    #     id="controller",
    #     func=controller.deploy_controller,
    #     trigger="interval",
    #     seconds=15,
    # )
    if os.getenv("GITOPS_ENABLED", "False"):
        scheduler.add_job(
            id="gitopsmdc",
            func=giopsmdc.gitops_mlflow_controller,
            trigger="interval",
            seconds=15,
        )
    scheduler.start()
    while True:
        sleep(1)
