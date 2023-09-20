from wallets.settings import REDIS

address = REDIS.get("xrp_address_list")
print(address)