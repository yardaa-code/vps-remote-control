#!/bin/bash
# Noční restart Claude Remote Control: paměť Claude s délkou běhu roste.
# Ukončí screen "claude", služba claude-remote ho do 20 s spustí znovu.
screen -S claude -X quit
