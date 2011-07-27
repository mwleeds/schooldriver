from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.safestring import mark_safe
from django.contrib.localflavor.us.forms import *
from django.conf import settings

from ecwsp.schedule.models import *
from ecwsp.sis.models import *
from ecwsp.sis.forms import *

from decimal import Decimal
from datetime import datetime, date

class EnrollForm(forms.Form):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.filter(inactive=False), widget=FilteredSelectMultiple("Students",False,attrs={'rows':'10'}), required=False)
    cohorts = forms.ModelMultipleChoiceField(queryset=Cohort.objects.all(), required=False)

class MarkingPeriodSelectForm(forms.Form):
    marking_period = forms.ModelChoiceField(queryset=MarkingPeriod.objects.filter(active=True))

class EngradeSyncForm(MarkingPeriodSelectForm):
    include_comments = forms.BooleanField(required=False)
    
class GradeUpload(UploadFileForm, MarkingPeriodSelectForm):
    pass
    
class GradeFilterForm(TimeBasedForm):
    marking_period = forms.ModelMultipleChoiceField(required=False, queryset=MarkingPeriod.objects.all())
    final = forms.BooleanField(required=False)
    each_marking_period = forms.BooleanField(required=False)
    mid_mark = forms.BooleanField(required=False)
    grade = forms.CharField(max_length=5,
                            widget=forms.TextInput(attrs={'placeholder': 'Enter Grade Here'}),
                            required=False,
                            help_text="P counts as 100%, F counts as 0%",)
    filter_choices = (
        ("lt", "Less Than"),
        ("lte", "Less Than Equals"),
        ("gt", "Greater Than"),
        ("gte", "Greater Than Equals"),
    )
    filter = forms.ChoiceField(choices=filter_choices)
    filter_times = forms.CharField(max_length=2, required=False, initial="*", widget=forms.TextInput(attrs={'style':'width:20px;'}))
    filter_year = forms.ModelMultipleChoiceField(required=False, queryset=GradeLevel.objects.all())
    currently_in_asp = forms.BooleanField(required=False)
    in_individual_education_program = forms.BooleanField(required=False)
    #disc
    filter_disc_action = forms.ModelChoiceField(required=False, queryset=DisciplineAction.objects.all())
    filter_disc = forms.ChoiceField(choices=filter_choices, required=False)
    filter_disc_times = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={'style':'width:20px;'}))
    #attn
    filter_attn = forms.ChoiceField(choices=filter_choices, required=False)
    filter_attn_times = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs={'style':'width:20px;'}))
    
    
class CourseBulkChangeForm(forms.Form):
    active = forms.NullBooleanField(required=False)
    teacher = forms.ModelChoiceField(queryset=Faculty.objects.filter(teacher=True), required=False)
    homeroom = forms.NullBooleanField(required=False)
    asp = forms.NullBooleanField(required=False)
    active = forms.NullBooleanField(required=False)
    credits = forms.DecimalField(required=False, max_digits=5, decimal_places=2)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)
    level = forms.ModelChoiceField(queryset=GradeLevel.objects.all(), required=False)
    marking_period = forms.ModelMultipleChoiceField(queryset=MarkingPeriod.objects.all(), required=False)
    
class CourseSelectionForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.filter(marking_period__school_year__active_year=True).distinct(), required=False)