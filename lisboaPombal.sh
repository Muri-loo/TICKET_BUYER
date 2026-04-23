#!/bin/bash

POMBAL_STATION=94-34645
SANTA_APOLONIA_STATION=94-30007
DEPARTURE_TIME=17:39
ARRIVAL_TIME=19:07

. /home/murilo-oliveira/CP/TICKET_BUYER/.venv/bin/activate
python3 /home/murilo-oliveira/CP/TICKET_BUYER/ticket.py $SANTA_APOLONIA_STATION $POMBAL_STATION $DEPARTURE $ARRIVAL > /home/murilo-oliveira/CP/TICKET_BUYER/jobStatus.txt 2>&1