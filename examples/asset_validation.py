from maximo_sim.modules.work_management import new_work_order

wo = new_work_order(
    "2001",
    "Inspect Boiler B-100",
    worktype="PM"
)

wo.set_value("STATUS","APPR")

print(wo)

wo.set_value("STATUS","COMP")

print(wo)