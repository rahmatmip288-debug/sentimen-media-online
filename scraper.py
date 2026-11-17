import re
import urllib.parse
import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.google.com/',
    'Cache-Control': 'no-cache',
    'DNT': '1'
}

def extract_domain(url):
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return 'Online Media'

def scrape_news(url):
    """
    Mengambil artikel berita dari URL online.
    Mendukung berbagai portal berita nasional dan lokal Bangka Belitung.
    """
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url

    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
        response.raise_for_status()
        
        # Penanganan encoding
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Bersihkan elemen yang tidak relevan (iklan, script, komentar, nav)
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript', 'iframe', 'form']):
            element.decompose()

        # Bersihkan elemen widget iklan umum
        for ad_class in ['advertisement', 'ads-wrapper', 'baca-juga', 'related-article', 'social-share', 'komentar-wrap']:
            for ad_elem in soup.find_all(class_=re.compile(ad_class, re.I)):
                ad_elem.decompose()

        # 2. Ekstrak Judul
        title = ''
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()
        elif soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        elif soup.find('title'):
            title = soup.find('title').get_text().strip()
        
        # Bersihkan suffix nama portal pada judul (misal: " - Bangkapos.com", " | Detikcom")
        title = re.sub(r'\s*[-|–]\s*(Bangka Pos|Tribunnews|Kompas|Detik|Antara News|Babelpos|rri\.co\.id).*$', '', title, flags=re.I).strip()

        # 3. Ekstrak Tanggal Publikasi
        publish_date = ''
        og_time = soup.find('meta', property='article:published_time')
        if og_time and og_time.get('content'):
            publish_date = og_time['content'][:16].replace('T', ' ')
        else:
            time_tag = soup.find('time')
            if time_tag:
                publish_date = time_tag.get_text().strip()

        # 4. Ekstrak Konten / Isi Berita
        content_paragraphs = []

        # Selector spesifik untuk situs berita terkemuka
        specific_selectors = [
            '.detail__body-text',              # Detik
            '.read__content',                  # Kompas
            '.txt-article',                    # Bangkapos / Tribun
            '.side-article.txt-article',       # Tribunnews
            '.post-content',                   # Antara
            '.entry-content',                  # WordPress umum / Babelpos
            '.content-detail',                 # Media umum
            'div[itemprop="articleBody"]',     # Schema.org
            'article'                          # Standard HTML5 Article
        ]

        article_container = None
        for sel in specific_selectors:
            found = soup.select_one(sel)
            if found:
                article_container = found
                break

        if article_container:
            for p in article_container.find_all('p'):
                text = p.get_text().strip()
                # Filter kalimat pengganggu seperti "Baca juga:" atau "Simak video:"
                if len(text) > 25 and not re.match(r'^(Baca juga|Simak juga|Tonton juga|Editor:|Penulis:|Foto:)', text, re.I):
                    content_paragraphs.append(text)
        else:
            # Fallback jika tidak menemukan container spesifik
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if len(text) > 35 and not re.match(r'^(Baca juga|Copyright|All rights reserved)', text, re.I):
                    content_paragraphs.append(text)

        full_content = "\n\n".join(content_paragraphs).strip()

        if not full_content:
            return {
                'success': False,
                'error': 'Berita tidak dapat diekstrak secara otomatis dari halaman ini. Halaman mungkin menggunakan Javascript murni atau terproteksi. Silakan gunakan opsi Salin-Tempel (Manual Input).'
            }

        domain = extract_domain(url)

        return {
            'success': True,
            'url': url,
            'source': domain,
            'title': title or 'Berita Online Tanpa Judul',
            'publish_date': publish_date,
            'content': full_content,
            'paragraphs_count': len(content_paragraphs)
        }

    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Koneksi ke link berita timeout (melebihi batas waktu 15 detik).'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'Gagal mengakses link berita: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'Terjadi kesalahan saat memproses berita: {str(e)}'}

