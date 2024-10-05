# Certificate Transparency Logs Uploader

This tool allows to automatically fetch discovered x509 certificates from publicly available OONI datasets and upload them to Let's Encrypt Twig Certificate Transparency log.

The tool to download certificate chains from OONI data and later upload them to Twig CT log has been developed using as support the Celery task manager, in order to parallelize the operations, mainly affected by I/O time.

To spin up the background worker and the message broker, from inside the root folder
```bash
docker compose up --build
```
These two components, in an hypothetic deployment, would be always running (local server or cloud environment), waiting for the `main.py` script to be launched every hour, triggering record fetch and upload tasks.

To launch the periodic script
```bash
python3 -m venv penv
source penv/bin/activate
pip install -r requirements.txt
```

```bash
python3 main.py
```

The script will fetch all record indexes up to the current day and hour, from a fixed "day0" coded in the script or from the last fetched day and hour, if any

This repository was developed as part of a code challenge for an intership.

MISSING: further optimizations could be implemented in the upload phase to the CT log, in particular checking if the root CA certificate of the certificate chain being sent is among the ones accepted by the log
