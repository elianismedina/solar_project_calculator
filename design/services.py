import pvlib
import pandas as pd
import math
import os
import json
from geopy.geocoders import Nominatim
from .models import Project
from openai import OpenAI

def get_location_name(latitude, longitude):
    try:
        geolocator = Nominatim(user_agent="solar_project_calc")
        location = geolocator.reverse(f"{latitude}, {longitude}", timeout=10)
        if location:
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('town') or address.get('village') or address.get('county')
            country = address.get('country')
            if city and country:
                return f"{city}, {country}"
            return location.address
    except Exception:
        pass
    return "Unknown Location"

def get_consumption_forecast(project, location_name):
    """
    Uses OpenAI to forecast 12 months of consumption based on 6 months history and climate.
    """
    history = list(project.consumptions.all().order_by('month_index').values('month_name', 'kwh_value'))
    avg_hist = sum([h['kwh_value'] for h in history]) / len(history) if history else 300
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        base = [h['kwh_value'] for h in history]
        while len(base) < 12: base.append(avg_hist)
        return base[:12]

    client = OpenAI(api_key=api_key)
    prompt = f"""
    The following is the energy consumption (kWh) of a household in {location_name} for the last 6 months:
    {json.dumps(history)}
    
    Based on the typical climate, seasons, and temperature changes in {location_name}, 
    forecast the expected monthly consumption for a full calendar year (Jan to Dec).
    Return ONLY a JSON list of 12 floats representing kWh from January to December.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        forecast = json.loads(content)
        if len(forecast) == 12:
            return [float(v) for v in forecast]
    except Exception as e:
        print(f"OpenAI Forecast Error: {e}")
    
    base = [h['kwh_value'] for h in history]
    while len(base) < 12: base.append(avg_hist)
    return base[:12]

def calculate_project_energy(project_id):
    project = Project.objects.get(pk=project_id)
    settings = project.settings
    
    # Sizing Parameters
    SAFETY_MARGIN = 1.10
    DAYS_OF_AUTONOMY = settings.autonomy_hours / 24.0
    BATTERY_DISCHARGE_LIMIT = 0.8

    avg_monthly_kwh = sum([c.kwh_value for c in project.consumptions.all()]) / 6 if project.consumptions.exists() else 0
    avg_daily_kwh = avg_monthly_kwh / 30

    # Define sets early to avoid NameErrors
    panel_arrays = project.projectpanelarray_set.all()
    inverter_blocks = project.projectinverterblock_set.all()
    battery_banks = project.projectbatterybank_set.all()

    # 1. First Pass: Sizing
    total_dc_power_watts = 0
    for array in panel_arrays:
        if avg_daily_kwh > 0:
            target_kw_total = (avg_daily_kwh * SAFETY_MARGIN) / 4.0 
            target_kw = max(0.5, target_kw_total) / max(1, panel_arrays.count())
            array.quantity = math.ceil((target_kw * 1000) / array.panel.pmax)
            array.save()
        total_dc_power_watts += (array.panel.pmax * array.quantity)

    for block in inverter_blocks:
        target_ac_watts_total = total_dc_power_watts / 1.2
        block.quantity = math.ceil((target_ac_watts_total / block.inverter.rated_power_watts) / max(1, inverter_blocks.count()))
        if block.quantity == 0: block.quantity = 1 
        block.save()

    for bank in battery_banks:
        if avg_daily_kwh > 0:
            energy_kwh_per_unit = (bank.battery.nominal_energy_wh / 1000) * BATTERY_DISCHARGE_LIMIT
            required_kwh = ((avg_daily_kwh * DAYS_OF_AUTONOMY) * SAFETY_MARGIN) / max(1, battery_banks.count())
            bank.quantity = math.ceil(required_kwh / energy_kwh_per_unit)
        else:
            bank.quantity = 1
        bank.save()

    # 2. Consumption Forecast
    location_name = settings.location_name or get_location_name(settings.latitude, settings.longitude)
    full_year_consumption = get_consumption_forecast(project, location_name)
    total_annual_consumption = sum(full_year_consumption)

    # 3. Second Pass: Monthly Simulation
    location = pvlib.location.Location(latitude=settings.latitude, longitude=settings.longitude)
    monthly_production = []
    total_annual_production = 0

    for month in range(1, 13):
        date_str = f'2026-{month:02d}-15'
        times = pd.date_range(date_str, periods=24, freq='h', tz='UTC')
        clearsky = location.get_clearsky(times)
        solar_position = location.get_solarposition(times)
        dni_extra = pvlib.irradiance.get_extra_radiation(times)
        airmass = location.get_airmass(times=times, solar_position=solar_position)
        
        month_total_yield = 0
        for array in panel_arrays:
            poa = pvlib.irradiance.get_total_irradiance(
                surface_tilt=settings.tilt_angle, surface_azimuth=settings.azimuth_angle,
                dni=clearsky['dni'], ghi=clearsky['ghi'], dhi=clearsky['dhi'],
                solar_zenith=solar_position['apparent_zenith'], solar_azimuth=solar_position['azimuth'],
                dni_extra=dni_extra, airmass=airmass['airmass_relative'], model='perez'
            )
            daily_yield = (poa['poa_global'].fillna(0) / 1000 * array.panel.pmax).sum() / 1000
            month_total_yield += (daily_yield * array.quantity * 30)
            
        monthly_production.append(round(float(month_total_yield), 2))
        total_annual_production += month_total_yield

    # 4. Results
    rate = settings.electricity_rate
    current_annual_cost = total_annual_consumption * rate
    new_annual_cost = max(0, (total_annual_consumption - total_annual_production) * rate)
    annual_savings = current_annual_cost - new_annual_cost
    
    # Inverter Logic
    total_ac_watts = sum([b.inverter.rated_power_watts * b.quantity for b in inverter_blocks])
    inverter_analysis = {}
    if total_ac_watts > 0:
        ratio = total_dc_power_watts / total_ac_watts
        total_inv_qty = sum([b.quantity for b in inverter_blocks])
        if ratio < 1.15:
            status, color = ("Spare Capacity", "info") if total_inv_qty == 1 else ("Oversized", "warning")
            note = f"Ratio {round(ratio, 2)}: Normal for single units."
        elif 1.15 <= ratio <= 1.25:
            status, color, note = ("Optimized", "success", "Ideal balance.")
        else:
            status, color, note = ("Clipping Risk", "danger", "High ratio.")
        inverter_analysis = {'ratio': round(ratio, 2), 'status': status, 'color': color, 'note': note}

    # Compatibility
    compatibility_checks = []
    if inverter_blocks.exists() and battery_banks.exists():
        main_inv = inverter_blocks.first().inverter
        main_bat = battery_banks.first().battery
        bat_qty = battery_banks.first().quantity
        v_match = False
        if "48V" in main_inv.battery_voltage_nominal and 40.0 <= main_bat.nominal_voltage <= 60.0: v_match = True
        elif str(int(main_bat.nominal_voltage)) in main_inv.battery_voltage_nominal: v_match = True

        compatibility_checks.append({'label': 'Voltage Compatibility', 'passed': v_match, 'desc': f"Inverter: {main_inv.battery_voltage_nominal}. Battery: {main_bat.nominal_voltage}V.", 'fix': "Match voltage."})
        current_safe = main_inv.max_charge_current_total <= (main_bat.rec_charge_current * bat_qty)
        compatibility_checks.append({'label': 'Charge Current Limit', 'passed': current_safe, 'desc': f"Inv: {main_inv.max_charge_current_total}A. Bank: {main_bat.rec_charge_current * bat_qty}A.", 'fix': "Adjust current."})

    system_details = []
    for array in panel_arrays:
        system_details.append({'type': 'Panel Array', 'name': str(array.panel), 'qty': array.quantity, 'metric': 'Solar Source'})
    for block in inverter_blocks:
        system_details.append({'type': 'Inverter', 'name': str(block.inverter), 'qty': block.quantity, 'metric': f"{block.inverter.rated_power_watts * block.quantity}W AC"})
    for bank in battery_banks:
        system_details.append({'type': 'Battery Bank', 'name': str(bank.battery), 'qty': bank.quantity, 'metric': f"{settings.autonomy_hours}h Backup"})

    return {
        'total_annual_kwh': round(float(total_annual_production), 2),
        'total_dc_power_kw': round(float(total_dc_power_watts / 1000), 2),
        'avg_monthly_consumption': round(float(total_annual_consumption / 12), 2),
        'financials': {
            'current_bill': round(float(current_annual_cost / 12), 2),
            'new_bill': round(float(new_annual_cost / 12), 2),
            'savings': round(float(annual_savings / 12), 2),
            'annual_savings': round(float(annual_savings), 2)
        },
        'chart_data': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'production': monthly_production,
            'consumption': [round(float(v), 2) for v in full_year_consumption]
        },
        'details': system_details,
        'inverter_analysis': inverter_analysis,
        'compatibility_checks': compatibility_checks,
        'location': location_name,
        'explanations': {
            'solar': f"Sized using a 1.2 DC/AC ratio and a {int((SAFETY_MARGIN-1)*100)}% safety margin.",
            'storage': f"Sized for {settings.autonomy_hours} hours of autonomy.",
            'forecast': "12-month consumption forecast generated based on local climate and trends."
        }
    }
