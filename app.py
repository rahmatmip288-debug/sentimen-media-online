import os
import io
import csv
import json
from flask import Flask, render_template, request, jsonify, session, send_file, Response
from database import (
    init_db, verify_admin_password, update_admin_password, get_password_info,
    set_rotation_days, get_keywords, add_keyword, delete_keyword, reset_default_keywords,
    save_analysis, get_history, get_history_stats, delete_history_item, clear_all_history
)
from scraper import scrape_news
from analyzer import analyze_sentiment

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inisialisasi Database saat aplikasi dijalankan
init_db()

@app.route('/')
def index():
    return render_template('index.html')

# ================= AUTHENTICATION & PASSWORD MANAGEMENT =================
@app.route('/api/auth-status', methods=['GET'])
def auth_status():
    is_logged_in = session.get('is_logged_in', False)
    pwd_info = get_password_info()
    return jsonify({
        'is_logged_in': is_logged_in,
        'password_info': pwd_info
    })

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    password = data.get('password', '').strip()
    
    if not password:
        return jsonify({'success': False, 'message': 'Password wajib diisi'}), 400

    if verify_admin_password(password):
        session['is_logged_in'] = True
        return jsonify({
            'success': True,
            'message': 'Login berhasil',
            'password_info': get_password_info()
        })
    else:
        return jsonify({'success': False, 'message': 'Password salah, silakan coba lagi'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('is_logged_in', None)
    return jsonify({'success': True, 'message': 'Berhasil keluar sistem'})

@app.route('/api/admin/change-password', methods=['POST'])
def change_password():
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Akses ditolak. Silakan login terlebih dahulu'}), 403

    data = request.get_json() or {}
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': 'Password lama dan baru wajib diisi'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'Konfirmasi password baru tidak cocok'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password baru minimal 6 karakter'}), 400

    if not verify_admin_password(old_password):
        return jsonify({'success': False, 'message': 'Password saat ini (lama) tidak sesuai'}), 400

    update_admin_password(new_password)
    return jsonify({
        'success': True,
        'message': 'Password Admin berhasil diperbarui!',
        'password_info': get_password_info()
    })

@app.route('/api/admin/rotation-settings', methods=['POST'])
def update_rotation_settings():
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Akses ditolak'}), 403

    data = request.get_json() or {}
    rotation_days = data.get('rotation_days', 30)
    try:
        rotation_days = int(rotation_days)
    except ValueError:
        return jsonify({'success': False, 'message': 'Nilai hari rotasi tidak valid'}), 400

    set_rotation_days(rotation_days)
    return jsonify({
        'success': True,
        'message': f'Periode rotasi password berhasil diatur ke {rotation_days} hari',
        'password_info': get_password_info()
    })

# ================= ANALISIS SENTIMEN =================
@app.route('/api/analyze-url', methods=['POST'])
def api_analyze_url():
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401

    data = request.get_json() or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'success': False, 'message': 'Link berita online tidak boleh kosong'}), 400

    # 1. Scraping Berita
    scrape_res = scrape_news(url)
    if not scrape_res.get('success'):
        return jsonify({
            'success': False,
            'message': scrape_res.get('error', 'Gagal mengambil berita dari link yang diberikan')
        }), 400

    title = scrape_res.get('title', 'Berita Online')
    content = scrape_res.get('content', '')
    source = scrape_res.get('source', '')
    publish_date = scrape_res.get('publish_date', '')

    # 2. Analisis Sentimen
    analysis = analyze_sentiment(title, content)

    # 3. Simpan ke Riwayat
    history_data = {
        'title': title,
        'url': url,
        'source': source,
        'publish_date': publish_date,
        'content_snippet': content[:300] + '...' if len(content) > 300 else content,
        'sentiment': analysis['sentiment'],
        'score': analysis['net_score'],
        'pos_count': analysis['pos_count'],
        'neg_count': analysis['neg_count'],
        'neu_count': analysis['neu_count'],
        'relevance': analysis['relevance'],
        'matched_pos': json.dumps(analysis['matched_pos']),
        'matched_neg': json.dumps(analysis['matched_neg'])
    }
    history_id = save_analysis(history_data)

    return jsonify({
        'success': True,
        'history_id': history_id,
        'article': {
            'title': title,
            'url': url,
            'source': source,
            'publish_date': publish_date,
            'content': content
        },
        'analysis': analysis
    })

@app.route('/api/analyze-text', methods=['POST'])
def api_analyze_text():
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401

    data = request.get_json() or {}
    title = data.get('title', 'Teks Berita Manual').strip()
    content = data.get('content', '').strip()
    source = data.get('source', 'Input Manual').strip()
    url = data.get('url', '').strip() or 'https://input-manual'

    if not content:
        return jsonify({'success': False, 'message': 'Konten berita tidak boleh kosong'}), 400

    analysis = analyze_sentiment(title, content)

    history_data = {
        'title': title,
        'url': url,
        'source': source,
        'publish_date': 'Manual',
        'content_snippet': content[:300] + '...' if len(content) > 300 else content,
        'sentiment': analysis['sentiment'],
        'score': analysis['net_score'],
        'pos_count': analysis['pos_count'],
        'neg_count': analysis['neg_count'],
        'neu_count': analysis['neu_count'],
        'relevance': analysis['relevance'],
        'matched_pos': json.dumps(analysis['matched_pos']),
        'matched_neg': json.dumps(analysis['matched_neg'])
    }
    history_id = save_analysis(history_data)

    return jsonify({
        'success': True,
        'history_id': history_id,
        'article': {
            'title': title,
            'url': url,
            'source': source,
            'publish_date': 'Manual',
            'content': content
        },
        'analysis': analysis
    })

# ================= KELOLA KATA KUNCI =================
@app.route('/api/keywords', methods=['GET'])
def api_get_keywords():
    kws = get_keywords()
    return jsonify({'success': True, 'keywords': kws})

@app.route('/api/keywords', methods=['POST'])
def api_add_keyword():
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401

    data = request.get_json() or {}
    keyword = data.get('keyword', '').strip()
    category = data.get('category', 'positif').strip().lower()
    weight = float(data.get('weight', 1.0))

    if category not in ['positif', 'negatif', 'netral', 'pemkab']:
        return jsonify({'success': False, 'message': 'Kategori tidak valid'}), 400

    success, msg = add_keyword(keyword, category, weight)
    if success:
        return jsonify({'success': True, 'message': msg})
    else:
        return jsonify({'success': False, 'message': msg}), 400

@app.route('/api/keywords/<int:kw_id>', methods=['DELETE'])
def api_delete_keyword(kw_id):
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401

    delete_keyword(kw_id)
    return jsonify({'success': True, 'message': 'Kata kunci berhasil dihapus'})

@app.route('/api/keywords/reset', methods=['POST'])
def api_reset_keywords():
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401

    reset_default_keywords()
    return jsonify({'success': True, 'message': 'Kata kunci berhasil direset ke standar Pemkab Bangka'})

# ================= RIWAYAT & STATISTIK =================
@app.route('/api/history', methods=['GET'])
def api_get_history():
    history = get_history(limit=100)
    return jsonify({'success': True, 'history': history})

@app.route('/api/stats', methods=['GET'])
def api_get_stats():
    stats = get_history_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/history/<int:history_id>', methods=['DELETE'])
def api_delete_history(history_id):
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401

    delete_history_item(history_id)
    return jsonify({'success': True, 'message': 'Riwayat berhasil dihapus'})

@app.route('/api/history/clear', methods=['POST'])
def api_clear_history():
    if not session.get('is_logged_in', False):
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401

    clear_all_history()
    return jsonify({'success': True, 'message': 'Semua riwayat berhasil dibersihkan'})

@app.route('/api/export-history', methods=['GET'])
def api_export_history():
    history = get_history(limit=500)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Tanggal', 'Judul Berita', 'Sumber', 'Sentimen', 'Skor', 'Kata Positif', 'Kata Negatif', 'Relevansi Pemkab', 'URL'])
    
    for h in history:
        writer.writerow([
            h['id'],
            h['created_at'],
            h['title'],
            h['source'],
            h['sentiment'],
            h['score'],
            h['pos_count'],
            h['neg_count'],
            h['relevance'],
            h['url']
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=laporan_sentimen_pemkab_bangka.csv"}
    )

if __name__ == '__main__':
    print("=" * 60)
    print(" SISTEM ANALISIS SENTIMEN BERITA PEMERINTAH KABUPATEN BANGKA ")
    print(" Server berjalan di: http://localhost:5000")
    print(" Password default admin: adminbangka")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)

