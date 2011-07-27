#   Copyright 2011 David M Burke
#   Author David M Burke <dburke@cristoreyny.org>
#   
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#      
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

from django.contrib import admin

from ecwsp.omr.models import *

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    
class AnswerBankInline(admin.TabularInline):
    model = AnswerBank
    extra = 4
    
class AnswerInstanceInline(admin.TabularInline):
    model = AnswerInstance
    extra = 0

admin.site.register(MeasurementTopic)
admin.site.register(Benchmark)

class TestAdmin(admin.ModelAdmin):
    list_display = ['name', 'link_copy']
    
admin.site.register(Test, TestAdmin)

admin.site.register(QuestionGroup)

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]    
admin.site.register(Question, QuestionAdmin)

admin.site.register(ErrorType)

class AnswerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Answer, AnswerAdmin)

class TestInstanceAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'points_possible', 'points_earned', 'grade']
    inlines = [AnswerInstanceInline]
admin.site.register(TestInstance, TestInstanceAdmin)

admin.site.register(AnswerInstance)

admin.site.register(AnswerBank, AnswerAdmin)

class QuestionBankAdmin(admin.ModelAdmin):
    inlines = [AnswerBankInline]    
admin.site.register(QuestionBank,QuestionBankAdmin)

admin.site.register(Theme)