from celery import Celery
from datetime import date
import ooni
import os
from typing import List
import twig

TASK_BROKER_HOST = os.environ.get("TASK_BROKER_HOST", "localhost")
TASK_BROKER_PORT = os.environ.get("TASK_BROKER_PORT", "5672")
TASK_BROKER_USER = os.environ.get("TASK_BROKER_USER", "worker")
TASK_BROKER_PASS = os.environ.get("TASK_BROKER_PASS", "workerpass")
RABBITMQ_DEFAULT_VHOST = os.environ.get("RABBITMQ_DEFAULT_VHOST", "vh1")

app = Celery(
    __file__,
    broker=f"amqp://{TASK_BROKER_USER}:{TASK_BROKER_PASS}@{TASK_BROKER_HOST}:{TASK_BROKER_PORT}/{RABBITMQ_DEFAULT_VHOST}",
    task_routes={
        "fetch_index_records": {"queue": "queue1"},
        "dwnld_extr_tls": {"queue": "queue2"},
        "upload_ctlog": {"queue": "queue3"},
    },
)
app.control.rate_limit("worker.upload_ctlog", "20/m")


@app.task
def upload_ctlog(certs: List[str]):
    """
    Check possible chain rejection
    Upload chain to CT log
    """
    ok, p1, p2 = twig.add_chain(certs)
    if ok:
        ts, sig = p1, p2
        print(ts, sig)
    else:
        print("failed", p1, p2)
    return ok


@app.task
def dwnld_extr_tls(record: str):
    """
    Download record from S3 bucket
    Extract list of certificate chains inside records
    Submit task for chain submissions to CT
    """
    file = ooni.download_measurement(record)
    for cert_chain in ooni.extract_tls_certificates(file):
        upload_ctlog.delay(cert_chain)
    os.remove(file)
    return True


@app.task
def fetch_index_records(day: date, hour: int, country: str, test=False):
    """
    Fetch list of measurement files from S3 bucket for given folder index
    Submit task for record download
    """
    records = ooni.get_measurements_list(day, hour, country)
    for record in records:
        dwnld_extr_tls.delay(record)
    return True
