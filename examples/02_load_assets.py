from datetime import datetime

assets = []

for i in range(1, 51):
    assets.append(
        {
            "ASSETNUM": f"A{i:04}",
            "DESCRIPTION": f"Pump {i}",
            "STATUS": "OPERATING",
            "SITEID": "BEDFORD",
            "LOCATION": f"PLANT-{(i % 10) + 1}",
            "CHANGEDATE": datetime.utcnow(),
        }
    )

print(f"Loaded {len(assets)} assets")

for asset in assets[:5]:
    print(asset)