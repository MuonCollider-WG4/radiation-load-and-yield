#!/bin/bash
python ../fill_json.py fluka_run *99
python ../emittance_calculator.py
