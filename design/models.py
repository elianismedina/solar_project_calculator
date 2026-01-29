from django.db import models
from django.utils import timezone

class Panel(models.Model):
    manufacturer = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    
    # Electrical Parameters
    pmax = models.FloatField(help_text="Maximum Power (Pmax) in Watts", default=0.0)
    voc = models.FloatField(help_text="Open Circuit Voltage (Voc) in Volts", default=0.0)
    isc = models.FloatField(help_text="Short Circuit Current (Isc) in Amps", default=0.0)
    vmpp = models.FloatField(help_text="Voltage at Maximum Power (Vmpp) in Volts", default=0.0)
    impp = models.FloatField(help_text="Current at Maximum Power (Impp) in Amps", default=0.0)
    efficiency = models.FloatField(help_text="Module Efficiency (%)", default=0.0)

    # Mechanical Characteristics
    length_mm = models.FloatField(help_text="Length in mm", default=0.0)
    width_mm = models.FloatField(help_text="Width in mm", default=0.0)
    thickness_mm = models.FloatField(help_text="Thickness/Depth in mm", null=True, blank=True)
    weight_kg = models.FloatField(help_text="Weight in kg", null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manufacturer} {self.model_name} ({self.pmax}W)"

class Inverter(models.Model):
    INVERTER_TYPES = [
        ('Hybrid', 'Hybrid'),
        ('Offgrid', 'Offgrid'),
    ]
    
    manufacturer = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    inverter_type = models.CharField(max_length=20, choices=INVERTER_TYPES, default='Offgrid')
    
    # Inverter Output
    rated_power_watts = models.FloatField(help_text="Rated power in Watts", default=0.0)
    surge_rating_watts = models.FloatField(help_text="Surge rating in Watts", default=0.0)
    motor_start_hp = models.FloatField(help_text="Capable of starting electric motor (HP)", default=0.0)
    
    # Battery
    battery_voltage_nominal = models.CharField(
        max_length=20, 
        choices=[('24VDC', '24VDC'), ('48VDC', '48VDC'), ('24VDC/48VDC', '24VDC/48VDC')],
        default='48VDC'
    )
    
    # AC Input Mode
    ac_nominal_voltage = models.FloatField(help_text="Nominal input voltage (V)", default=230.0)
    ac_max_voltage = models.FloatField(help_text="Max input voltage (V)", default=280.0)
    ac_input_frequency = models.FloatField(help_text="Input frequency (Hz)", default=50.0)
    ac_efficiency = models.FloatField(help_text="AC Efficiency (%)", default=0.0)
    
    # Solar Charger
    pv_max_power_watts = models.FloatField(help_text="Maximum PV array power (W)", default=0.0)
    pv_max_charge_current = models.FloatField(help_text="Maximum PV Charge current (A)", default=0.0)
    pv_dc_voltage_nominal = models.FloatField(help_text="DC voltage / MPPT Range (V)", default=0.0)
    pv_max_input_voltage = models.FloatField(help_text="Maximum solar input voltage (V)", default=0.0)
    pv_max_efficiency = models.FloatField(help_text="Maximum efficiency (%)", default=0.0)
    
    # Charge Mode
    max_charge_current_total = models.FloatField(help_text="Max charge current (A)", default=0.0)
    
    # Dimensions
    width_mm = models.FloatField(default=0.0)
    height_mm = models.FloatField(default=0.0)
    depth_mm = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manufacturer} {self.model_name} ({self.rated_power_watts}W)"

class Battery(models.Model):
    manufacturer = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    
    # Electrical Parameters
    nominal_voltage = models.FloatField(help_text="Nominal voltage (V)", default=0.0)
    nominal_capacity_ah = models.FloatField(help_text="Nominal capacity (Ah)", default=0.0)
    nominal_energy_wh = models.FloatField(help_text="Nominal energy (Wh)", default=0.0)
    
    # Performance & Charging
    life_cycles = models.PositiveIntegerField(help_text="Life Cycles (e.g. 6000)", default=0)
    rec_charge_voltage = models.FloatField(help_text="Recommended charge voltage (V)", default=0.0)
    rec_charge_current = models.FloatField(help_text="Recommended charge current (A)", default=0.0)
    end_of_discharge_voltage = models.FloatField(help_text="End of discharge voltage (V)", default=0.0)
    
    # Mechanical & Warranty
    width_mm = models.FloatField(default=0.0)
    height_mm = models.FloatField(default=0.0)
    depth_mm = models.FloatField(default=0.0)
    weight_kg = models.FloatField(default=0.0)
    warranty_years = models.PositiveIntegerField(help_text="Warranty in years", default=0)
    
    chemistry = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.manufacturer} {self.model_name} ({self.nominal_energy_wh/1000}kWh)"

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProjectSettings(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='settings')
    latitude = models.FloatField()
    longitude = models.FloatField()
    location_name = models.CharField(max_length=255, blank=True, help_text="Automatically determined from coordinates")
    tilt_angle = models.FloatField(default=0.0, help_text="Panel tilt angle in degrees")
    azimuth_angle = models.FloatField(default=180.0, help_text="Panel azimuth angle (180=South)")
    electricity_rate = models.FloatField(default=0.15, help_text="Cost per kWh")
    autonomy_hours = models.FloatField(default=8.0, help_text="Desired battery backup hours (e.g. 8.0)")

    def __str__(self):
        return f"Settings for {self.project.name}"

class MonthlyConsumption(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='consumptions')
    month_index = models.PositiveIntegerField(help_text="1 for most recent, 6 for oldest")
    month_name = models.CharField(max_length=20, help_text="e.g., January")
    kwh_value = models.FloatField(default=0.0)

    class Meta:
        ordering = ['month_index']

    def __str__(self):
        return f"{self.month_name}: {self.kwh_value} kWh"

class ProjectComponent(models.Model):
    """
    Abstract base for components added to a project (e.g. 10x Panel A).
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True

class ProjectPanelArray(ProjectComponent):
    panel = models.ForeignKey(Panel, on_delete=models.PROTECT)
    orientation = models.CharField(max_length=20, default='Portrait', choices=[('Portrait', 'Portrait'), ('Landscape', 'Landscape')])
    
    def __str__(self):
        return f"{self.quantity}x {self.panel} in {self.project.name}"

class ProjectInverterBlock(ProjectComponent):
    inverter = models.ForeignKey(Inverter, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.quantity}x {self.inverter} in {self.project.name}"

class ProjectBatteryBank(ProjectComponent):
    battery = models.ForeignKey(Battery, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.quantity}x {self.battery} in {self.project.name}"

class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    generated_content = models.TextField(help_text="JSON or text content of the report")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.project.name}"
