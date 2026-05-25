#!/bin/bash
set -e

BASE="/home/murilo-oliveira/CP/TICKET_BUYER"

LISBOA_ORIENTE=94-31039
PORTO_CAMPANHA=94-2006
DEPARTURE=06:45
WAIT_FOR_OPEN_TIME="--wait"
RETRY_IF_FAILS="--retry"

rm -f "$BASE/finish.png"

source "$BASE/.venv/bin/activate"

python3 "$BASE/ticket.py" "$PORTO_CAMPANHA" "$LISBOA_ORIENTE" "$DEPARTURE" "$WAIT_FOR_OPEN_TIME" $RETRY_IF_FAILS""

xdg-open "$BASE/finish.png"