from maximo_sim.modules.work_management import new_work_order

wo = new_work_order(
    "3002",
    "",
    worktype = "PM"
)


description = ""

if description :
    print(PASS)
else : 
    print("FAIL - Description Required")