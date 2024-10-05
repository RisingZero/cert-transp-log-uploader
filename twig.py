import base64
import ssl
from datetime import datetime
import os
import requests
from typing import List, Tuple
from cryptography import x509

URL = os.environ.get("CT_DOMAIN", "twig.ct.letsencrypt.org")

twig_paths = {
    "2024h1": {
        "not_before": datetime.fromisoformat("2023-12-20T00:00Z"),
        "not_after": datetime.fromisoformat("2024-07-20T00:00Z"),
    },
    "2024h2": {
        "not_before": datetime.fromisoformat("2024-06-20T00:00Z"),
        "not_after": datetime.fromisoformat("2025-01-20T00:00Z"),
    },
    "2025h1": {
        "not_before": datetime.fromisoformat("2024-12-20T00:00Z"),
        "not_after": datetime.fromisoformat("2025-07-20T00:00Z"),
    },
    "2025h2": {
        "not_before": datetime.fromisoformat("2025-06-20T00:00Z"),
        "not_after": datetime.fromisoformat("2026-01-20T00:00Z"),
    },
}


def get_roots(year_path) -> List[str]:
    res = requests.get(f"https://{URL}/{year_path}/ct/v1/get-roots").json()
    return res["certificates"]


def add_chain(certificate_chain: List[str]) -> Tuple[int, str]:
    # check CT log path
    cert_bytes = base64.b64decode(certificate_chain[0])
    cert_pem = ssl.DER_cert_to_PEM_cert(cert_bytes)
    certificate = x509.load_pem_x509_certificate(cert_pem.encode())
    expiry_date = certificate.not_valid_after_utc

    twig_path = ""
    for year_path, dates in twig_paths.items():
        if dates["not_before"] <= expiry_date <= dates["not_after"]:
            twig_path = year_path
            break

    if not twig_path:
        return (
            False,
            "Certificate not in range, not added to CT log",
            expiry_date.isoformat(),
        )

    print(f"Adding chain to {twig_path}")

    # upload chain to CT log
    res = requests.post(
        f"https://{URL}/{twig_path}/ct/v1/add-chain", json={"chain": certificate_chain}
    )
    if res.status_code == 200:
        res = res.json()
        return True, res["timestamp"], res["signature"]
    else:
        return False, res.text, None
