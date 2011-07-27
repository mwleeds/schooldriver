from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType

from ajax_select import make_ajax_form
from ajax_select.fields import autoselect_fields_check_can_add
import sys
from reversion.admin import VersionAdmin

from ecwsp.sis.models import *
from ecwsp.sis.forms import *
from ecwsp.sis.views import *
from ecwsp.sis.helper_functions import ReadPermissionModelAdmin
from ecwsp.schedule.models import *

# Global actions
def export_simple_selected_objects(modeladmin, request, queryset):
    selected_int = queryset.values_list('id', flat=True)
    selected = []
    for s in selected_int:
        selected.append(str(s))
    ct = ContentType.objects.get_for_model(queryset.model)
    return HttpResponseRedirect("/sis/export_to_xls/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
#    app = queryset[0]._meta.app_label
#    model = queryset[0]._meta.module_name
#    return admin_export_xls(request, app, model, queryset)
export_simple_selected_objects.short_description = "Export selected items to XLS"
admin.site.add_action(export_simple_selected_objects)

#def export_m2m_selected_objects(modeladmin, request, queryset):
#    app = queryset[0]._meta.app_label
#    model = queryset[0]._meta.module_name
#    return admin_export_xls(request, app, model, queryset, m2m=True)
#export_m2m_selected_objects.short_description = "Export selected items to XLS (extra)"
#admin.site.add_action(export_m2m_selected_objects)


def promote_to_worker(modeladmin, request, queryset):
    for object in queryset:
        object.promote_to_worker()
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )

def promote_to_sis(modeladmin, request, queryset):
    for object in queryset:
        object.promote_to_sis()
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )
        

def graduate_and_create_alumni(modeladmin, request, queryset):
    i = 0
    for object in queryset:
        object.graduate_and_create_alumni()
        LogEntry.objects.log_action(
            user_id         = request.user.pk, 
            content_type_id = ContentType.objects.get_for_model(object).pk,
            object_id       = object.pk,
            object_repr     = unicode(object), 
            action_flag     = CHANGE
        )
        i += 1
    messages.success(request, "%s students were set as graduated, marked inactive, and if installed created in the alumni app." % (i,))

def mark_inactive(modeladmin, request, queryset):
    for object in queryset:
        object.inactive=True
        LogEntry.objects.log_action(
                    user_id         = request.user.pk, 
                    content_type_id = ContentType.objects.get_for_model(object).pk,
                    object_id       = object.pk,
                    object_repr     = unicode(object), 
                    action_flag     = CHANGE
                )
        object.save()

def bulk_change(modeladmin, request, queryset):
    selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    ct = ContentType.objects.get_for_model(queryset.model)
    if ct.name == "student":
        return HttpResponseRedirect("/sis/student/bulk_change/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))
    elif ct.name == "studentattendance":
        return HttpResponseRedirect("/sis/studentattendance/bulk_change/?ct=%s&ids=%s" % (ct.pk, ",".join(selected)))

class StudentNumberInline(admin.TabularInline):
    model = StudentNumber
    extra = 1
    
    
class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContactNumber
    extra = 1
    
class TranscriptNoteInline(admin.TabularInline):
    model = TranscriptNote
    extra = 1
    
class StudentFileInline(admin.StackedInline):
    model = StudentFile
    extra = 1


class StudentHealthRecordInline(admin.StackedInline):
    model = StudentHealthRecord
    extra = 1
    
class StudentAwardInline(admin.TabularInline):
    model = AwardStudent
    extra = 0

class DisciplineActionInstanceInline(admin.TabularInline):
    model = DisciplineActionInstance
    extra = 1

class ASPHistoryInline(admin.TabularInline):
    model = ASPHistory
    extra = 1
    
class StudentCohortInline(admin.TabularInline):
    model = Student.cohorts.through
    extra = 1

class StudentECInline(admin.StackedInline):
    model = Student.emergency_contacts.through
    extra = 1

admin.site.register(GradeLevel)

class StudentAdmin(VersionAdmin, ReadPermissionModelAdmin):
    def changelist_view(self, request, extra_context=None):
        """override to hide inactive students by default"""
        try:
            test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
            if test and test[-1] and not test[-1].startswith('?') and not request.GET.has_key('inactive__exact'):
                return HttpResponseRedirect("/admin/sis/student/?inactive__exact=0")
        except: pass # In case there is no referer
        return super(StudentAdmin,self).changelist_view(request, extra_context=extra_context)

    
    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup in ('year__id__exact'):
            return True
        return super(StudentAdmin, self).lookup_allowed(lookup, *args, **kwargs)
    
    def render_change_form(self, request, context, *args, **kwargs):
        try:
            if context['original'].pic:
                txt = '<img src="' + str(context['original'].pic.url_70x65) + '"/>'
                context['adminform'].form.fields['pic'].help_text += txt
        except:
            print >> sys.stderr, "Error in StudentAdmin render_change_form"
        
        return super(StudentAdmin, self).render_change_form(request, context, args, kwargs)
    
    def change_view(self, request, object_id, extra_context=None):
        courses = Course.objects.filter(courseenrollment__user__id=object_id, marking_period__school_year__active_year=True).distinct()
        for course in courses:
            course.enroll = course.courseenrollment_set.get(user__id=object_id).id
        other_courses = Course.objects.filter(courseenrollment__user__id=object_id, marking_period__school_year__active_year=False).distinct()
        for course in other_courses:
            course.enroll = course.courseenrollment_set.get(user__id=object_id).id
        my_context = {
            'courses': courses,
            'other_courses': other_courses,
        }
        return super(StudentAdmin, self).change_view(request, object_id, extra_context=my_context)
        
    def get_form(self, request, obj=None, **kwargs):
        form = super(StudentAdmin,self).get_form(request,obj,**kwargs)
        autoselect_fields_check_can_add(StudentForm, self.model ,request.user)
        if not request.user.has_perm('sis.view_ssn_student'):
            self.exclude = ("ssn",)
        return form
        
    form = StudentForm
    search_fields = ['fname', 'lname', 'username', 'unique_id', 'street', 'state', 'zip', 'id']
    inlines = [StudentNumberInline, StudentCohortInline, StudentFileInline, StudentHealthRecordInline, TranscriptNoteInline, StudentAwardInline, ASPHistoryInline]
    actions = [promote_to_worker, mark_inactive, graduate_and_create_alumni, bulk_change]
    list_filter = ['inactive','year']
    list_display = ['__unicode__','year']
admin.site.register(Student, StudentAdmin)


class EmergencyContactAdmin(admin.ModelAdmin):
    inlines = [EmergencyContactInline, StudentECInline]
    search_fields = ['fname', 'lname', 'email', 'student__fname', 'student__lname']
admin.site.register(EmergencyContact, EmergencyContactAdmin)


class MdlUserAdmin(admin.ModelAdmin):
    actions = [promote_to_sis]
admin.site.register(MdlUser, MdlUserAdmin)


class StudentDisciplineAdmin(admin.ModelAdmin):
    form = make_ajax_form(StudentDiscipline, dict(students='discstudent'))

    list_per_page = 50
    fields = ['date', 'students', 'teacher', 'infraction', 'comments']
    list_display = ('show_students', 'date', 'comment_Brief', 'infraction')
    list_filter = ['date', 'infraction', 'action',]
    search_fields = ['comments', 'students__fname', 'students__lname']
    inlines = [DisciplineActionInstanceInline]

admin.site.register(StudentDiscipline, StudentDisciplineAdmin)
admin.site.register(DisciplineAction)

class CohortAdmin(admin.ModelAdmin):
    filter_horizontal = ('students',)
    
    def save_model(self, request, obj, form, change):
        if obj.id:
            prev_students = Cohort.objects.get(id=obj.id).students.all()
        else:
            prev_students = Student.objects.none()
            
        # Django is retarded about querysets,
        # save these ids because the queryset will just change later
        student_ids = []
        for student in prev_students:
            student_ids.append(student.id)
        
        super(CohortAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        
        for student in obj.students.all() | Student.objects.filter(id__in=student_ids):
            student.cache_cohorts()
            student.save()
    
admin.site.register(Cohort, CohortAdmin)

class StudentAttendanceAdmin(admin.ModelAdmin):
    form = make_ajax_form(StudentAttendance, dict(student='attendance_quick_view_student'))
    list_display = ['student', 'date', 'status', 'notes']
    list_filter = ['date', 'status']
    list_editable = ['status', 'notes']
    search_fields = ['student__fname', 'student__lname', 'notes', 'status__name']
    actions = [bulk_change]
admin.site.register(StudentAttendance, StudentAttendanceAdmin)

class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'excused', 'absent', 'tardy']
admin.site.register(AttendanceStatus,AttendanceStatusAdmin)
admin.site.register(ReasonLeft)
admin.site.register(ReportField)

admin.site.register(TranscriptNoteChoices)

if settings.ASP:
    class ASPAttendanceAdmin(admin.ModelAdmin):
        list_display = ['student', 'status', 'date', 'course', 'notes']
    admin.site.register(ASPAttendance, ASPAttendanceAdmin)