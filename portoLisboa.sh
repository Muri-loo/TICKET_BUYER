#!/bin/bash
set -e

BASE="/home/murilo-oliveira/CP/TICKET_BUYER"

LISBOA_ORIENTE=94-31039
PORTO_CAMPANHA=94-2006
POMBAL_STATION=94-34645
DEPARTURE=17:39
WAIT_FOR_OPEN_TIME="--wait"
RETRY_IF_FAILS="--retry"

rm -f "$BASE/finish.png"

source "$BASE/.venv/bin/activate"

python3 "$BASE/ticket.py" "$LISBOA_ORIENTE" "$POMBAL_STATION" "$DEPARTURE" "$RETRY_IF_FAILS" "$WAIT_FOR_OPEN_TIME"
xdg-open "$BASE/finish.png"