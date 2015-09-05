__author__ = 'onotole'

import requests
import config

regions = ["ru", "asia", "com", "eu"]
tanks_id_list = dict.fromkeys(regions)
session = requests.Session()
# api_reqs = []


def diff(a, b):
        b = set(b)
        return [aa for aa in a if aa not in b]


for region in regions:
    REQ_GET_ALL_TANKS_ID = "https://api.wotblitz.{}/wotb/encyclopedia/vehicles/?application_id={}&fields=tank_id".\
        format(region, "demo")#config.applicationWGID)
    print(REQ_GET_ALL_TANKS_ID)
    r = session.get(REQ_GET_ALL_TANKS_ID).json()["data"].keys()
    tanks_id_list[region] = r

for region in regions:
    if region == "ru":
        continue
    print("rus vs " + region)
    print(diff(tanks_id_list["ru"], tanks_id_list[region]))
    print("\n\n")

#for req in api_reqs:





