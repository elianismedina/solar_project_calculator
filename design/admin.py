from django.contrib import admin
from .models import (
    Project, ProjectSettings, Panel, Inverter, Battery,
    ProjectPanelArray, ProjectInverterBlock, ProjectBatteryBank, Report
)

class ProjectSettingsInline(admin.StackedInline):
    model = ProjectSettings
    can_delete = False
    verbose_name_plural = 'Settings'

class ProjectPanelArrayInline(admin.TabularInline):
    model = ProjectPanelArray
    extra = 1

class ProjectInverterBlockInline(admin.TabularInline):
    model = ProjectInverterBlock
    extra = 1

class ProjectBatteryBankInline(admin.TabularInline):
    model = ProjectBatteryBank
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    inlines = [ProjectSettingsInline, ProjectPanelArrayInline, ProjectInverterBlockInline, ProjectBatteryBankInline]

@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model_name', 'pmax', 'voc', 'isc', 'efficiency')
    search_fields = ('manufacturer', 'model_name')
    fieldsets = (
        ('General', {
            'fields': ('manufacturer', 'model_name')
        }),
        ('Electrical Parameters', {
            'fields': ('pmax', 'voc', 'isc', 'vmpp', 'impp', 'efficiency')
        }),
        ('Mechanical Characteristics', {
            'fields': ('length_mm', 'width_mm', 'thickness_mm', 'weight_kg')
        }),
    )

@admin.register(Inverter)
class InverterAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model_name', 'rated_power_watts', 'inverter_type', 'battery_voltage_nominal')
    list_filter = ('inverter_type', 'battery_voltage_nominal')
    search_fields = ('manufacturer', 'model_name')
    fieldsets = (
        ('General', {
            'fields': ('manufacturer', 'model_name', 'inverter_type')
        }),
        ('Inverter Output', {
            'fields': ('rated_power_watts', 'surge_rating_watts', 'motor_start_hp')
        }),
        ('Battery Settings', {
            'fields': ('battery_voltage_nominal',)
        }),
        ('AC Input Mode', {
            'fields': ('ac_nominal_voltage', 'ac_max_voltage', 'ac_input_frequency', 'ac_efficiency')
        }),
        ('Solar Charger', {
            'fields': ('pv_max_power_watts', 'pv_max_charge_current', 'pv_dc_voltage_nominal', 'pv_max_input_voltage', 'pv_max_efficiency')
        }),
        ('Charge Mode', {
            'fields': ('max_charge_current_total',)
        }),
        ('Dimensions', {
            'fields': ('width_mm', 'height_mm', 'depth_mm')
        }),
    )

@admin.register(Battery)
class BatteryAdmin(admin.ModelAdmin):
    list_display = ('manufacturer', 'model_name', 'nominal_voltage', 'nominal_capacity_ah', 'nominal_energy_wh')
    search_fields = ('manufacturer', 'model_name')
    fieldsets = (
        ('General', {
            'fields': ('manufacturer', 'model_name', 'chemistry', 'warranty_years')
        }),
        ('Electrical Parameters', {
            'fields': ('nominal_voltage', 'nominal_capacity_ah', 'nominal_energy_wh')
        }),
        ('Performance & Charging', {
            'fields': ('life_cycles', 'rec_charge_voltage', 'rec_charge_current', 'end_of_discharge_voltage')
        }),
        ('Dimensions & Weight', {
            'fields': ('width_mm', 'height_mm', 'depth_mm', 'weight_kg')
        }),
    )

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'created_at')
    list_filter = ('created_at', 'project')

# Registering intermediate models is optional if they are inlines, but good for direct access if needed
admin.site.register(ProjectPanelArray)
admin.site.register(ProjectInverterBlock)
admin.site.register(ProjectBatteryBank)