/**
 * Advanced Dashboard Management
 * Includes session tracking, real-time updates, and auto-sorting
 */

class DashboardManager {
  constructor() {
    this.sessionTimeout = null;
    this.refreshInterval = null;
    this.autoSortEnabled = false;
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.updateSessionInfo();
    this.startAutoRefresh();
  }

  setupEventListeners() {
    // Auto Sort
    document.getElementById('autoSortBtn')?.addEventListener('click', () => {
      this.toggleAutoSort();
    });

    // Refresh
    document.getElementById('refreshBtn')?.addEventListener('click', () => {
      location.reload();
    });

    // Export
    document.getElementById('exportBtn')?.addEventListener('click', () => {
      this.exportData();
    });

    // Settings
    document.getElementById('settingsBtn')?.addEventListener('click', () => {
      this.showSettings();
    });

    // Search
    document.getElementById('searchInput')?.addEventListener('keyup', (e) => {
      this.searchTable(e.target.value);
    });

    // Sort Select
    document.getElementById('sortSelect')?.addEventListener('change', (e) => {
      this.sortTable(e.target.value);
    });

    // Extend Session
    document.getElementById('extendSessionBtn')?.addEventListener('click', () => {
      this.extendSession();
    });

    // Filter
    document.getElementById('filterBtn')?.addEventListener('click', () => {
      this.showAdvancedFilter();
    });
  }

  /**
   * تحديث معلومات الجلسة من الـ API
   */
  async updateSessionInfo() {
    try {
      const response = await fetch('/api/session/');
      const data = await response.json();

      this.updateSessionUI(data);
      this.scheduleSessionWarning(data.remaining_seconds);
    } catch (error) {
      console.error('خطأ في تحديث معلومات الجلسة:', error);
    }
  }

  /**
   * تحديث واجهة الجلسة
   */
  updateSessionUI(data) {
    const minutes = Math.floor(data.remaining_seconds / 60);
    const seconds = data.remaining_seconds % 60;

    // تحديث الشاشة
    const timer = document.getElementById('sessionTimer');
    if (timer) {
      timer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    // تحديث شريط التقدم
    const maxSeconds = data.session_timeout_minutes * 60;
    const progress = (data.remaining_seconds / maxSeconds) * 100;
    const progressBar = document.getElementById('sessionProgress');
    if (progressBar) {
      progressBar.style.width = progress + '%';
    }

    // تحديث وقت الانتهاء
    const expiryTime = new Date(data.expiry_time);
    const expiryDisplay = document.getElementById('expiryTime');
    if (expiryDisplay) {
      expiryDisplay.textContent = expiryTime.toLocaleTimeString('ar-SA');
    }
  }

  /**
   * جدولة تحذير الجلسة
   */
  scheduleSessionWarning(remainingSeconds) {
    // تحذير بعد 5 دقائق من الانتهاء
    const warningTime = remainingSeconds - 300;

    if (warningTime > 0) {
      this.sessionTimeout = setTimeout(() => {
        this.showSessionWarning();
      }, warningTime * 1000);
    }
  }

  /**
   * عرض تحذير الجلسة
   */
  showSessionWarning() {
    const modal = document.getElementById('sessionWarningModal');
    if (modal) {
      const bsModal = new bootstrap.Modal(modal);
      bsModal.show();
    }
  }

  /**
   * استمرار الجلسة
   */
  async extendSession() {
    try {
      // يمكن إضافة endpoint لإعادة تعيين الجلسة
      this.updateSessionInfo();
      const modal = document.getElementById('sessionWarningModal');
      if (modal) {
        bootstrap.Modal.getInstance(modal).hide();
      }
    } catch (error) {
      console.error('خطأ في استمرار الجلسة:', error);
    }
  }

  /**
   * بدء التحديث التلقائي
   */
  startAutoRefresh() {
    this.refreshInterval = setInterval(() => {
      this.updateSessionInfo();
      this.updateDashboardStats();
    }, 30000); // تحديث كل 30 ثانية
  }

  /**
   * تحديث إحصائيات الداشبورد
   */
  async updateDashboardStats() {
    try {
      const response = await fetch('/api/dashboard/');
      const data = await response.json();
      // يمكن إضافة رسوم بيانية هنا
      console.log('Updated stats:', data);
    } catch (error) {
      console.error('خطأ في تحديث الإحصائيات:', error);
    }
  }

  /**
   * تفعيل/تعطيل الترتيب التلقائي
   */
  toggleAutoSort() {
    this.autoSortEnabled = !this.autoSortEnabled;

    const btn = document.getElementById('autoSortBtn');
    if (btn) {
      if (this.autoSortEnabled) {
        btn.classList.add('active');
        this.sortTableAuto();
      } else {
        btn.classList.remove('active');
      }
    }
  }

  /**
   * الفرز التلقائي للجدول
   */
  sortTableAuto() {
    const table = document.getElementById('reportsTable');
    const tbody = table?.getElementsByTagName('tbody')[0];
    if (!tbody) return;

    const rows = Array.from(tbody.rows);
    rows.sort((a, b) => {
      // الفرز حسب التاريخ الأحدث أولاً
      const dateA = new Date(a.cells[4]?.textContent);
      const dateB = new Date(b.cells[4]?.textContent);
      return dateB - dateA;
    });

    rows.forEach(row => tbody.appendChild(row));
  }

  /**
   * فرز الجدول
   */
  sortTable(sortBy) {
    const table = document.getElementById('reportsTable');
    const tbody = table?.getElementsByTagName('tbody')[0];
    if (!tbody) return;

    const rows = Array.from(tbody.rows);

    rows.sort((a, b) => {
      let aVal, bVal;

      switch (sortBy) {
        case 'date-asc':
          return new Date(a.cells[4].textContent) - new Date(b.cells[4].textContent);
        case 'date-desc':
          return new Date(b.cells[4].textContent) - new Date(a.cells[4].textContent);
        case 'category':
          aVal = a.cells[1].textContent;
          bVal = b.cells[1].textContent;
          return aVal.localeCompare(bVal, 'ar');
        case 'reporter':
          aVal = a.cells[2].textContent;
          bVal = b.cells[2].textContent;
          return aVal.localeCompare(bVal, 'ar');
        default:
          return 0;
      }
    });

    rows.forEach(row => tbody.appendChild(row));
  }

  /**
   * البحث في الجدول
   */
  searchTable(searchTerm) {
    const table = document.getElementById('reportsTable');
    const rows = table?.getElementsByTagName('tbody')[0]?.rows;

    if (!rows) return;

    Array.from(rows).forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(searchTerm.toLowerCase()) ? '' : 'none';
    });
  }

  /**
   * التصفية المتقدمة
   */
  showAdvancedFilter() {
    // يمكن إضافة نموذج فلترة متقدمة هنا
    alert('سيتم إضافة نموذج التصفية المتقدمة قريباً');
  }

  /**
   * تصدير البيانات
   */
  exportData() {
    const table = document.getElementById('reportsTable');
    if (!table) return;

    const csv = [];

    // Headers
    const headers = [];
    Array.from(table.querySelectorAll('th')).forEach(th => {
      headers.push(th.textContent);
    });
    csv.push(headers.join(','));

    // Rows
    Array.from(table.querySelectorAll('tbody tr')).forEach(tr => {
      const row = [];
      Array.from(tr.querySelectorAll('td')).slice(0, -1).forEach(td => {
        row.push(`"${td.textContent.trim()}"`);
      });
      csv.push(row.join(','));
    });

    // Download
    const csvContent = 'data:text/csv;charset=utf-8,' + csv.join('\n');
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csvContent));
    link.setAttribute('download', `reports_${new Date().getTime()}.csv`);
    link.click();
  }

  /**
   * عرض الإعدادات
   */
  showSettings() {
    alert('سيتم إضافة نافذة الإعدادات قريباً');
  }

  /**
   * تنظيف الموارد
   */
  destroy() {
    clearTimeout(this.sessionTimeout);
    clearInterval(this.refreshInterval);
  }
}

// تهيئة الداشبورد عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
  window.dashboardManager = new DashboardManager();
});
