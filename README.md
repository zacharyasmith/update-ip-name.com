# Cloudflare Dynamic DNS Updater

This script allows a user to update the cloudflare DNS A record at a specified interval
to always match your public facing IP address. This is similar to how DuckDNS does
their auto-updating.

Uses https://checkip.amazonaws.com to get IP address.

# Configuration

To run, set the following environment variables.

| Name                      | Required | Description                                              | Default |
|---------------------------|----------|----------------------------------------------------------|---------|
| `UPDATE_INTERVAL_MINUTES` | N        | Wait time before updating.                               | 15      |
| `TOKEN`                   | Y        | Your cloudflare API token. (Can also be in secrets.ini)  | -       |
| `ZONE_IDS`                | Y        | Space seperated DNS zones. (Can also be in secrets.ini)  | -       |


