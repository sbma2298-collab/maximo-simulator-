from maximo_sim import db

asset = db.asset[0]

print(asset)
print(asset["ASSETNUM"])
print(asset["DESCRIPTION"])
print(asset["STATUS"])


