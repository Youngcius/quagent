"""
Utils functions processing iLab API
"""
import requests
import json
from pprint import pprint

# zhy's client ID and token
cid = '/M8BJdb/scEfeqmpf0l9qw=='
token = 'zdgtQF4ohVe64CfcA9XJTbDdxmRCGpR+S0Pmd2y4OdSotBK+p74mZoFVyV6Hm4pD+Fyumfr44bPuqJ2ZqHeGGw=='
facility_id = 5807  # facility ID of INQUIRE

core_url = 'https://api.ilabsolutions.com/v1/cores'
ilab_urls = {
    'service': core_url + '/{}/services.json'.format(facility_id),
    'equipment': core_url + '/{}/equipment.json'.format(facility_id),
    'request': core_url + '/{}/service_requests.json'.format(facility_id),
    'price': core_url + '/{}/price_types.json'.format(facility_id)
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
    'Content-Type': 'application/json',
    'Authorization': 'bearer {}'.format(token)
}

resp = {
    "ilab_response": {
        "ilab_metadata": {
            "authorization": "This is the root of Version 1 of the iLab Solutions API, but you don't seem to have access to any resources. Please contact iLab for assistance."
        }
    }
}
