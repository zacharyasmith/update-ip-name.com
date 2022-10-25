# Name.com DNS Updater

This script allows a user to update the Name.com DNS A record at a specified interval
to always match your public facing IP address. This is similar to how DuckDNS does
their auto-updating.

# Configuration

To run, set the following environment variables.

| Name                    | Required | Description                 | Default |
|-------------------------|----------|-----------------------------|---------|
| `UPDATE_INTERVAL_HOURS` | N        | Wait time before updating.  | 12      |
| `NAME_COM_USERNAME`     | Y        | Username at name.com        | -       |
| `PROD_TOKEN`            | Y        | Token supplied by name.com  | -       |
| `DOMAIN_NAMES`          | Y        | Space separated (no `www.`) | -       |

Get your token at `https://www.name.com/account/settings/api`

