#!/bin/bash

KEY="1A9kcWiX3cL1b4KF31lngAJL4dIDusoqfe88rFfQ"

curl -X POST "https://api.nal.usda.gov/fdc/v1/foods/search/?api_key=$KEY" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{\"query\":\"Cheddar cheese\",\"dataType\":\"Foundation,SR Legacy\",\"pageSize\":25,\"pageNumber\":2,\"sortBy\":\"dataType.keyword\",\"sortOrder\":\"asc\",\"brandOwner\":\"Kar Nut Products Company\"}"
