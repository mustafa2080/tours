# دليل تكامل PayPal Sandbox مع Django

هذا الدليل يشرح كيفية استخدام التكامل المنفذ بين Django و PayPal Sandbox.

## الملفات المنفذة

1. **عميل PayPal**:
   - `payments/paypal_client_updated.py`: عميل للتعامل مع PayPal REST API

2. **Views للتعامل مع عمليات الدفع**:
   - `payments/views_paypal_sandbox.py`: views للتعامل مع عمليات الدفع
   - `payments/views_payment_sandbox.py`: صفحة الدفع

3. **URLs للتعامل مع عمليات الدفع**:
   - `payments/urls_paypal_sandbox.py`: URLs للتعامل مع عمليات الدفع

4. **JavaScript للتعامل مع PayPal من الواجهة الأمامية**:
   - `static/js/paypal-sandbox-integration.js`: JavaScript للتعامل مع PayPal من الواجهة الأمامية

5. **صفحة HTML للدفع**:
   - `templates/payments/payment_sandbox.html`: صفحة HTML للدفع

6. **تعديل BookingCreateView**:
   - `booking/views_sandbox.py`: تعديل BookingCreateView لاستخدام صفحة الدفع الجديدة

## كيفية الاستخدام

### 1. إضافة URLs إلى ملف urls.py الرئيسي

```python
from django.urls import path, include

urlpatterns = [
    # ... URLs أخرى
    
    # إضافة URLs الخاصة بـ PayPal Sandbox
    path('payments/', include('payments.urls_paypal_sandbox')),
]
```

### 2. استخدام BookingCreateViewSandbox بدلاً من BookingCreateView

```python
from django.urls import path
from booking.views_sandbox import BookingCreateViewSandbox

urlpatterns = [
    # ... URLs أخرى
    
    # استخدام BookingCreateViewSandbox بدلاً من BookingCreateView
    path('new/tour/<int:tour_id>/', BookingCreateViewSandbox.as_view(), name='booking_create'),
]
```

### 3. التأكد من وجود الإعدادات المطلوبة في settings.py

```python
# PayPal Sandbox settings
PAYPAL_MODE = 'sandbox'  # sandbox or live
PAYPAL_CLIENT_ID = 'YOUR_PAYPAL_CLIENT_ID'
PAYPAL_SECRET = 'YOUR_PAYPAL_SECRET'
PAYPAL_RETURN_URL = 'http://127.0.0.1:8000/payments/paypal/return/'
PAYPAL_CANCEL_URL = 'http://127.0.0.1:8000/payments/paypal/cancel/'
PAYPAL_TEST_MODE = True  # Set to False in production
SITE_URL = 'http://127.0.0.1:8000'
SITE_NAME = 'Tourism Website'
```

## خطوات عملية الدفع

1. **إنشاء حجز**:
   - يقوم المستخدم بإنشاء حجز جديد
   - يتم توجيه المستخدم إلى صفحة الدفع

2. **صفحة الدفع**:
   - يتم عرض تفاصيل الحجز والمبلغ المطلوب دفعه
   - يقوم المستخدم بالنقر على زر "الدفع عبر PayPal"

3. **إنشاء طلب دفع**:
   - يتم إرسال طلب POST إلى `/payments/api/create-paypal-order/`
   - يتم إنشاء طلب دفع في PayPal
   - يتم الحصول على رابط الموافقة

4. **توجيه المستخدم إلى PayPal**:
   - يتم توجيه المستخدم إلى رابط الموافقة
   - يقوم المستخدم بتسجيل الدخول إلى PayPal والموافقة على الدفع

5. **العودة من PayPal**:
   - يتم توجيه المستخدم إلى `/payments/paypal/return/`
   - يتم تنفيذ عملية الدفع (capture)
   - يتم تحديث حالة الحجز والدفع
   - يتم عرض صفحة التأكيد

6. **إلغاء الدفع**:
   - إذا قام المستخدم بإلغاء الدفع، يتم توجيهه إلى `/payments/paypal/cancel/`
   - يتم تحديث حالة الدفع إلى "ملغي"
   - يتم إعادة توجيه المستخدم إلى قائمة الحجوزات

## ملاحظات هامة

1. **وضع الاختبار**:
   - يمكن تفعيل وضع الاختبار عن طريق ضبط `PAYPAL_TEST_MODE = True`
   - في وضع الاختبار، يتم استخدام استجابات وهمية بدلاً من الاتصال بـ PayPal

2. **بيانات الاعتماد**:
   - تأكد من استخدام بيانات اعتماد PayPal Sandbox الخاصة بك
   - لا تستخدم بيانات اعتماد الإنتاج في بيئة التطوير

3. **عناوين URL**:
   - تأكد من ضبط `PAYPAL_RETURN_URL` و `PAYPAL_CANCEL_URL` بشكل صحيح
   - في بيئة الإنتاج، استخدم عناوين URL كاملة مع HTTPS

4. **التعامل مع الأخطاء**:
   - تم تنفيذ آلية قوية للتعامل مع الأخطاء وتسجيلها
   - في حالة حدوث خطأ، يتم عرض رسالة خطأ للمستخدم وتسجيل الخطأ في السجل
