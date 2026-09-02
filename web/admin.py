from django.contrib import admin
from .models import Zone, TableZone, Customer, CustomerPhone, Reservation, Review


admin.site.site_header = "The Book & Brew — ระบบจัดการหลังบ้าน"
admin.site.site_title = "The Book & Brew Admin"
admin.site.index_title = "ยินดีต้อนรับสู่ระบบจัดการ Book Cafe & Library Lounge"


@admin.register(TableZone)
class TableZoneAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'zone_id', 'table_type', 'capacity', 'status')
    list_filter = ('zone_id', 'table_type', 'status')
    search_fields = ('table_id', 'table_number')
    list_editable = ('status', 'capacity')
    ordering = ('table_id',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_id', 'customer_id', 'table_id', 'reserve_datetime', 'confirm_status')
    list_filter = ('confirm_status', 'reserve_datetime')
    search_fields = ('reservation_id', 'customer_id', 'table_id')
    list_editable = ('confirm_status',)
    ordering = ('-reserve_datetime',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'first_name', 'last_name')
    search_fields = ('customer_id', 'first_name', 'last_name')
    ordering = ('customer_id',)


@admin.register(CustomerPhone)
class CustomerPhoneAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'phone_number', 'phone_type')
    search_fields = ('customer_id', 'phone_number')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_id', 'nickname', 'message_snippet')
    search_fields = ('review_id', 'nickname', 'message')
    ordering = ('-review_id',)

    def message_snippet(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_snippet.short_description = "ข้อความรีวิว"


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_id', 'zone_name')
    search_fields = ('zone_id', 'zone_name')
