from maximo_sim import db

print("Total Assets:", len(db.assets))

for asset in db.assets[:5]:
    print(asset)