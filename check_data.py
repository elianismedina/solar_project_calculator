import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_project.settings')
django.setup()

from design.models import Project

def check():
    print("--- INVERTER CURRENT FIELDS ---")
    for p in Project.objects.all():
        for block in p.projectinverterblock_set.all():
            inv = block.inverter
            print(f"Inverter: {inv.model_name}")
            print(f"  pv_max_input_current: {inv.pv_max_input_current}")
            print(f"  pv_max_charge_current: {inv.pv_max_charge_current}")
            print(f"  max_charge_current_total: {inv.max_charge_current_total}")

if __name__ == "__main__":
    check()