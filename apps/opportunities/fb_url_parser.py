import re
import urllib.request
import urllib.error

def fetch_fb_marketplace_url(url: str) -> dict:
    """
    Fetches visible OpenGraph metadata and description from a Facebook Marketplace URL.
    Returns a dict with 'raw_text', 'title', 'description', 'url', and status flags.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    }

    # Clean URL if needed
    cleaned_url = url.strip()
    if not cleaned_url.startswith(('http://', 'https://')):
        cleaned_url = 'https://' + cleaned_url

    req = urllib.request.Request(cleaned_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=6) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Extract og:title, og:description, og:image
            title_match = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', html, re.I) or \
                          re.search(r'<title>(.*?)</title>', html, re.I)
            desc_match = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', html, re.I) or \
                         re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.I)
            image_match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\'](.*?)["\']', html, re.I)

            title = title_match.group(1) if title_match else ""
            description = desc_match.group(1) if desc_match else ""
            image_url = image_match.group(1) if image_match else ""
            
            combined_text = f"{title} {description}".strip()
            
            return {
                "raw_text": combined_text if combined_text else cleaned_url,
                "title": title,
                "description": description,
                "image_url": image_url,
                "url": cleaned_url,
                "success": True
            }
    except Exception as e:
        # Fallback: Extract words/keywords from URL path
        url_slug = cleaned_url.split('/')[-1].replace('-', ' ').replace('_', ' ')
        return {
            "raw_text": f"Publicación de Marketplace {url_slug}",
            "title": url_slug,
            "description": "",
            "url": cleaned_url,
            "error": str(e),
            "success": False
        }
