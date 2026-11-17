import sqlite3
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bangka_sentimen.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabel Pengaturan (Termasuk Password Admin & Rotasi Berkala)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabel Riwayat Perubahan Password
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            note TEXT
        )
    ''')

    # Tabel Kata Kunci Sentimen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL, -- 'positif', 'negatif', 'netral', 'pemkab'
            weight REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabel Riwayat Analisis Berita
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            source TEXT,
            publish_date TEXT,
            content_snippet TEXT,
            sentiment TEXT NOT NULL, -- 'POSITIF', 'NEGATIF', 'NETRAL'
            score REAL,
            pos_count INTEGER,
            neg_count INTEGER,
            neu_count INTEGER,
            relevance TEXT,
            matched_pos TEXT,
            matched_neg TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Inisialisasi default password admin jika belum ada
    cursor.execute("SELECT value FROM settings WHERE key = 'admin_password'")
    if not cursor.fetchone():
        # Default password: adminbangka
        default_hash = generate_password_hash('adminbangka')
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO settings (key, value, updated_at) VALUES ('admin_password', ?, ?)", (default_hash, now))
        cursor.execute("INSERT INTO settings (key, value, updated_at) VALUES ('rotation_days', '30', ?)", (now,))
        cursor.execute("INSERT INTO settings (key, value, updated_at) VALUES ('last_password_change', ?, ?)", (now, now))
        cursor.execute("INSERT INTO password_logs (changed_at, note) VALUES (?, 'Password awal sistem diinisialisasi')", (now,))

    # Inisialisasi kata kunci default jika tabel masih kosong
    cursor.execute("SELECT COUNT(*) as cnt FROM keywords")
    count = cursor.fetchone()['cnt']
    if count == 0:
        default_keywords = [
            # KATA KUNCI POSITIF
            ('prestasi', 'positif', 1.5),
            ('penghargaan', 'positif', 1.5),
            ('sukses', 'positif', 1.2),
            ('berhasil', 'positif', 1.2),
            ('apresiasi', 'positif', 1.3),
            ('pembangunan', 'positif', 1.0),
            ('peningkatan', 'positif', 1.0),
            ('kemajuan', 'positif', 1.2),
            ('transparan', 'positif', 1.4),
            ('akuntabel', 'positif', 1.4),
            ('pelayanan prima', 'positif', 1.5),
            ('inovasi', 'positif', 1.3),
            ('beasiswa', 'positif', 1.2),
            ('bantuan', 'positif', 1.0),
            ('sejahtera', 'positif', 1.2),
            ('ramah investasi', 'positif', 1.3),
            ('pertumbuhan', 'positif', 1.1),
            ('panen raya', 'positif', 1.2),
            ('opini wtp', 'positif', 2.0),
            ('juara', 'positif', 1.3),
            ('terbaik', 'positif', 1.3),
            ('optimal', 'positif', 1.0),
            ('kolaborasi', 'positif', 1.0),
            ('responsif', 'positif', 1.2),
            ('penurunan stunting', 'positif', 1.5),
            ('surplus', 'positif', 1.3),
            ('memuaskan', 'positif', 1.3),
            ('kondusif', 'positif', 1.1),
            ('perbaikan', 'positif', 1.0),
            ('diresmikan', 'positif', 1.0),

            # KATA KUNCI NEGATIF
            ('korupsi', 'negatif', 2.0),
            ('gratifikasi', 'negatif', 1.8),
            ('pungli', 'negatif', 1.8),
            ('suap', 'negatif', 1.8),
            ('mangkrak', 'negatif', 1.7),
            ('keluhan', 'negatif', 1.2),
            ('kecewa', 'negatif', 1.3),
            ('rusak', 'negatif', 1.2),
            ('kerusakan', 'negatif', 1.2),
            ('banjir', 'negatif', 1.2),
            ('gagal', 'negatif', 1.5),
            ('lambat', 'negatif', 1.1),
            ('defisit', 'negatif', 1.4),
            ('polemik', 'negatif', 1.3),
            ('skandal', 'negatif', 1.8),
            ('unjuk rasa', 'negatif', 1.3),
            ('demonstrasi', 'negatif', 1.3),
            ('protes', 'negatif', 1.3),
            ('kritik', 'negatif', 1.1),
            ('merugikan', 'negatif', 1.4),
            ('pelanggaran', 'negatif', 1.5),
            ('temu dugaan', 'negatif', 1.4),
            ('bencana', 'negatif', 1.2),
            ('pengangguran', 'negatif', 1.3),
            ('kemiskinan', 'negatif', 1.3),
            ('stunting', 'negatif', 1.1),
            ('buruk', 'negatif', 1.4),
            ('ambruk', 'negatif', 1.6),
            ('penyimpangan', 'negatif', 1.7),
            ('diperiksa kejaksaan', 'negatif', 1.8),
            ('tersangka', 'negatif', 1.8),

            # KATA KUNCI RELEVANSI / PEMKAB BANGKA CONTEXT
            ('pemkab bangka', 'pemkab', 1.5),
            ('kabupaten bangka', 'pemkab', 1.5),
            ('bupati bangka', 'pemkab', 1.5),
            ('pj bupati bangka', 'pemkab', 1.5),
            ('wakil bupati bangka', 'pemkab', 1.4),
            ('sekda bangka', 'pemkab', 1.3),
            ('dprd bangka', 'pemkab', 1.3),
            ('dinas kabupaten bangka', 'pemkab', 1.2),
            ('sungailiat', 'pemkab', 1.2),
            ('belinyu', 'pemkab', 1.1),
            ('mendo barat', 'pemkab', 1.1),
            ('merawang', 'pemkab', 1.1),
            ('pemali', 'pemkab', 1.1),
            ('bakit', 'pemkab', 1.0),
            ('riau silip', 'pemkab', 1.1),
            ('puding besar', 'pemkab', 1.1),

            # KATA KUNCI NETRAL
            ('sosialisasi', 'netral', 1.0),
            ('rapat koordinasi', 'netral', 1.0),
            ('agenda', 'netral', 1.0),
            ('kunjungan kerja', 'netral', 1.0),
            ('audiensi', 'netral', 1.0),
            ('pelantikan', 'netral', 1.0),
            ('peninjauan', 'netral', 1.0),
            ('evaluasi', 'netral', 1.0),
            ('imbauan', 'netral', 1.0),
            ('surat edaran', 'netral', 1.0)
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO keywords (keyword, category, weight) VALUES (?, ?, ?)",
            default_keywords
        )

    conn.commit()
    conn.close()

# Password Management
def verify_admin_password(password):
    conn = get_db_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = 'admin_password'").fetchone()
    conn.close()
    if row and check_password_hash(row['value'], password):
        return True
    return False

def update_admin_password(new_password):
    conn = get_db_connection()
    new_hash = generate_password_hash(new_password)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'admin_password'", (new_hash, now))
    conn.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'last_password_change'", (now, now))
    conn.execute("INSERT INTO password_logs (changed_at, note) VALUES (?, 'Password berhasil diperbarui oleh Admin')", (now,))
    conn.commit()
    conn.close()
    return True

def get_password_info():
    conn = get_db_connection()
    last_change_row = conn.execute("SELECT value FROM settings WHERE key = 'last_password_change'").fetchone()
    rotation_row = conn.execute("SELECT value FROM settings WHERE key = 'rotation_days'").fetchone()
    logs = conn.execute("SELECT changed_at, note FROM password_logs ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()

    last_change_str = last_change_row['value'] if last_change_row else None
    rotation_days = int(rotation_row['value']) if rotation_row else 30

    days_since_change = 0
    is_overdue = False
    if last_change_str:
        try:
            last_date = datetime.datetime.strptime(last_change_str, '%Y-%m-%d %H:%M:%S')
            days_since_change = (datetime.datetime.now() - last_date).days
            if rotation_days > 0 and days_since_change >= rotation_days:
                is_overdue = True
        except Exception:
            pass

    return {
        'last_change': last_change_str,
        'rotation_days': rotation_days,
        'days_since_change': days_since_change,
        'is_overdue': is_overdue,
        'recent_logs': [dict(r) for r in logs]
    }

def set_rotation_days(days):
    conn = get_db_connection()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'rotation_days'", (str(days), now))
    conn.commit()
    conn.close()

# Keywords Management
def get_keywords():
    conn = get_db_connection()
    rows = conn.execute("SELECT id, keyword, category, weight FROM keywords ORDER BY category, keyword ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_keyword(keyword, category, weight=1.0):
    keyword = keyword.strip().lower()
    if not keyword:
        return False, "Kata kunci tidak boleh kosong"
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO keywords (keyword, category, weight) VALUES (?, ?, ?)", (keyword, category, weight))
        conn.commit()
        conn.close()
        return True, "Kata kunci berhasil ditambahkan"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Kata kunci sudah terdaftar"
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_keyword(keyword_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))
    conn.commit()
    conn.close()
    return True

def reset_default_keywords():
    conn = get_db_connection()
    conn.execute("DELETE FROM keywords")
    conn.commit()
    conn.close()
    init_db()
    return True

# Analysis History Management
def save_analysis(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO news_history 
        (title, url, source, publish_date, content_snippet, sentiment, score, pos_count, neg_count, neu_count, relevance, matched_pos, matched_neg)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('title', ''),
        data.get('url', ''),
        data.get('source', ''),
        data.get('publish_date', ''),
        data.get('content_snippet', ''),
        data.get('sentiment', 'NETRAL'),
        data.get('score', 0.0),
        data.get('pos_count', 0),
        data.get('neg_count', 0),
        data.get('neu_count', 0),
        data.get('relevance', 'Sedang'),
        data.get('matched_pos', ''),
        data.get('matched_neg', '')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_history(limit=50):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM news_history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_history_stats():
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) as count FROM news_history").fetchone()['count']
    pos = conn.execute("SELECT COUNT(*) as count FROM news_history WHERE sentiment = 'POSITIF'").fetchone()['count']
    neg = conn.execute("SELECT COUNT(*) as count FROM news_history WHERE sentiment = 'NEGATIF'").fetchone()['count']
    neu = conn.execute("SELECT COUNT(*) as count FROM news_history WHERE sentiment = 'NETRAL'").fetchone()['count']
    conn.close()
    return {
        'total': total,
        'positif': pos,
        'negatif': neg,
        'netral': neu
    }

def delete_history_item(history_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM news_history WHERE id = ?", (history_id,))
    conn.commit()
    conn.close()
    return True

def clear_all_history():
    conn = get_db_connection()
    conn.execute("DELETE FROM news_history")
    conn.commit()
    conn.close()
    return True

