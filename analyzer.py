import re
import html
from database import get_keywords

NEGATORS = [
    'tidak', 'tak', 'bukan', 'belum', 'tanpa', 'kurang', 'minim', 'jangan', 'batal', 'gagal'
]

BOOSTERS = [
    'sangat', 'amat', 'luar biasa', 'sungguh', 'terbukti', 'signifikan', 'besar', 'makin', 'semakin'
]

def analyze_sentiment(title, content, custom_keywords=None):
    """
    Menganalisis sentimen teks berita terhadap jalannya Pemerintah Kabupaten Bangka.
    Menggunakan pencocokan kata kunci terbobot dengan dukungan negasi dan konteks lokal.
    """
    if custom_keywords is None:
        db_keywords = get_keywords()
    else:
        db_keywords = custom_keywords

    pos_keywords = [k for k in db_keywords if k['category'] == 'positif']
    neg_keywords = [k for k in db_keywords if k['category'] == 'negatif']
    neu_keywords = [k for k in db_keywords if k['category'] == 'netral']
    pemkab_keywords = [k for k in db_keywords if k['category'] == 'pemkab']

    # Gabungkan teks (judul diberi bobot ganda)
    full_text = f"{title}\n{content}"
    full_lower = full_text.lower()
    
    # 1. Cek Relevansi Terhadap Pemkab Bangka
    pemkab_matches = {}
    total_pemkab_hits = 0
    for kw in pemkab_keywords:
        term = kw['keyword'].lower()
        pattern = r'\b' + re.escape(term) + r'\b'
        hits = len(re.findall(pattern, full_lower))
        if hits > 0:
            pemkab_matches[term] = hits
            total_pemkab_hits += hits

    if total_pemkab_hits >= 4:
        relevance = 'Sangat Tinggi (Fokus Pemkab Bangka)'
    elif total_pemkab_hits >= 1:
        relevance = 'Cukup Relevan (Menyebut Bangka/Pemda)'
    else:
        relevance = 'Rendah (Konteks Bangka Terbatas)'

    # 2. Deteksi Kata Sentimen & Negasi
    # Tokenisasi berbasis kalimat untuk mendeteksi konteks negator di sekitar kata
    sentences = re.split(r'[.!?\n]+', full_text)

    pos_matches = {}
    neg_matches = {}
    neu_matches = {}

    pos_score = 0.0
    neg_score = 0.0

    # Peta kata kunci untuk lookup cepat
    pos_dict = {k['keyword'].lower(): float(k.get('weight', 1.0)) for k in pos_keywords}
    neg_dict = {k['keyword'].lower(): float(k.get('weight', 1.0)) for k in neg_keywords}
    neu_dict = {k['keyword'].lower(): float(k.get('weight', 1.0)) for k in neu_keywords}

    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        s_lower = s_clean.lower()
        words = re.findall(r'\b\w+\b', s_lower)

        # Cek kata kunci netral
        for term, weight in neu_dict.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            hits = len(re.findall(pattern, s_lower))
            if hits > 0:
                neu_matches[term] = neu_matches.get(term, 0) + hits

        # Cek kata kunci positif
        for term, weight in pos_dict.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            for match in re.finditer(pattern, s_lower):
                # Periksa apakah ada negator sebelum kata ini (3 token sebelumnya)
                start_idx = match.start()
                text_before = s_lower[max(0, start_idx - 30):start_idx]
                tokens_before = re.findall(r'\b\w+\b', text_before)
                recent_before = tokens_before[-3:] if tokens_before else []

                has_negator = any(neg in recent_before for neg in NEGATORS)
                has_booster = any(boost in recent_before for boost in BOOSTERS)

                multiplier = 1.3 if has_booster else 1.0

                if has_negator:
                    # Ternegasi: misal "tidak berhasil", "kurang transparan" -> masuk negatif
                    flipped_term = f"[ternegasi] {recent_before[-1]} {term}"
                    neg_matches[flipped_term] = neg_matches.get(flipped_term, 0) + 1
                    neg_score += (weight * 1.0)
                else:
                    pos_matches[term] = pos_matches.get(term, 0) + 1
                    pos_score += (weight * multiplier)

        # Cek kata kunci negatif
        for term, weight in neg_dict.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            for match in re.finditer(pattern, s_lower):
                start_idx = match.start()
                text_before = s_lower[max(0, start_idx - 30):start_idx]
                tokens_before = re.findall(r'\b\w+\b', text_before)
                recent_before = tokens_before[-3:] if tokens_before else []

                has_negator = any(neg in recent_before for neg in NEGATORS)
                has_booster = any(boost in recent_before for boost in BOOSTERS)

                multiplier = 1.3 if has_booster else 1.0

                if has_negator:
                    # Ternegasi: misal "tidak ada korupsi", "bukan kegagalan" -> masuk positif
                    flipped_term = f"[ternegasi] {recent_before[-1]} {term}"
                    pos_matches[flipped_term] = pos_matches.get(flipped_term, 0) + 1
                    pos_score += (weight * 0.9)
                else:
                    neg_matches[term] = neg_matches.get(term, 0) + 1
                    neg_score += (weight * multiplier)

    # 3. Klasifikasi Sentimen Final
    total_pos_count = sum(pos_matches.values())
    total_neg_count = sum(neg_matches.values())
    total_neu_count = sum(neu_matches.values())

    net_score = pos_score - neg_score
    total_sentimen_score = pos_score + neg_score

    if total_sentimen_score == 0:
        sentiment = 'NETRAL'
        confidence = 85.0
        pos_ratio = 33.3
        neg_ratio = 33.3
        neu_ratio = 33.4
    else:
        pos_ratio = round((pos_score / total_sentimen_score) * 100, 1)
        neg_ratio = round((neg_score / total_sentimen_score) * 100, 1)
        neu_ratio = round(max(0, 100 - (pos_ratio + neg_ratio)), 1)

        diff = pos_score - neg_score
        if diff >= 1.2:
            sentiment = 'POSITIF'
            confidence = min(98.0, 60.0 + (pos_ratio * 0.38))
        elif diff <= -1.2:
            sentiment = 'NEGATIF'
            confidence = min(98.0, 60.0 + (neg_ratio * 0.38))
        else:
            sentiment = 'NETRAL'
            confidence = 75.0

    # 4. Ringkasan Kesimpulan Analisis
    kesimpulan_parts = []
    if sentiment == 'POSITIF':
        kesimpulan_parts.append(f"Berita mencerminkan sentimen **POSITIF** terhadap jalannya Pemerintah Kabupaten Bangka.")
        if pos_matches:
            top_pos = sorted(pos_matches.items(), key=lambda x: x[1], reverse=True)[:3]
            top_str = ", ".join([f"'{k}' ({v}x)" for k, v in top_pos])
            kesimpulan_parts.append(f"Didukung oleh kata kunci apresiasi/keberhasilan seperti {top_str}.")
    elif sentiment == 'NEGATIF':
        kesimpulan_parts.append(f"Berita mencerminkan sentimen **NEGATIF** atau sorotan kritis terhadap Pemerintah Kabupaten Bangka.")
        if neg_matches:
            top_neg = sorted(neg_matches.items(), key=lambda x: x[1], reverse=True)[:3]
            top_str = ", ".join([f"'{k}' ({v}x)" for k, v in top_neg])
            kesimpulan_parts.append(f"Ditemukan indikasi kendala/kritik publik seperti {top_str}.")
    else:
        kesimpulan_parts.append(f"Berita berbobot **NETRAL / INFORMATIF**.")
        kesimpulan_parts.append("Konten didominasi oleh agenda kegiatan formal, sosialisasi kedinasan, atau memiliki keseimbangan fakta positif dan catatan evaluasi.")

    kesimpulan = " ".join(kesimpulan_parts)

    # 5. Highlight Teks Asli (Positif Hijau, Negatif Merah, Pemkab Biru)
    highlighted_content = generate_highlighted_html(content, pos_keywords, neg_keywords, pemkab_keywords)

    return {
        'sentiment': sentiment,
        'confidence': round(confidence, 1),
        'net_score': round(net_score, 2),
        'pos_score': round(pos_score, 2),
        'neg_score': round(neg_score, 2),
        'pos_ratio': pos_ratio,
        'neg_ratio': neg_ratio,
        'neu_ratio': neu_ratio,
        'pos_count': total_pos_count,
        'neg_count': total_neg_count,
        'neu_count': total_neu_count,
        'matched_pos': pos_matches,
        'matched_neg': neg_matches,
        'matched_pemkab': pemkab_matches,
        'relevance': relevance,
        'kesimpulan': kesimpulan,
        'highlighted_html': highlighted_content
    }

def generate_highlighted_html(text, pos_keywords, neg_keywords, pemkab_keywords):
    """
    Menghasilkan HTML dengan penyorotan warna cerdas untuk teks berita.
    """
    if not text:
        return ""

    escaped_text = html.escape(text)

    # Kata kunci terurut dari yang terpanjang agar frasa multi-kata tertangkap lebih dulu
    all_kws = []
    for k in pos_keywords:
        all_kws.append((k['keyword'], 'pos'))
    for k in neg_keywords:
        all_kws.append((k['keyword'], 'neg'))
    for k in pemkab_keywords:
        all_kws.append((k['keyword'], 'pemkab'))

    all_kws.sort(key=lambda x: len(x[0]), reverse=True)

    # Ganti kata kunci dengan span bersorot warna
    for kw, cat in all_kws:
        term = html.escape(kw)
        pattern = re.compile(r'\b(' + re.escape(term) + r')\b', re.IGNORECASE)
        if cat == 'pos':
            replacement = r'<mark class="bg-emerald-100 text-emerald-800 font-semibold px-1 rounded shadow-sm" title="Kata Kunci Positif">\1</mark>'
        elif cat == 'neg':
            replacement = r'<mark class="bg-rose-100 text-rose-800 font-semibold px-1 rounded shadow-sm" title="Kata Kunci Negatif">\1</mark>'
        else:
            replacement = r'<mark class="bg-sky-100 text-sky-800 font-medium px-1 rounded" title="Konteks Pemkab Bangka">\1</mark>'
        escaped_text = pattern.sub(replacement, escaped_text)

    # Format paragraf
    paragraphs = escaped_text.split('\n\n')
    formatted = "".join([f"<p class='mb-4 leading-relaxed'>{p.strip()}</p>" for p in paragraphs if p.strip()])
    return formatted

