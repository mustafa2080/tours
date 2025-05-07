/**
 * مثال على كيفية استخدام PayPal API من الواجهة الأمامية
 * 
 * ملاحظة: هذا الملف للتوضيح فقط ولا يتم استخدامه في التكامل الفعلي
 * حيث أن التكامل يتم بالكامل من خلال backend
 */

// دالة لإنشاء طلب دفع جديد
async function createPayPalOrder(amount, bookingId = null) {
    try {
        // إعداد بيانات الطلب
        const requestData = {
            amount: amount,
            currency: 'USD'
        };
        
        // إضافة معرف الحجز إذا كان متاحًا
        if (bookingId) {
            requestData.booking_id = bookingId;
        }
        
        // إرسال طلب إلى API
        const response = await fetch('/api/payments/create-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken() // دالة للحصول على CSRF token
            },
            body: JSON.stringify(requestData)
        });
        
        // التحقق من نجاح الطلب
        if (!response.ok) {
            throw new Error('فشل إنشاء طلب الدفع');
        }
        
        // تحليل البيانات المستلمة
        const data = await response.json();
        
        // التحقق من وجود رابط الموافقة
        if (!data.success || !data.approve_url) {
            throw new Error('لم يتم العثور على رابط الموافقة');
        }
        
        // توجيه المستخدم إلى صفحة PayPal للموافقة على الدفع
        window.location.href = data.approve_url;
        
    } catch (error) {
        console.error('خطأ في إنشاء طلب الدفع:', error);
        // عرض رسالة خطأ للمستخدم
        showErrorMessage(error.message);
    }
}

// دالة للحصول على CSRF token
function getCsrfToken() {
    // البحث عن CSRF token في ملفات تعريف الارتباط
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    return cookieValue || '';
}

// دالة لعرض رسالة خطأ
function showErrorMessage(message) {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
    } else {
        alert(message);
    }
}

// مثال على استخدام الدالة عند النقر على زر الدفع
document.addEventListener('DOMContentLoaded', function() {
    const payButton = document.getElementById('pay-button');
    
    if (payButton) {
        payButton.addEventListener('click', function() {
            // الحصول على المبلغ ومعرف الحجز من الصفحة
            const amount = document.getElementById('amount').value;
            const bookingId = document.getElementById('booking-id').value;
            
            // إنشاء طلب دفع
            createPayPalOrder(amount, bookingId);
        });
    }
});
