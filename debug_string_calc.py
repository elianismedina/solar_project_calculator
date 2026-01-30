import os
import django
import math

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_project.settings')
django.setup()

from design.models import Project

def debug_calculation():
    print("\n--- DEBUGGING STRING LAYOUT ---")
    
    # Get the project and components (assuming there is at least one)
    project = Project.objects.first()
    if not project:
        print("No projects found.")
        return

    array = project.projectpanelarray_set.first()
    block = project.projectinverterblock_set.first()

    if not array or not block:
        print("Missing components.")
        return

    pan = array.panel
    inv = block.inverter
    
    print(f"Panel: {pan.manufacturer} {pan.model_name}")
    print(f"  Voc: {pan.voc} V")
    print(f"  Vmpp: {pan.vmpp} V")
    print(f"  Isc: {pan.isc} A")
    print(f"  Coeff Voc: {pan.temp_coeff_voc} %/C")
    
    print(f"\nInverter: {inv.manufacturer} {inv.model_name}")
    print(f"  Vdc Max: {inv.pv_max_input_voltage} V")
    print(f"  Vmppt Min: {inv.pv_dc_voltage_nominal} V")
    print(f"  I Limit: {inv.pv_max_input_current or inv.pv_max_charge_current} A")

    # Parameters
    num_modulos = array.quantity
    t_min = -10
    t_stc = 25
    
    # Logic from services.py
    coeff_voc_abs = abs(pan.temp_coeff_voc / 100) if pan.temp_coeff_voc else 0.003
    voc_frio = pan.voc * (1 + coeff_voc_abs * (t_stc - t_min))
    isc_safety = pan.isc * 1.25
    vmppt_min = inv.pv_dc_voltage_nominal
    vdc_max = inv.pv_max_input_voltage
    i_limit = inv.pv_max_input_current or inv.pv_max_charge_current or 50.0

    print(f"\n--- CALCULATED PARAMETERS ---")
    print(f"Voc_cold ({t_min}C): {voc_frio:.2f} V")
    print(f"Isc_safety (x1.25): {isc_safety:.2f} A")

    print(f"\n--- TESTING CONFIGURATIONS (Total {num_modulos} panels) ---")
    
    opciones = []
    for ns in range(1, num_modulos + 1):
        if num_modulos % ns == 0:
            np = num_modulos // ns
            opciones.append((ns, np))
    
    # Sort by Ns descending to see series priority
    opciones.sort(key=lambda x: x[0], reverse=True)

    for ns, np in opciones:
        print(f"\nChecking: {np} string(s) of {ns} panel(s)வுகளில்...")
        
        # Rule 1: Min Voltage
        v_string_min = ns * pan.vmpp
        pass_min_v = v_string_min >= vmppt_min
        print(f"  Rule 1 (Min V): {v_string_min:.2f}V >= {vmppt_min}V? {'PASS' if pass_min_v else 'FAIL'}")

        # Rule 2: Max Voltage
        v_string_max = ns * voc_frio
        pass_max_v = v_string_max <= vdc_max
        print(f"  Rule 2 (Max V): {v_string_max:.2f}V <= {vdc_max}V? {'PASS' if pass_max_v else 'FAIL (!!!)'}")

        # Rule 3: Max Current
        i_total = np * isc_safety
        pass_i = i_total <= i_limit
        print(f"  Rule 3 (Max I): {i_total:.2f}A <= {i_limit}A? {'PASS' if pass_i else 'FAIL'}")

        if pass_min_v and pass_max_v and pass_i:
            print("  -> RESULT: VALID")
        else:
            print("  -> RESULT: INVALID")

if __name__ == "__main__":
    debug_calculation()
