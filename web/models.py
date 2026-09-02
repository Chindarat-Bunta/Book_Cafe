from django.db import models


class Zone(models.Model):
    zone_id = models.CharField(db_column='Zone_ID', primary_key=True, max_length=5)
    zone_name = models.CharField(db_column='Zone_Name', max_length=50)

    class Meta:
        managed = False
        db_table = 'zone'
        verbose_name = 'โซน'
        verbose_name_plural = 'โซนทั้งหมด'

    def __str__(self):
        return f"{self.zone_id} - {self.zone_name}"


class TableZone(models.Model):
    table_id = models.CharField(db_column='Table_ID', primary_key=True, max_length=5)
    zone_id = models.CharField(db_column='Zone_ID', max_length=5)
    table_number = models.CharField(db_column='Table_Number', max_length=10)
    table_type = models.CharField(db_column='Table_Type', max_length=20)
    capacity = models.CharField(db_column='Capacity', max_length=20)
    status = models.CharField(db_column='Status', max_length=10)

    class Meta:
        managed = False
        db_table = 'table_zone'
        verbose_name = 'โต๊ะ'
        verbose_name_plural = 'โต๊ะทั้งหมด'

    def __str__(self):
        return f"{self.table_id} ({self.table_type}) - {self.status}"


class Customer(models.Model):
    customer_id = models.CharField(db_column='Customer_ID', primary_key=True, max_length=6)
    first_name = models.CharField(db_column='First_Name', max_length=50)
    last_name = models.CharField(db_column='Last_Name', max_length=50)

    class Meta:
        managed = False
        db_table = 'customer'
        verbose_name = 'ลูกค้า'
        verbose_name_plural = 'ข้อมูลลูกค้า'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CustomerPhone(models.Model):
    customer_id = models.CharField(db_column='Customer_ID', max_length=6)
    phone_number = models.CharField(db_column='Phone_Number', primary_key=True, max_length=10)
    phone_type = models.CharField(db_column='Phone_Type', max_length=20, default='Mobile')

    class Meta:
        managed = False
        db_table = 'customer_phone'
        verbose_name = 'เบอร์โทรลูกค้า'
        verbose_name_plural = 'เบอร์โทรลูกค้าทั้งหมด'

    def __str__(self):
        return f"{self.customer_id}: {self.phone_number}"


class Reservation(models.Model):
    reservation_id = models.CharField(db_column='Reservation_ID', primary_key=True, max_length=12)
    customer_id = models.CharField(db_column='Customer_ID', max_length=6)
    table_id = models.CharField(db_column='Table_ID', max_length=6)
    reserve_datetime = models.DateTimeField(db_column='Reserve_DateTime')
    confirm_status = models.CharField(db_column='Confirm_Status', max_length=20, default='สำเร็จ')

    class Meta:
        managed = False
        db_table = 'reservation'
        verbose_name = 'การจอง'
        verbose_name_plural = 'รายการจองทั้งหมด'

    def __str__(self):
        return f"{self.reservation_id} - {self.table_id} ({self.confirm_status})"


class Review(models.Model):
    review_id = models.CharField(db_column='Review_ID', primary_key=True, max_length=6)
    nickname = models.CharField(db_column='Nickname', max_length=50)
    message = models.TextField(db_column='Message')

    class Meta:
        managed = False
        db_table = 'review'
        verbose_name = 'รีวิว'
        verbose_name_plural = 'รีวิวทั้งหมด'

    def __str__(self):
        return f"{self.nickname}: {self.message[:30]}"
