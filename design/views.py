from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Project, ProjectSettings, ProjectPanelArray, Panel, Inverter, ProjectInverterBlock, Battery, ProjectBatteryBank
from .forms import (
    ProjectForm, ProjectSettingsForm, ProjectPanelArrayForm, PanelForm, 
    InverterForm, ProjectInverterBlockForm, BatteryForm, ProjectBatteryBankForm,
    ConsumptionFormSet
)
from .services import calculate_project_energy

class ProjectListView(ListView):
    model = Project
    template_name = 'design/project_list.html'
    context_object_name = 'projects'

class InverterListView(ListView):
    model = Inverter
    template_name = 'design/inverter_list.html'
    context_object_name = 'inverters'

class InverterCreateView(CreateView):
    model = Inverter
    form_class = InverterForm
    template_name = 'design/inverter_form.html'
    success_url = reverse_lazy('inverter_list')

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'design/project_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Create default settings for the new project
        ProjectSettings.objects.create(project=self.object, latitude=0, longitude=0)
        # Initialize 6 months of consumption
        months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]
        from .models import MonthlyConsumption
        for i, m in enumerate(months):
            MonthlyConsumption.objects.create(project=self.object, month_index=i+1, month_name=m, kwh_value=0)
        return response

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})

class ProjectConsumptionUpdateView(UpdateView):
    model = Project
    template_name = 'design/project_consumption_form.html'
    fields = [] # We use the formset instead

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Ensure 6 months exist
        existing_count = self.object.consumptions.count()
        if existing_count < 6:
            from .models import MonthlyConsumption
            for i in range(existing_count + 1, 7):
                MonthlyConsumption.objects.create(
                    project=self.object, 
                    month_index=i, 
                    month_name=f"Month {i}", 
                    kwh_value=0
                )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['consumption_formset'] = ConsumptionFormSet(self.request.POST, instance=self.object)
        else:
            context['consumption_formset'] = ConsumptionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['consumption_formset']
        if formset.is_valid():
            formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'design/project_form.html'

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.pk})

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'design/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'design/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Auto-fetch location if missing
        if not project.settings.location_name and (project.settings.latitude != 0 or project.settings.longitude != 0):
            from .services import get_location_name
            project.settings.location_name = get_location_name(project.settings.latitude, project.settings.longitude)
            project.settings.save()

        context['panel_arrays'] = project.projectpanelarray_set.all()
        context['inverter_blocks'] = project.projectinverterblock_set.all()
        context['battery_banks'] = project.projectbatterybank_set.all()
        return context

class ProjectSettingsUpdateView(UpdateView):
    model = ProjectSettings
    form_class = ProjectSettingsForm
    template_name = 'design/project_settings_form.html'

    def get_object(self, queryset=None):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return project.settings

    def form_valid(self, form):
        # Fetch location name before saving
        from .services import get_location_name
        lat = form.cleaned_data.get('latitude')
        lon = form.cleaned_data.get('longitude')
        form.instance.location_name = get_location_name(lat, lon)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.kwargs['pk']})

class ProjectPanelArrayCreateView(CreateView):
    model = ProjectPanelArray
    form_class = ProjectPanelArrayForm
    template_name = 'design/project_panel_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        form.instance.project = project
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.kwargs['project_pk']})

class ProjectInverterBlockCreateView(CreateView):
    model = ProjectInverterBlock
    form_class = ProjectInverterBlockForm
    template_name = 'design/project_inverter_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        form.instance.project = project
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.kwargs['project_pk']})

class BatteryListView(ListView):
    model = Battery
    template_name = 'design/battery_list.html'
    context_object_name = 'batteries'

class BatteryCreateView(CreateView):
    model = Battery
    form_class = BatteryForm
    template_name = 'design/battery_form.html'
    success_url = reverse_lazy('battery_list')

class ProjectBatteryBankCreateView(CreateView):
    model = ProjectBatteryBank
    form_class = ProjectBatteryBankForm
    template_name = 'design/project_battery_form.html'

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        form.instance.project = project
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        return context

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.kwargs['project_pk']})

class ProjectBatteryBankDeleteView(DeleteView):
    model = ProjectBatteryBank
    template_name = 'design/project_component_confirm_delete.html'

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.project.pk})

class ProjectPanelArrayDeleteView(DeleteView):
    model = ProjectPanelArray
    template_name = 'design/project_component_confirm_delete.html'

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.project.pk})

class ProjectInverterBlockDeleteView(DeleteView):
    model = ProjectInverterBlock
    template_name = 'design/project_component_confirm_delete.html'

    def get_success_url(self):
        return reverse('project_detail', kwargs={'pk': self.object.project.pk})

class PanelUpdateView(UpdateView):
    model = Panel
    form_class = PanelForm
    template_name = 'design/panel_form.html'
    success_url = reverse_lazy('panel_list')

class PanelDeleteView(DeleteView):
    model = Panel
    template_name = 'design/catalog_confirm_delete.html'
    success_url = reverse_lazy('panel_list')

class InverterUpdateView(UpdateView):
    model = Inverter
    form_class = InverterForm
    template_name = 'design/inverter_form.html'
    success_url = reverse_lazy('inverter_list')

class InverterDeleteView(DeleteView):
    model = Inverter
    template_name = 'design/catalog_confirm_delete.html'
    success_url = reverse_lazy('inverter_list')

class BatteryUpdateView(UpdateView):
    model = Battery
    form_class = BatteryForm
    template_name = 'design/battery_form.html'
    success_url = reverse_lazy('battery_list')

class BatteryDeleteView(DeleteView):
    model = Battery
    template_name = 'design/catalog_confirm_delete.html'
    success_url = reverse_lazy('battery_list')

class PanelListView(ListView):
    model = Panel
    template_name = 'design/panel_list.html'
    context_object_name = 'panels'

class PanelCreateView(CreateView):

    model = Panel

    form_class = PanelForm

    template_name = 'design/panel_form.html'

    success_url = reverse_lazy('panel_list')



def run_calculation_view(request, pk):

    project = get_object_or_404(Project, pk=pk)

    results = calculate_project_energy(pk)

    return render(request, 'design/calculation_results.html', {

        'project': project,

        'results': results

    })
