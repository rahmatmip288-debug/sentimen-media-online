// State Aplikasi
let allKeywords = [];
let currentCategoryFilter = 'all';
let sentimentChart = null;

document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
});

// ================= AUTENTIKASI & KEAMANAN =================
async function checkAuthStatus() {
    try {
        const res = await fetch('/api/auth-status');
        const data = await res.json();
        
        if (data.is_logged_in) {
            document.getElementById('login-modal').classList.add('hidden');
            updatePasswordRotationUI(data.password_info);
            loadKeywords();
            loadStats();
            loadHistory();
        } else {
            document.getElementById('login-modal').classList.remove('hidden');
        }
    } catch (err) {
        console.error('Gagal memeriksa status login:', err);
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const password = document.getElementById('login-password').value;
    const btn = document.getElementById('btn-login');
    const errBox = document.getElementById('login-error');
    const errMsg = document.getElementById('login-error-msg');

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Memverifikasi...';
    errBox.classList.add('hidden');

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });
        const data = await res.json();

        if (data.success) {
            document.getElementById('login-modal').classList.add('hidden');
            document.getElementById('login-password').value = '';
            updatePasswordRotationUI(data.password_info);
            loadKeywords();
            loadStats();
            loadHistory();
        } else {
            errMsg.textContent = data.message || 'Password salah.';
            errBox.classList.remove('hidden');
        }
    } catch (err) {
        errMsg.textContent = 'Gagal menghubungi server. Pastikan aplikasi berjalan.';
        errBox.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>Masuk ke Dashboard</span> <i class="fa-solid fa-arrow-right text-xs"></i>';
    }
}

async function handleLogout() {
    if (!confirm('Apakah Anda yakin ingin keluar dari sistem?')) return;
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.reload();
    } catch (err) {
        console.error(err);
    }
}

function updatePasswordRotationUI(info) {
    if (!info) return;

    const banner = document.getElementById('overdue-banner');
    const rotText = document.getElementById('pwd-rotation-text');
    const dot = document.getElementById('pwd-warning-dot');

    if (info.is_overdue) {
        banner.classList.remove('hidden');
        rotText.textContent = 'Sandi Kadaluarsa';
        dot.className = 'w-2 h-2 rounded-full bg-rose-500 animate-ping';
    } else {
        banner.classList.add('hidden');
        rotText.textContent = `Sandi (${info.days_since_change}h lalu)`;
        dot.className = 'w-2 h-2 rounded-full bg-emerald-500';
    }

    // Modal Status Info
    document.getElementById('modal-last-change').textContent = info.last_change || 'Belum pernah';
    document.getElementById('modal-password-age').textContent = `${info.days_since_change} hari yang lalu (Jadwal: per ${info.rotation_days} hari)`;
    
    const secStatus = document.getElementById('modal-security-status');
    if (info.is_overdue) {
        secStatus.textContent = 'Perlu Rotasi Segera!';
        secStatus.className = 'px-2 py-0.5 rounded text-[11px] font-bold bg-rose-100 text-rose-800';
    } else {
        secStatus.textContent = 'Aman & Terkini';
        secStatus.className = 'px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800';
    }

    document.getElementById('select-rotation-days').value = info.rotation_days || 30;
}

function openPasswordModal() {
    document.getElementById('password-modal').classList.remove('hidden');
    document.getElementById('pwd-change-msg').classList.add('hidden');
    document.getElementById('input-old-password').value = '';
    document.getElementById('input-new-password').value = '';
    document.getElementById('input-confirm-password').value = '';
}

function closePasswordModal() {
    document.getElementById('password-modal').classList.add('hidden');
}

async function handleChangePassword(e) {
    e.preventDefault();
    const old_password = document.getElementById('input-old-password').value;
    const new_password = document.getElementById('input-new-password').value;
    const confirm_password = document.getElementById('input-confirm-password').value;
    const msgBox = document.getElementById('pwd-change-msg');
    const btn = document.getElementById('btn-save-password');

    btn.disabled = true;
    btn.textContent = 'Menyimpan...';

    try {
        const res = await fetch('/api/admin/change-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_password, new_password, confirm_password })
        });
        const data = await res.json();

        msgBox.classList.remove('hidden');
        if (data.success) {
            msgBox.className = 'p-3 rounded-xl text-xs bg-emerald-50 text-emerald-800 border border-emerald-200';
            msgBox.innerHTML = `<i class="fa-solid fa-check mr-1"></i> ${data.message}`;
            updatePasswordRotationUI(data.password_info);
            setTimeout(() => { closePasswordModal(); }, 1800);
        } else {
            msgBox.className = 'p-3 rounded-xl text-xs bg-rose-50 text-rose-800 border border-rose-200';
            msgBox.innerHTML = `<i class="fa-solid fa-circle-exclamation mr-1"></i> ${data.message}`;
        }
    } catch (err) {
        msgBox.className = 'p-3 rounded-xl text-xs bg-rose-50 text-rose-800 border border-rose-200';
        msgBox.textContent = 'Terjadi kesalahan sistem.';
        msgBox.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Simpan Password Baru';
    }
}

async function handleSaveRotation() {
    const days = document.getElementById('select-rotation-days').value;
    try {
        const res = await fetch('/api/admin/rotation-settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rotation_days: days })
        });
        const data = await res.json();
        if (data.success) {
            alert(data.message);
            updatePasswordRotationUI(data.password_info);
        }
    } catch (err) {
        alert('Gagal menyimpan jadwal rotasi');
    }
}

function togglePasswordVisibility(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fa-solid fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fa-solid fa-eye';
    }
}

// ================= NAVIGASI TAB =================
function switchTab(tabId) {
    ['tab-analisis', 'tab-keywords', 'tab-history'].forEach(id => {
        document.getElementById(id).classList.add('hidden');
        const navBtn = document.getElementById(`nav-${id}`);
        if (navBtn) {
            navBtn.className = 'tab-btn px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 rounded-lg transition-all';
        }
    });

    document.getElementById(tabId).classList.remove('hidden');
    const activeNav = document.getElementById(`nav-${tabId}`);
    if (activeNav) {
        activeNav.className = 'tab-btn px-4 py-2 text-xs font-semibold rounded-lg transition-all bg-white text-emerald-800 shadow-sm';
    }

    if (tabId === 'tab-history') {
        loadStats();
        loadHistory();
    } else if (tabId === 'tab-keywords') {
        loadKeywords();
    }
}

function setAnalysisMode(mode) {
    if (mode === 'url') {
        document.getElementById('section-input-url').classList.remove('hidden');
        document.getElementById('section-input-manual').classList.add('hidden');
        document.getElementById('mode-btn-url').className = 'px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5';
        document.getElementById('mode-btn-manual').className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-500 hover:text-slate-800 flex items-center gap-1.5';
    } else {
        document.getElementById('section-input-url').classList.add('hidden');
        document.getElementById('section-input-manual').classList.remove('hidden');
        document.getElementById('mode-btn-url').className = 'px-3.5 py-1.5 rounded-lg text-xs font-medium text-slate-500 hover:text-slate-800 flex items-center gap-1.5';
        document.getElementById('mode-btn-manual').className = 'px-3.5 py-1.5 rounded-lg text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5';
    }
}

// ================= ANALISIS SENTIMEN =================
function fillSampleUrl(url) {
    setAnalysisMode('url');
    document.getElementById('input-news-url').value = url;
}

function fillSampleText(type) {
    setAnalysisMode('manual');
    if (type === 'positif') {
        document.getElementById('manual-title').value = "Pemkab Bangka Raih Penghargaan Pelayanan Publik Terbaik dan Opini WTP";
        document.getElementById('manual-source').value = "Bangka Pos Online";
        document.getElementById('manual-content').value = 
`Pemerintah Kabupaten Bangka kembali mengukir prestasi gemilang dengan meraih penghargaan bergengsi tingkat nasional di bidang pelayanan prima dan inovasi digital. 

Pj Bupati Bangka menyampaikan apresiasi yang sangat tinggi kepada seluruh jajaran OPD dan masyarakat Kabupaten Bangka atas kerja keras dan sinergi yang terjalin dengan baik. Menurutnya, keberhasilan ini adalah bukti nyata komitmen Pemkab Bangka dalam menghadirkan tata kelola pemerintahan yang transparan, akuntabel, dan berorientasi pada kepuasan masyarakat.

Selain itu, Pemkab Bangka juga sukses mempertahankan opini Wajar Tanpa Pengecualian (WTP) dari BPK RI. Program beasiswa bagi siswa kurang mampu serta bantuan langsung untuk petani di Kecamatan Belinyu dan Sungailiat terus dioptimalkan guna mendorong kemajuan dan kesejahteraan daerah.`;
    } else {
        document.getElementById('manual-title').value = "Warga Sungailiat Keluhkan Jalan Rusak Parah dan Banjir, Soroti Lambatnya Penanganan Pemkab";
        document.getElementById('manual-source').value = "Babel Media Online";
        document.getElementById('manual-content').value = 
`Warga di sejumlah kelurahan di Kota Sungailiat Kabupaten Bangka menyampaikan kekecewaan mendalam atas lambatnya perbaikan jalan yang mengalami kerusakan parah. Kondisi jalan berlubang tersebut dinilai sangat merugikan pengguna jalan dan kerap memicu kecelakaan lalu lintas.

Selain persoalan jalan rusak, masalah banjir musiman juga kembali menjadi polemik dan keluhan hangat. Sejumlah tokoh masyarakat melayangkan kritik terhadap kinerja dinas terkait di Pemkab Bangka yang dinilai lambat dan belum optimal dalam menangani saluran drainase. 

Warga mendesak dinas terkait di Pemerintah Kabupaten Bangka agar segera turun ke lapangan melakukan perbaikan nyata tanpa menunggu eskalasi aksi protes atau unjuk rasa dari masyarakat yang semakin kecewa.`;
    }
}

async function handleAnalyzeUrl(e) {
    e.preventDefault();
    const url = document.getElementById('input-news-url').value.trim();
    if (!url) return;

    showLoading(true, "Mengunduh Berita...", "Menghubungi portal berita online dan mengekstrak artikel berita...");

    try {
        const res = await fetch('/api/analyze-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await res.json();

        if (data.success) {
            displayAnalysisResult(data.article, data.analysis);
        } else {
            alert(data.message || 'Gagal menganalisis URL berita');
        }
    } catch (err) {
        alert('Terjadi kesalahan jaringan atau server');
    } finally {
        showLoading(false);
    }
}

async function handleAnalyzeText(e) {
    e.preventDefault();
    const title = document.getElementById('manual-title').value.trim();
    const content = document.getElementById('manual-content').value.trim();
    const source = document.getElementById('manual-source').value.trim() || 'Input Manual';

    if (!content) return;

    showLoading(true, "Menganalisis Teks...", "Memproses kata kunci dan bobot sentimen Pemkab Bangka...");

    try {
        const res = await fetch('/api/analyze-text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content, source })
        });
        const data = await res.json();

        if (data.success) {
            displayAnalysisResult(data.article, data.analysis);
        } else {
            alert(data.message || 'Gagal menganalisis teks berita');
        }
    } catch (err) {
        alert('Terjadi kesalahan saat memproses teks');
    } finally {
        showLoading(false);
    }
}

function showLoading(show, title = "", desc = "") {
    const loading = document.getElementById('analysis-loading');
    const resultCard = document.getElementById('analysis-result-card');
    if (show) {
        loading.classList.remove('hidden');
        resultCard.classList.add('hidden');
        document.getElementById('loading-step-title').textContent = title;
        document.getElementById('loading-step-desc').textContent = desc;
    } else {
        loading.classList.add('hidden');
    }
}

function displayAnalysisResult(article, analysis) {
    const resultCard = document.getElementById('analysis-result-card');
    resultCard.classList.remove('hidden');

    // Judul & Sumber
    document.getElementById('res-title').textContent = article.title;
    document.getElementById('res-source').textContent = article.source || 'Media Online';
    document.getElementById('res-date').textContent = article.publish_date || 'Terkini';
    document.getElementById('res-relevance').textContent = analysis.relevance;

    const urlLink = document.getElementById('res-url-link');
    if (article.url && article.url.startsWith('http')) {
        urlLink.href = article.url;
        urlLink.classList.remove('hidden');
    } else {
        urlLink.classList.add('hidden');
    }

    // Sentiment Badge & Colors
    const sentBox = document.getElementById('res-sentiment-box');
    const sentBadge = document.getElementById('res-sentiment-badge');
    const sentText = document.getElementById('res-sentiment-text');
    const sentIcon = document.getElementById('res-sentiment-icon');
    const confBar = document.getElementById('res-confidence-bar');

    sentText.textContent = analysis.sentiment;
    document.getElementById('res-confidence').textContent = `${analysis.confidence}%`;
    confBar.style.width = `${analysis.confidence}%`;

    const scorePrefix = analysis.net_score > 0 ? `+${analysis.net_score}` : `${analysis.net_score}`;
    document.getElementById('res-score').textContent = scorePrefix;

    if (analysis.sentiment === 'POSITIF') {
        sentBadge.className = 'text-3xl font-extrabold tracking-tight mb-1 text-emerald-600 flex items-center gap-2';
        sentIcon.className = 'fa-solid fa-circle-check';
        sentBox.className = 'flex flex-col items-center justify-center p-6 rounded-2xl bg-emerald-50/70 border border-emerald-200 min-w-[220px] text-center';
        confBar.className = 'bg-emerald-500 h-1.5 rounded-full';
    } else if (analysis.sentiment === 'NEGATIF') {
        sentBadge.className = 'text-3xl font-extrabold tracking-tight mb-1 text-rose-600 flex items-center gap-2';
        sentIcon.className = 'fa-solid fa-circle-xmark';
        sentBox.className = 'flex flex-col items-center justify-center p-6 rounded-2xl bg-rose-50/70 border border-rose-200 min-w-[220px] text-center';
        confBar.className = 'bg-rose-500 h-1.5 rounded-full';
    } else {
        sentBadge.className = 'text-3xl font-extrabold tracking-tight mb-1 text-sky-600 flex items-center gap-2';
        sentIcon.className = 'fa-solid fa-scale-balanced';
        sentBox.className = 'flex flex-col items-center justify-center p-6 rounded-2xl bg-sky-50/70 border border-sky-200 min-w-[220px] text-center';
        confBar.className = 'bg-sky-500 h-1.5 rounded-full';
    }

    // Counts & Scores
    document.getElementById('res-pos-count').textContent = analysis.pos_count;
    document.getElementById('res-pos-score').textContent = `Skor: +${analysis.pos_score}`;
    document.getElementById('res-neg-count').textContent = analysis.neg_count;
    document.getElementById('res-neg-score').textContent = `Skor: -${analysis.neg_score}`;
    document.getElementById('res-neu-count').textContent = analysis.neu_count;

    // Kesimpulan
    document.getElementById('res-kesimpulan').innerHTML = analysis.kesimpulan.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Tags Positif Ditemukan
    const posTagsContainer = document.getElementById('res-pos-tags');
    posTagsContainer.innerHTML = '';
    const posKeys = Object.keys(analysis.matched_pos);
    if (posKeys.length > 0) {
        posKeys.forEach(k => {
            const count = analysis.matched_pos[k];
            const span = document.createElement('span');
            span.className = 'inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300';
            span.innerHTML = `<i class="fa-solid fa-check text-[10px]"></i> ${k} <span class="bg-emerald-200 px-1 rounded text-[10px]">${count}</span>`;
            posTagsContainer.appendChild(span);
        });
    } else {
        posTagsContainer.innerHTML = '<span class="text-xs text-slate-400 italic">Tidak ada kata positif yang terdeteksi</span>';
    }

    // Tags Negatif Ditemukan
    const negTagsContainer = document.getElementById('res-neg-tags');
    negTagsContainer.innerHTML = '';
    const negKeys = Object.keys(analysis.matched_neg);
    if (negKeys.length > 0) {
        negKeys.forEach(k => {
            const count = analysis.matched_neg[k];
            const span = document.createElement('span');
            span.className = 'inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300';
            span.innerHTML = `<i class="fa-solid fa-xmark text-[10px]"></i> ${k} <span class="bg-rose-200 px-1 rounded text-[10px]">${count}</span>`;
            negTagsContainer.appendChild(span);
        });
    } else {
        negTagsContainer.innerHTML = '<span class="text-xs text-slate-400 italic">Tidak ada kata negatif yang terdeteksi</span>';
    }

    // Highlighting HTML
    document.getElementById('res-highlighted-text').innerHTML = analysis.highlighted_html;

    // Scroll mulus ke card hasil
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Update data riwayat di tab riwayat
    loadStats();
    loadHistory();
}

// ================= KELOLA KATA KUNCI =================
async function loadKeywords() {
    try {
        const res = await fetch('/api/keywords');
        const data = await res.json();
        if (data.success) {
            allKeywords = data.keywords;
            updateKeywordCounts();
            renderKeywords();
        }
    } catch (err) {
        console.error('Gagal memuat kata kunci:', err);
    }
}

function updateKeywordCounts() {
    document.getElementById('count-kw-all').textContent = allKeywords.length;
    document.getElementById('count-kw-pos').textContent = allKeywords.filter(k => k.category === 'positif').length;
    document.getElementById('count-kw-neg').textContent = allKeywords.filter(k => k.category === 'negatif').length;
    document.getElementById('count-kw-pemkab').textContent = allKeywords.filter(k => k.category === 'pemkab').length;
    document.getElementById('count-kw-netral').textContent = allKeywords.filter(k => k.category === 'netral').length;
}

function filterKeywordsTab(cat) {
    currentCategoryFilter = cat;
    document.querySelectorAll('.kw-category-tab').forEach(btn => {
        btn.className = 'kw-category-tab px-4 py-2 text-xs font-semibold rounded-xl bg-white text-slate-600 border border-slate-200 hover:bg-slate-50';
    });
    const active = document.getElementById(`kw-tab-${cat}`);
    if (active) {
        active.className = 'kw-category-tab px-4 py-2 text-xs font-bold rounded-xl bg-slate-900 text-white shadow-sm';
    }
    renderKeywords();
}

function handleSearchKeywords() {
    renderKeywords();
}

function renderKeywords() {
    const container = document.getElementById('keywords-container');
    const searchVal = document.getElementById('kw-search-input').value.toLowerCase();

    let filtered = allKeywords;
    if (currentCategoryFilter !== 'all') {
        filtered = filtered.filter(k => k.category === currentCategoryFilter);
    }
    if (searchVal) {
        filtered = filtered.filter(k => k.keyword.toLowerCase().includes(searchVal));
    }

    if (filtered.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center py-8 text-xs text-slate-400">Tidak ada kata kunci yang cocok</div>';
        return;
    }

    container.innerHTML = filtered.map(k => {
        let badgeColor = 'bg-slate-100 text-slate-700 border-slate-200';
        let icon = 'fa-scale-balanced';
        if (k.category === 'positif') {
            badgeColor = 'bg-emerald-50 text-emerald-800 border-emerald-200';
            icon = 'fa-circle-check text-emerald-600';
        } else if (k.category === 'negatif') {
            badgeColor = 'bg-rose-50 text-rose-800 border-rose-200';
            icon = 'fa-circle-xmark text-rose-600';
        } else if (k.category === 'pemkab') {
            badgeColor = 'bg-sky-50 text-sky-800 border-sky-200';
            icon = 'fa-location-dot text-sky-600';
        }

        return `
            <div class="p-3 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between hover:shadow transition-all group">
                <div class="flex items-center gap-2.5 overflow-hidden">
                    <i class="fa-solid ${icon} text-sm flex-shrink-0"></i>
                    <div class="overflow-hidden">
                        <span class="text-xs font-bold text-slate-800 truncate block">${k.keyword}</span>
                        <div class="flex items-center gap-1.5 mt-0.5">
                            <span class="px-1.5 py-0.2 rounded text-[10px] font-semibold border ${badgeColor} uppercase">${k.category}</span>
                            <span class="text-[10px] text-slate-400">Bobot: ${k.weight}</span>
                        </div>
                    </div>
                </div>
                <button onclick="handleDeleteKeyword(${k.id})" title="Hapus kata kunci"
                    class="opacity-60 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 transition-all">
                    <i class="fa-regular fa-trash-can text-xs"></i>
                </button>
            </div>
        `;
    }).join('');
}

function openAddKeywordModal() {
    document.getElementById('add-keyword-modal').classList.remove('hidden');
    document.getElementById('new-kw-text').value = '';
    document.getElementById('add-kw-msg').classList.add('hidden');
}

function closeAddKeywordModal() {
    document.getElementById('add-keyword-modal').classList.add('hidden');
}

async function handleAddKeyword(e) {
    e.preventDefault();
    const keyword = document.getElementById('new-kw-text').value.trim();
    const category = document.getElementById('new-kw-category').value;
    const weight = document.getElementById('new-kw-weight').value;
    const msgBox = document.getElementById('add-kw-msg');

    try {
        const res = await fetch('/api/keywords', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keyword, category, weight })
        });
        const data = await res.json();

        msgBox.classList.remove('hidden');
        if (data.success) {
            msgBox.className = 'p-3 rounded-xl text-xs bg-emerald-50 text-emerald-800 border border-emerald-200';
            msgBox.textContent = data.message;
            loadKeywords();
            setTimeout(() => { closeAddKeywordModal(); }, 1000);
        } else {
            msgBox.className = 'p-3 rounded-xl text-xs bg-rose-50 text-rose-800 border border-rose-200';
            msgBox.textContent = data.message;
        }
    } catch (err) {
        msgBox.className = 'p-3 rounded-xl text-xs bg-rose-50 text-rose-800 border border-rose-200';
        msgBox.textContent = 'Gagal menyimpan kata kunci.';
        msgBox.classList.remove('hidden');
    }
}

async function handleDeleteKeyword(id) {
    if (!confirm('Hapus kata kunci ini?')) return;
    try {
        const res = await fetch(`/api/keywords/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadKeywords();
        }
    } catch (err) {
        alert('Gagal menghapus kata kunci');
    }
}

async function handleResetKeywords() {
    if (!confirm('Reset semua kata kunci ke daftar standar Pemerintah Kabupaten Bangka? Kata kunci kustom yang Anda buat akan diganti ke konfigurasi awal.')) return;
    try {
        const res = await fetch('/api/keywords/reset', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            alert(data.message);
            loadKeywords();
        }
    } catch (err) {
        alert('Gagal mereset kata kunci');
    }
}

// ================= RIWAYAT & STATISTIK =================
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        if (data.success) {
            const s = data.stats;
            document.getElementById('stat-total').textContent = s.total;
            document.getElementById('stat-pos').textContent = s.positif;
            document.getElementById('stat-neg').textContent = s.negatif;
            document.getElementById('stat-neu').textContent = s.netral;
            renderChart(s.positif, s.negatif, s.netral);
        }
    } catch (err) {
        console.error('Gagal memuat statistik:', err);
    }
}

function renderChart(pos, neg, neu) {
    const ctx = document.getElementById('sentimentPieChart');
    if (!ctx) return;

    if (sentimentChart) {
        sentimentChart.destroy();
    }

    const hasData = (pos + neg + neu) > 0;
    const dataValues = hasData ? [pos, neg, neu] : [1];
    const bgColors = hasData ? ['#10b981', '#f43f5e', '#0ea5e9'] : ['#e2e8f0'];
    const labels = hasData ? ['Positif', 'Negatif', 'Netral'] : ['Belum Ada Data'];

    sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: bgColors,
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 10,
                        font: { size: 10, family: 'Plus Jakarta Sans' }
                    }
                }
            },
            cutout: '70%'
        }
    });
}

async function loadHistory() {
    try {
        const res = await fetch('/api/history');
        const data = await res.json();
        if (data.success) {
            renderHistoryTable(data.history);
        }
    } catch (err) {
        console.error('Gagal memuat riwayat:', err);
    }
}

function renderHistoryTable(items) {
    const tbody = document.getElementById('history-table-body');
    if (!items || items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-8 text-slate-400">Belum ada riwayat analisis berita</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(h => {
        let sentClass = 'bg-slate-100 text-slate-700 border-slate-200';
        if (h.sentiment === 'POSITIF') sentClass = 'bg-emerald-100 text-emerald-800 border-emerald-200 font-bold';
        else if (h.sentiment === 'NEGATIF') sentClass = 'bg-rose-100 text-rose-800 border-rose-200 font-bold';
        else if (h.sentiment === 'NETRAL') sentClass = 'bg-sky-100 text-sky-800 border-sky-200 font-bold';

        const shortDate = h.created_at ? h.created_at.substring(0, 16) : '-';

        return `
            <tr class="hover:bg-slate-50/80 transition-colors">
                <td class="py-2.5 px-3 text-slate-500 whitespace-nowrap text-[11px]">${shortDate}</td>
                <td class="py-2.5 px-3 max-w-xs">
                    <span class="font-semibold text-slate-800 line-clamp-1" title="${h.title}">${h.title}</span>
                </td>
                <td class="py-2.5 px-3 text-slate-600 font-medium">${h.source || '-'}</td>
                <td class="py-2.5 px-3">
                    <span class="px-2 py-0.5 rounded text-[10px] border ${sentClass}">${h.sentiment}</span>
                </td>
                <td class="py-2.5 px-3 font-mono font-bold ${h.score > 0 ? 'text-emerald-600' : (h.score < 0 ? 'text-rose-600' : 'text-slate-600')}">
                    ${h.score > 0 ? '+' : ''}${h.score}
                </td>
                <td class="py-2.5 px-3 text-right whitespace-nowrap">
                    ${h.url && h.url.startsWith('http') ? `
                        <a href="${h.url}" target="_blank" class="p-1 text-slate-400 hover:text-emerald-600 mr-1" title="Kunjungi Link">
                            <i class="fa-solid fa-arrow-up-right-from-square"></i>
                        </a>
                    ` : ''}
                    <button onclick="handleDeleteHistory(${h.id})" class="p-1 text-slate-400 hover:text-rose-600" title="Hapus Riwayat">
                        <i class="fa-regular fa-trash-can"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

async function handleDeleteHistory(id) {
    if (!confirm('Hapus catatan riwayat analisis ini?')) return;
    try {
        const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadStats();
            loadHistory();
        }
    } catch (err) {
        alert('Gagal menghapus riwayat');
    }
}

async function clearAllHistoryConfirm() {
    if (!confirm('Hapus SEMUA riwayat analisis berita? Tindakan ini tidak dapat dibatalkan.')) return;
    try {
        const res = await fetch('/api/history/clear', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            loadStats();
            loadHistory();
        }
    } catch (err) {
        alert('Gagal membersihkan riwayat');
    }
}

