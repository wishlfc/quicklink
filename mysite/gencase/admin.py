# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
# from django.contrib.admin import AdminSite
# from gencase.models import Testlinetopo
# # Register your models here.
# # from dbview.pet_class import PetAdmin
# # class TblrealueAdmin(admin.ModelAdmin):
# class TAAdminSite(AdminSite):
#     site_header = 'QL Data Configuration'
#     site_header = ' '
#     site_title = '  Quick Link'
#     index_title = 'QL TA Data Configuration'
#     index_title = ''

# admin_site = TAAdminSite(name='QLAdmin')

# class PetAdmin(admin.ModelAdmin):
#     change_list_template = 'admin/base_c.html'
#     change_form_template = 'admin/change_form_c.html'

#     actions = None

#     def Actions(self, obj):
#         model_class_name = type(obj).__name__
#         add_url = "'/dbview/%s/add/'" % (model_class_name.lower().replace('model', ''))
#         url = '<span> <input type="button" value="Add..."  onclick="location.href=%s"/> </span>' % (add_url)
#         url += '<span> <input type="button" value="Delete"  onclick="location.href=\'%s/delete/\'" /> </span>' % (obj.pk)
#         return url
#     Actions.short_description = 'Actions'
#     Actions.allow_tags = True

#     def get_model_perms(self, request):
#         return {}

#     def changelist_view(self, request, extra_context=None):
#         extra_context = {'title': ''}
#         return super(PetAdmin, self).changelist_view(request, extra_context=extra_context)

# class TestlinetopoAdmin(PetAdmin):
#     list_display = ('aid', 'imei', 'imsi', 'manufacturer', 'product', 'model', 'version',
#                     'proxy', 'ucid', 'fixedip')
#     list_display_links = ('aid', )
#     ordering = ('imei', )
#     search_fields = ['aid', 'imei', 'imsi', 'proxy', 'product', 'model', ]

# admin_site.register(Testlinetopo, TestlinetopoAdmin)
