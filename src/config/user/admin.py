from django.contrib import admin
from config.user import models

class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    fields = ('name', 'slug')
admin.site.register(models.Access)
admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.RoleAccess)
admin.site.register(models.User)
admin.site.register(models.AgentPlan)
