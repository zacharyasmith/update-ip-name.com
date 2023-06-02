"""Test suite for get_ip_address stuff."""

import update_dns_ip as mod
import re
import json
from pprint import pprint


def test_get_ip_address():
    ip_address = mod.get_ip_address()
    assert ip_address != ""
    print(ip_address)
    assert re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",
                    ip_address)


def test_get_conf():
    print(mod.get_conf("TEST_TOKEN"))
    print(mod.get_conf("PROD_TOKEN"))


def test_request_api():
    for domain in mod.DOMAIN_NAMES:
        print(f"{domain:-^30}")
        result = mod.request_api(f"/v4/domains/{domain}/records")
        pprint(json.loads(result))


def test_update_A_rec():
    for domain in mod.DOMAIN_NAMES:
        mod.update_dns_A_record(domain, dry_run=True)
