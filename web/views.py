import re
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from .models import Zone, TableZone, Customer, CustomerPhone, Reservation, Review


def get_next_customer_id():
    customers = Customer.objects.all().values_list('customer_id', flat=True)
    max_num = 0
    for cid in customers:
        nums = re.findall(r'\d+', str(cid))
        if nums:
            max_num = max(max_num, int(nums[0]))
    return f"C{max_num + 1:05d}"


def get_next_reservation_id():
    now_str = datetime.now().strftime("%y%m")
    prefix = f"RES{now_str}-"
    existing = Reservation.objects.filter(reservation_id__startswith=prefix).values_list('reservation_id', flat=True)
    max_num = 0
    for rid in existing:
        try:
            num = int(rid.split("-")[-1])
            max_num = max(max_num, num)
        except (ValueError, IndexError):
            pass
    return f"{prefix}{max_num + 1:03d}"


def get_next_review_id():
    existing = Review.objects.all().values_list('review_id', flat=True)
    max_num = 0
    for rid in existing:
        nums = re.findall(r'\d+', str(rid))
        if nums:
            max_num = max(max_num, int(nums[0]))
    return f"RV{max_num + 1:03d}"


def home(request):
    zones = Zone.objects.all()
    tables = TableZone.objects.all().order_by('table_id')
    reviews = Review.objects.all().order_by('-review_id')

    # Calculate statistics
    total_tables = tables.count()
    available_tables = tables.filter(status="ว่าง").count()

    context = {
        "zones": zones,
        "tables": tables,
        "reviews": reviews,
        "total_tables": total_tables,
        "available_tables": available_tables,
    }
    return render(request, "index.html", context)


@require_GET
def get_tables_api(request):
    tables = TableZone.objects.all().order_by('table_id')
    data = [
        {
            "table_id": t.table_id,
            "zone_id": t.zone_id,
            "table_number": t.table_number,
            "table_type": t.table_type,
            "capacity": t.capacity,
            "status": t.status,
            "is_available": t.status == "ว่าง",
        }
        for t in tables
    ]
    return JsonResponse({"tables": data})


@require_POST
def book_table(request):
    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    reserve_datetime_str = request.POST.get("reserve_datetime", "").strip()
    table_id = request.POST.get("table_id", "").strip()

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or \
              "application/json" in request.headers.get("Accept", "")

    if not name or not phone or not reserve_datetime_str or not table_id:
        msg = "กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง (ชื่อ, เบอร์โทรศัพท์, วันเวลา และเลือกโต๊ะ)"
        if is_ajax:
            return JsonResponse({"success": False, "message": msg}, status=400)
        messages.error(request, msg)
        return redirect("/#reserve")

    # Parse datetime (supports "YYYY-MM-DDTHH:MM" from datetime-local input)
    try:
        if "T" in reserve_datetime_str:
            parsed_dt = datetime.strptime(reserve_datetime_str, "%Y-%m-%dT%H:%M")
        else:
            parsed_dt = datetime.strptime(reserve_datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            parsed_dt = datetime.strptime(reserve_datetime_str, "%Y-%m-%d %H:%M")
        except ValueError:
            parsed_dt = datetime.now()

    # Split name into first and last name if possible
    name_parts = name.split(None, 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else "-"

    try:
        with transaction.atomic():
            table = TableZone.objects.select_for_update().filter(table_id=table_id).first()

            if not table:
                msg = f"ไม่พบโต๊ะรหัส {table_id} ในระบบ"
                if is_ajax:
                    return JsonResponse({"success": False, "message": msg}, status=404)
                messages.error(request, msg)
                return redirect("/#reserve")

            # Check availability - Requirement: "ในส่วนคนที่กดไม่ทันจะแจ้งเตือนว่า โต๊ะนี้ถูกจองไปแล้ว"
            if table.status != "ว่าง":
                msg = "โต๊ะนี้ถูกจองไปแล้ว กรุณาเลือกโต๊ะอื่น"
                if is_ajax:
                    return JsonResponse({"success": False, "message": msg, "already_booked": True}, status=409)
                messages.error(request, msg)
                return redirect("/#reserve")

            # Create Customer
            customer_id = get_next_customer_id()
            customer = Customer.objects.create(
                customer_id=customer_id,
                first_name=first_name,
                last_name=last_name,
            )

            # Create CustomerPhone (limit to max 10 chars as per schema)
            clean_phone = re.sub(r'[^0-9]', '', phone)[:10] or "0000000000"
            CustomerPhone.objects.create(
                customer_id=customer_id,
                phone_number=clean_phone,
                phone_type="Mobile",
            )

            # Create Reservation
            res_id = get_next_reservation_id()
            reservation = Reservation.objects.create(
                reservation_id=res_id,
                customer_id=customer_id,
                table_id=table_id,
                reserve_datetime=parsed_dt,
                confirm_status="สำเร็จ",
            )

            # Update table status
            table.status = "ไม่ว่าง"
            table.save()

            success_msg = f"จองโต๊ะสำเร็จ! รหัสการจอง: {res_id} (โต๊ะ {table.table_id} - {table.table_type})"
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": success_msg,
                    "reservation_id": res_id,
                    "table_id": table_id,
                    "table_type": table.table_type,
                    "customer_name": name,
                    "reserve_datetime": parsed_dt.strftime("%d/%m/%Y %H:%M"),
                })
            messages.success(request, success_msg)
            return redirect("/#reserve")

    except Exception as e:
        err_msg = f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}"
        if is_ajax:
            return JsonResponse({"success": False, "message": err_msg}, status=500)
        messages.error(request, err_msg)
        return redirect("/#reserve")


@require_POST
def add_review(request):
    nickname = request.POST.get("nickname", "").strip()
    message_text = request.POST.get("message", "").strip()

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or \
              "application/json" in request.headers.get("Accept", "")

    if not nickname or not message_text:
        msg = "กรุณากรอกชื่อเล่นและข้อความรีวิวให้ครบถ้วน"
        if is_ajax:
            return JsonResponse({"success": False, "message": msg}, status=400)
        messages.error(request, msg)
        return redirect("/#reviews")

    try:
        review_id = get_next_review_id()
        review = Review.objects.create(
            review_id=review_id,
            nickname=nickname[:50],
            message=message_text,
        )
        success_msg = "ส่งความคิดเห็น/แนะนำหนังสือเรียบร้อยแล้ว ขอบคุณครับ!"
        if is_ajax:
            return JsonResponse({
                "success": True,
                "message": success_msg,
                "review_id": review_id,
                "nickname": review.nickname,
                "review_text": review.message,
            })
        messages.success(request, success_msg)
        return redirect("/#reviews")

    except Exception as e:
        err_msg = f"เกิดข้อผิดพลาดในการบันทึกรีวิว: {str(e)}"
        if is_ajax:
            return JsonResponse({"success": False, "message": err_msg}, status=500)
        messages.error(request, err_msg)
        return redirect("/#reviews")
