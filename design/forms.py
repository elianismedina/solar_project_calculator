from django import forms
from .models import Project, ProjectSettings, ProjectPanelArray, ProjectInverterBlock, ProjectBatteryBank, Panel, Inverter, Battery, MonthlyConsumption

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }

class ProjectSettingsForm(forms.ModelForm):
    class Meta:
        model = ProjectSettings
        fields = ['latitude', 'longitude', 'location_name', 'tilt_angle', 'azimuth_angle', 'electricity_rate', 'autonomy_hours', 'hsp_min']
        widgets = {
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'location_name': forms.TextInput(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}),
            'tilt_angle': forms.NumberInput(attrs={'class': 'form-control'}),
            'azimuth_angle': forms.NumberInput(attrs={'class': 'form-control'}),
            'electricity_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'autonomy_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'hsp_min': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

class ProjectPanelArrayForm(forms.ModelForm):
    class Meta:
        model = ProjectPanelArray
        fields = ['panel', 'orientation']
        widgets = {
            'panel': forms.Select(attrs={'class': 'form-select'}),
            'orientation': forms.Select(attrs={'class': 'form-select'}),
        }

class ProjectInverterBlockForm(forms.ModelForm):
    class Meta:
        model = ProjectInverterBlock
        fields = ['inverter']
        widgets = {
            'inverter': forms.Select(attrs={'class': 'form-select'}),
        }

class ProjectBatteryBankForm(forms.ModelForm):
    class Meta:
        model = ProjectBatteryBank
        fields = ['battery']
        widgets = {
            'battery': forms.Select(attrs={'class': 'form-select'}),
        }

class MonthlyConsumptionForm(forms.ModelForm):
    class Meta:
        model = MonthlyConsumption
        fields = ['month_name', 'kwh_value']
        widgets = {
            'month_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., January'}),
            'kwh_value': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

ConsumptionFormSet = forms.inlineformset_factory(
    Project, MonthlyConsumption, 
    form=MonthlyConsumptionForm, 
    extra=0, can_delete=False
)

class PanelForm(forms.ModelForm):
    class Meta:
        model = Panel
        fields = [
            'manufacturer', 'model_name', 'image',
            'pmax', 'voc', 'isc', 'vmpp', 'impp', 'efficiency',
            'temp_coeff_voc', 'temp_coeff_pmax',
            'length_mm', 'width_mm', 'thickness_mm', 'weight_kg'
        ]
        widgets = {
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'pmax': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'voc': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'isc': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'vmpp': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'impp': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'efficiency': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'temp_coeff_voc': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'temp_coeff_pmax': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'length_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'width_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'thickness_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

class InverterForm(forms.ModelForm):
    class Meta:
        model = Inverter
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'inverter_type': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'rated_power_watts': forms.NumberInput(attrs={'class': 'form-control'}),
            'surge_rating_watts': forms.NumberInput(attrs={'class': 'form-control'}),
            'motor_start_hp': forms.NumberInput(attrs={'class': 'form-control'}),
            'battery_voltage_nominal': forms.Select(attrs={'class': 'form-select'}),
            'ac_nominal_voltage': forms.NumberInput(attrs={'class': 'form-control'}),
            'ac_max_voltage': forms.NumberInput(attrs={'class': 'form-control'}),
            'ac_input_frequency': forms.NumberInput(attrs={'class': 'form-control'}),
            'ac_efficiency': forms.NumberInput(attrs={'class': 'form-control'}),
            'pv_max_power_watts': forms.NumberInput(attrs={'class': 'form-control'}),
            'pv_max_input_current': forms.NumberInput(attrs={'class': 'form-control'}),
            'pv_max_charge_current': forms.NumberInput(attrs={'class': 'form-control'}),
            'pv_dc_voltage_nominal': forms.NumberInput(attrs={'class': 'form-control'}),
            'pv_max_input_voltage': forms.NumberInput(attrs={'class': 'form-control'}),
            'pv_max_efficiency': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_charge_current_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'width_mm': forms.NumberInput(attrs={'class': 'form-control'}),
            'height_mm': forms.NumberInput(attrs={'class': 'form-control'}),
            'depth_mm': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BatteryForm(forms.ModelForm):
    class Meta:
        model = Battery
        fields = '__all__'
        exclude = ['created_at']
        widgets = {
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'chemistry': forms.TextInput(attrs={'class': 'form-control'}),
            'nominal_voltage': forms.NumberInput(attrs={'class': 'form-control'}),
            'nominal_capacity_ah': forms.NumberInput(attrs={'class': 'form-control'}),
            'nominal_energy_wh': forms.NumberInput(attrs={'class': 'form-control'}),
            'life_cycles': forms.NumberInput(attrs={'class': 'form-control'}),
            'rec_charge_voltage': forms.NumberInput(attrs={'class': 'form-control'}),
            'rec_charge_current': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_of_discharge_voltage': forms.NumberInput(attrs={'class': 'form-control'}),
            'width_mm': forms.NumberInput(attrs={'class': 'form-control'}),
            'height_mm': forms.NumberInput(attrs={'class': 'form-control'}),
            'depth_mm': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'warranty_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }
