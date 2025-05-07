# دليل تكامل PayPal REST API مع Django

هذا الدليل يشرح كيفية تكامل PayPal REST API مع Django بطريقة آمنة وصحيحة، حيث يتم التعامل مع كل العمليات من خلال backend فقط دون الحاجة إلى JavaScript SDK.

## المتطلبات

1. حساب PayPal للمطورين
2. Django 3.2 أو أحدث
3. Django REST Framework

## الإعداد

### 1. إضافة الإعدادات في settings.py

```python
# PayPal REST API Settings
PAYPAL_MODE = 'sandbox'  # استخدم 'live' للإنتاج
PAYPAL_CLIENT_ID = 'YOUR_PAYPAL_CLIENT_ID'
PAYPAL_SECRET = 'YOUR_PAYPAL_SECRET'

# عناوين URL للعودة والإلغاء
PAYPAL_API_BASE_URL = 'https://api-m.sandbox.paypal.com' if PAYPAL_MODE == 'sandbox' else 'https://api-m.paypal.com'
PAYPAL_RETURN_URL = 'https://yourdomain.com/api/payments/paypal/return/'
PAYPAL_CANCEL_URL = 'https://yourdomain.com/api/payments/paypal/cancel/'

# إعدادات إضافية
PAYPAL_CURRENCY = 'USD'
SITE_DOMAIN = 'yourdomain.com'
```

### 2. إضافة URLs

في ملف `urls.py` الرئيسي:

```python
from django.urls import path, include

urlpatterns = [
    # ... URLs أخرى
    
    # إضافة URLs الخاصة بـ PayPal API
    path('api/payments/', include('payments.urls_paypal_api')),
    
    # إضافة URLs لصفحات العرض
    path('payments/', include('payments.urls_payment_pages')),
]
```

## خطوات التكامل

### 1. إنشاء طلب دفع

لإنشاء طلب دفع جديد، قم بإرسال طلب POST إلى `/api/payments/create-order/` مع البيانات التالية:

```json
{
    "amount": "100.00",
    "currency": "USD",
    "booking_id": "123",
    "description": "دفع مقابل الحجز رقم 123"
}
```

سيقوم الخادم بإنشاء طلب دفع في PayPal وإعادة البيانات التالية:

```json
{
    "success": true,
    "order_id": "5O190127TN364715T",
    "status": "CREATED",
    "approve_url": "https://www.sandbox.paypal.com/checkoutnow?token=5O190127TN364715T"
}
```

### 2. توجيه المستخدم إلى PayPal

قم بتوجيه المستخدم إلى `approve_url` المستلم من الخطوة السابقة:

```javascript
window.location.href = data.approve_url;
```

### 3. معالجة العودة من PayPal

بعد موافقة المستخدم على الدفع، سيتم توجيهه إلى `PAYPAL_RETURN_URL` المحدد في الإعدادات مع معلمة `token` تحتوي على معرف الطلب:

```
https://yourdomain.com/api/payments/paypal/return/?token=5O190127TN364715T&PayerID=ABCDEFGHIJKL
```

سيقوم الخادم بمعالجة العودة وتنفيذ عملية الدفع (capture) وتحديث حالة الدفع في قاعدة البيانات.

### 4. معالجة إلغاء الدفع

إذا قام المستخدم بإلغاء الدفع، سيتم توجيهه إلى `PAYPAL_CANCEL_URL` المحدد في الإعدادات:

```
https://yourdomain.com/api/payments/paypal/cancel/?token=5O190127TN364715T
```

سيقوم الخادم بتحديث حالة الدفع إلى "ملغي" في قاعدة البيانات.

### 5. التحقق من حالة الدفع

يمكنك التحقق من حالة الدفع عن طريق إرسال طلب GET إلى `/api/payments/status/{order_id}/`:

```
GET /api/payments/status/5O190127TN364715T/
```

سيقوم الخادم بإعادة حالة الدفع:

```json
{
    "order_id": "5O190127TN364715T",
    "status": "completed",
    "amount": "100.00",
    "currency": "USD",
    "transaction_id": "62J05946D1180435P",
    "created_at": "2023-06-01T12:34:56.789Z",
    "updated_at": "2023-06-01T12:40:12.345Z"
}
```

## ملاحظات هامة

1. **الأمان**: تأكد من أن `PAYPAL_CLIENT_ID` و `PAYPAL_SECRET` محميان ولا يتم مشاركتهما مع أي شخص.

2. **التحقق**: قم دائمًا بالتحقق من صحة البيانات المستلمة من PayPal قبل تحديث حالة الطلب في قاعدة البيانات.

3. **الاختبار**: استخدم وضع `sandbox` للاختبار قبل الانتقال إلى وضع `live`.

4. **التعامل مع الأخطاء**: قم بتنفيذ آلية قوية للتعامل مع الأخطاء وتسجيلها.

5. **التوثيق**: قم بتوثيق جميع المعاملات في قاعدة البيانات للرجوع إليها لاحقًا.

## المراجع

- [PayPal REST API Documentation](https://developer.paypal.com/docs/api/overview/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
