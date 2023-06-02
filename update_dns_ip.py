"""Update DNS entry with public IP."""

import urllib.request
import os
from pathlib import Path
import configparser
import base64
from pprint import pprint
import json
import time
import sys

INTERVAL_MINUTES = int(os.getenv("UPDATE_INTERVAL_MINUTES", "15"))

NAME_COM_DEV_API = "https://api.dev.name.com"
NAME_COM_API = "https://api.name.com"

conf_file_instance = None


def get_conf(key):
    """Get config file entries."""
    global conf_file_instance
    if conf_file_instance is None:
        secrets = Path(__file__).parent / 'secrets.ini'
        if secrets.is_file():
            conf_file_instance = configparser.ConfigParser()
            conf_file_instance.read(secrets)
    if conf_file_instance is None:
        return None
    else:
        return conf_file_instance.get('secrets', key, fallback=None)


NAME_COM_USER = os.getenv("NAME_COM_USERNAME", get_conf("NAME_COM_USERNAME"))
TEST_ENV_API = os.getenv("TEST_TOKEN", get_conf("TEST_TOKEN"))
PROD_ENV_API = os.getenv("PROD_TOKEN", get_conf("PROD_TOKEN"))


def get_ip_address():
    """Get the IP address."""
    with urllib.request.urlopen('https://checkip.amazonaws.com/') as f:
        return f.read(30).decode('UTF-8').strip()


def request_api(path, development=False, method="GET", data=None):
    """Return result of request."""
    base = NAME_COM_API if not development else NAME_COM_DEV_API
    password = PROD_ENV_API if not development else TEST_ENV_API
    if data:
        data = data.encode("utf-8")
    print(f"{method} {path} -- {data}")
    req = urllib.request.Request(f"{base}{path}", method=method, data=data)
    base64string = base64.b64encode(
        bytes(f"{NAME_COM_USER}:{password}", 'ascii'))
    req.add_header("Authorization", f"Basic {base64string.decode('utf-8')}")
    if method in ("POST", "PUT"):
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as f:
            return f.read().decode(encoding='utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        server_response = e.read().decode('utf-8')
        server_response = json.loads(server_response)
        msg = f"{e}\n{server_response}"
        raise RuntimeError(msg) from e


DOMAIN_NAMES = os.getenv("DOMAIN_NAMES", get_conf("DOMAIN_NAMES"))
if DOMAIN_NAMES is not None:
    DOMAIN_NAMES = [n.strip() for n in DOMAIN_NAMES.split()]
    print("Will update domains:")
    for name in DOMAIN_NAMES:
        print("  ", name)
else:
    raise RuntimeError("DOMAIN_NAMES need to be set.")


def update_dns_A_record(domain, dry_run=False):
    """Update DNS A record."""
    result = json.loads(request_api(f"/v4/domains/{domain}/records"))
    a_rec = None
    for record in result['records']:
        if record['type'] == "A":
            a_rec = record
            break
    if a_rec is None:
        # need to create new entry
        new_record = {
            "host": "@",
            "type": "A",
            "answer": get_ip_address(),
            "ttl": 300
        }
        if not dry_run:
            request_api(f"/v4/domains/{domain}/records",
                        method="POST",
                        data=json.dumps(new_record))
            return True
        else:
            pprint(new_record)
    else:
        # update the record
        ip_address = get_ip_address()
        if ip_address == a_rec["answer"]:
            return True
        update_record = {"type": "A", "answer": ip_address}
        if not dry_run:
            result = request_api(f"/v4/domains/{domain}/records/{a_rec['id']}",
                                 method="PUT",
                                 data=json.dumps(update_record))
            return result
        else:
            print(f"id -> {a_rec['id']}")
            pprint(update_record)


if __name__ == "__main__":
    while True:
        try:
            for domain in DOMAIN_NAMES:
                update_dns_A_record(domain)
        except Exception as e:
            print(e)
        sys.stdout.flush()
        time.sleep(INTERVAL_MINUTES * 60)
