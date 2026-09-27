#!/bin/sh
# usage: run_capped.sh <seconds> <logfile> args...   (wall-time cap via perl alarm; nice'd)
secs=$1; log=$2; shift 2
exec nice perl -e 'alarm shift; exec @ARGV' "$secs" python3 c2b_validate.py "$@" > "$log" 2>&1
