"""Update DNS entry with public IP."""

import urllib.request
import os
from pathlib import Path
import configparser
from pprint import pprint
import json
import time
import sys

INTERVAL_MINUTES = int(os.getenv("UPDATE_INTERVAL_MINUTES", "15"))

BASE_DEV_API = "https://api.cloudflare.com/client"
BASE_API = "https://api.cloudflare.com/client"

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


TOKEN = os.getenv("TOKEN", get_conf("TOKEN"))
ZONE_IDS = os.getenv("ZONE_IDS", get_conf("ZONE_IDS"))


def get_ip_address():
    """Get the IP address."""
    with urllib.request.urlopen('https://checkip.amazonaws.com/') as f:
        return f.read(30).decode('UTF-8').strip()


def request_api(path, development=False, method="GET", data=None):
    """Return result of request."""
    base = BASE_API if not development else BASE_DEV_API
    if data:
        data = data.encode("utf-8")
    print(f"{method} {path} -- {data}")
    req = urllib.request.Request(f"{base}{path}", method=method, data=data)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as f:
            return f.read().decode(encoding='utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        server_response = e.read().decode('utf-8')
        server_response = json.loads(server_response)
        msg = f"{e}\n{server_response}"
        raise RuntimeError(msg) from e


ZONES = []
if ZONE_IDS is not None:
    ZONE_IDS = [n.strip() for n in ZONE_IDS.split()]
    print("Will update domains:")
    for zone_id in ZONE_IDS:
        ZONES.append(zone_id.split(","))
        print("  ", zone_id)
else:
    raise RuntimeError("ZONE_IDS need to be set.")


def update_dns_A_record(zone, dry_run=False):
    """Update DNS A record."""
    zone_id, domain = zone
    result = json.loads(request_api(f"/v4/zones/{zone_id}/dns_records"))
    a_rec = None
    for record in result['result']:
        if record['type'] == "A" and record['name'] == domain:
            a_rec = record
            break
    if a_rec is None:
        # need to create new entry
        new_record = {
            "name": domain,
            "type": "A",
            "content": get_ip_address()
        }
        if not dry_run:
            request_api(f"/v4/zones/{zone_id}/dns_records",
                        method="POST",
                        data=json.dumps(new_record))
            return True
        else:
            pprint(new_record)
    else:
        # update the record
        ip_address = get_ip_address()
        if ip_address == a_rec["content"]:
            return True
        update_record = {"type": "A", "content": ip_address, "name": domain}
        if not dry_run:
            result = request_api(
                f"/v4/zones/{zone_id}/dns_records/{a_rec['id']}",
                method="PATCH",
                data=json.dumps(update_record))
            return result
        else:
            print(f"id -> {a_rec['id']}")
            pprint(update_record)


if __name__ == "__main__":
    while True:
        try:
            for zone in ZONES:
                update_dns_A_record(zone)
        except Exception as e:
            print(e)
        sys.stdout.flush()
        time.sleep(INTERVAL_MINUTES * 60)
