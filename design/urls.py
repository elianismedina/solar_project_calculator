from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_edit'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project_delete'),
    path('<int:pk>/settings/', views.ProjectSettingsUpdateView.as_view(), name='project_settings'),
    path('<int:pk>/settings/fetch-hsp/', views.fetch_hsp_view, name='project_settings_fetch_hsp'),
    path('<int:pk>/consumption/', views.ProjectConsumptionUpdateView.as_view(), name='project_consumption'),
    path('<int:pk>/calculate/', views.run_calculation_view, name='project_calculate'),
    path('<int:project_pk>/panels/add/', views.ProjectPanelArrayCreateView.as_view(), name='project_panel_add'),
    path('<int:project_pk>/inverters/add/', views.ProjectInverterBlockCreateView.as_view(), name='project_inverter_add'),
    path('<int:project_pk>/batteries/add/', views.ProjectBatteryBankCreateView.as_view(), name='project_battery_add'),
    
    # Panel Catalog URLs
    path('panels/', views.PanelListView.as_view(), name='panel_list'),
    path('panels/new/', views.PanelCreateView.as_view(), name='panel_create'),
    path('panels/<int:pk>/edit/', views.PanelUpdateView.as_view(), name='panel_edit'),
    path('panels/<int:pk>/delete/', views.PanelDeleteView.as_view(), name='panel_delete'),
    
    # Inverter Catalog URLs
    path('inverters/', views.InverterListView.as_view(), name='inverter_list'),
    path('inverters/new/', views.InverterCreateView.as_view(), name='inverter_create'),
    path('inverters/<int:pk>/edit/', views.InverterUpdateView.as_view(), name='inverter_edit'),
    path('inverters/<int:pk>/delete/', views.InverterDeleteView.as_view(), name='inverter_delete'),

    # Battery Catalog URLs
    path('batteries/', views.BatteryListView.as_view(), name='battery_list'),
    path('batteries/new/', views.BatteryCreateView.as_view(), name='battery_create'),
    path('batteries/<int:pk>/edit/', views.BatteryUpdateView.as_view(), name='battery_edit'),
    path('batteries/<int:pk>/delete/', views.BatteryDeleteView.as_view(), name='battery_delete'),
    
    # Project Component Removal
    path('project-panel/<int:pk>/delete/', views.ProjectPanelArrayDeleteView.as_view(), name='project_panel_delete'),
    path('project-inverter/<int:pk>/delete/', views.ProjectInverterBlockDeleteView.as_view(), name='project_inverter_delete'),
    path('project-battery/<int:pk>/delete/', views.ProjectBatteryBankDeleteView.as_view(), name='project_battery_delete'),
]
