from django.contrib import admin
from .models import EPsLinks, SPDsLinks, Reservation, Laboratory


class EPsLinksAdmin(admin.ModelAdmin):
    list_display = ['lab_order', 'lab_name', 'in_ch', 'out_ch', 'linkage', 'in_use']
    list_filter = ['lab', 'in_ch', 'out_ch', 'linkage', 'in_use']
    list_per_page = 20
    ordering = ['lab', 'in_ch', 'out_ch']

    def lab_name(self, obj):
        return str(obj.lab.lab_name)

    lab_name.short_description = 'lab name'

    def lab_order(self, obj):
        return obj.lab.lab_order

    lab_order.short_description = 'lab order'


class SPDsLinksAdmin(admin.ModelAdmin):
    list_display = ['lab_order', 'lab_name', 'in_ch', 'out_ch', 'linkage', 'in_use']
    list_filter = ['lab', 'in_ch', 'out_ch', 'linkage', 'in_use']
    list_per_page = 16
    ordering = ['lab', 'in_ch', 'out_ch']

    def lab_name(self, obj):
        return str(obj.lab.lab_name)

    lab_name.short_description = 'lab name'

    def lab_order(self, obj):
        return obj.lab.lab_order

    lab_order.short_description = 'lab order'


class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'in_ch', 'start_time', 'end_time']
    list_filter = ['user', 'resource', 'in_ch', 'start_time', 'end_time']
    list_per_page = 20


class LaboratoryAdmin(admin.ModelAdmin):
    list_display = ['lab_order', 'lab_name', 'pi_name', 'pi_email', 'pi_phone', 'location']
    list_filter = ['lab_order', 'lab_name', 'pi_name']
    ordering = ['lab_order']
    list_per_page = 20


admin.site.register(EPsLinks, EPsLinksAdmin)
admin.site.register(SPDsLinks, SPDsLinksAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Laboratory, LaboratoryAdmin)
