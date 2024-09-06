import logging
from prefect import task, flow
from prefect.deployments import Deployment
from prefect.client.schemas.schedules import CronSchedule
from create_db import create_database_if_not_exist


@task
def create_database_if_not_exist_task():
    logging.info("Creating database if not exist.")
    create_database_if_not_exist()
    logging.info("Database creation check completed.")

@task()
def populate_database_task():
    from data_writer import populate_database as populate_db_function

    logging.info("Populating the database.")
    populate_db_function()
    logging.info("Database population completed.")
@flow(name="Database Setup Flow")
def database_setup_flow():
    create_database_if_not_exist_task()
    populate_database_task()

if __name__ == "__main__":
    deployment = Deployment.build_from_flow(
        flow=database_setup_flow,
        name="database-setup",
        schedule=(CronSchedule(cron="*/1 * * * *", timezone="America/Chicago"))
    )
    deployment.apply()
    database_setup_flow()