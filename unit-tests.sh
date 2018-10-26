#!/bin/sh
export NOSE_VERBOSE=2
export NOSE_WITH_COVERAGE=1
export NOSE_COVER_MIN_PERCENTAGE=50

python3 -m nose --cover-erase
