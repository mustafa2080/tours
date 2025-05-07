/**
 * تكامل PayPal Sandbox مع Django
 * هذا الملف يتعامل مع عمليات الدفع عبر PayPal Sandbox
 */

// دالة لإنشاء طلب دفع جديد
async function createPayPalOrder(bookingId) {
    try {
        // عرض حالة التحميل
        showLoadingState();
        
        // إرسال طلب إلى API
        const response = await fetch('/api/create-paypal-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken() // دالة للحصول على CSRF token
            },
            body: JSON.stringify({
                booking_id: bookingId
            })
        });
        
        // تحليل البيانات المستلمة
        const data = await response.json();
        
        // التحقق من نجاح الطلب
        if (!data.success || !data.approve_url) {
            throw new Error(data.error || 'فشل إنشاء طلب الدفع');
        }
        
        // تسجيل البيانات للتصحيح
        console.log('تم إنشاء طلب PayPal بنجاح:', data);
        
        // توجيه المستخدم إلى صفحة PayPal للموافقة على الدفع
        window.location.href = data.approve_url;
        
    } catch (error) {
        // إخفاء حالة التحميل
        hideLoadingState();
        
        // عرض رسالة الخطأ
        showErrorMessage(error.message || 'حدث خطأ أثناء إنشاء طلب الدفع');
        
        // تسجيل الخطأ للتصحيح
        console.error('خطأ في إنشاء طلب PayPal:', error);
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

// دالة لعرض حالة التحميل
function showLoadingState() {
    // إخفاء زر الدفع
    const payButton = document.getElementById('pay-button');
    if (payButton) {
        payButton.style.display = 'none';
    }
    
    // عرض مؤشر التحميل
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'block';
    }
}

// دالة لإخفاء حالة التحميل
function hideLoadingState() {
    // عرض زر الدفع
    const payButton = document.getElementById('pay-button');
    if (payButton) {
        payButton.style.display = 'block';
    }
    
    // إخفاء مؤشر التحميل
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

// دالة لعرض رسالة خطأ
function showErrorMessage(message) {
    // عرض رسالة الخطأ
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.textContent = message;
        errorContainer.style.display = 'block';
    } else {
        // إذا لم يكن هناك حاوية للخطأ، استخدم تنبيهًا
        alert(message);
    }
}

// تهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // البحث عن زر الدفع
    const payButton = document.getElementById('pay-button');
    
    // إضافة مستمع حدث للنقر على زر الدفع
    if (payButton) {
        payButton.addEventListener('click', function() {
            // الحصول على معرف الحجز من السمة
            const bookingId = payButton.getAttribute('data-booking-id');
            
            // التحقق من وجود معرف الحجز
            if (!bookingId) {
                showErrorMessage('لم يتم العثور على معرف الحجز');
                return;
            }
            
            // إنشاء طلب دفع
            createPayPalOrder(bookingId);
        });
    }
});
