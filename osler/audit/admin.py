from __future__ import unicode_literals
from django.contrib import admin

from .models import PageviewRecord


class PageviewRecordAdmin(admin.ModelAdmin):
    """
    ModelAdmin class that prevents modifications through the admin.
    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.
    Source: https://gist.github.com/aaugustin/1388243
    """
    actions = None

    list_filter = (
        'status_code',
        'role'
    )

    list_display = (
        'method',
        'status_code',
        'user',
        'role',
        'user_ip',
        'url',
        'timestamp',
    )

    search_fields = (
        'user__username', 'user__first_name', 'user__last_name', 'user__email',
        'url', 'role__short_name'
    )

    # change_list_template = 'admin/pageview-log-summary.html'
    # date_hierarchy = 'timestamp'

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we  assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    # Allow viewing objects but not actually changing them.
    def has_change_permission(self, request, obj=None):
        return (request.method in ['GET', 'HEAD'] and
                super(admin.ModelAdmin, self).has_change_permission(
                    request, obj))

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(PageviewRecord, PageviewRecordAdmin)
