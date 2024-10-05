import boto3
from datetime import date
import gzip
import json
import os
from typing import List

s3 = boto3.resource("s3")
bucket = s3.Bucket(os.environ.get("AWS_BUCKET_NAME"))


def get_measurements_list(
    day: date, hour: int, country_code: str
) -> List[str]:
    objs = bucket.objects.filter(
        Prefix=f'raw/{day.strftime("%Y%m%d")}/{str(hour).zfill(2)}/{country_code}/webconnectivity/'
    )
    return list(filter(lambda x: x.endswith(".jsonl.gz"), (o.key for o in objs)))


def download_measurement(path: str) -> str:
    filename = f"data/ooni/{path.split('/')[-1]}"
    with open(filename, "wb") as f:
        bucket.download_fileobj(path, f)
    return filename


def extract_tls_certificates(measurement_file: str):
    with gzip.open(measurement_file, "rb") as f:
        for jsonline in f:
            obj = json.loads(jsonline)
            experiment_keys = obj["test_keys"]
            if (
                "tls_handshakes" in experiment_keys
                and experiment_keys["tls_handshakes"] is not None
            ):
                for handshake in experiment_keys["tls_handshakes"]:
                    if (
                        "peer_certificates" in handshake
                        and handshake["peer_certificates"] is not None
                    ):
                        yield list(
                            map(lambda x: x["data"], handshake["peer_certificates"])
                        )
