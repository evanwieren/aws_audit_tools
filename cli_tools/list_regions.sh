#!/bin/bash

aws ec2 describe-regions --query 'Regions[].{Name:RegionName}' --output text
