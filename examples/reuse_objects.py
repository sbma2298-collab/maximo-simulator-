from maximo_sim.modules.work_management import new_work_order

wo = new_work_order(
     "2001"
     "Pump Inspection"
     worktype = "PM"
)

print("Before")

print(wo)

wo.set_value("STATUS","APPR")

print("After Approval")

print(wo)

wo.set_value("STATUS","COMP")

print("After Completion")

print(wo)