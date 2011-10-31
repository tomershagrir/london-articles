
def get_current_site_posts(request):
    site = detect_current_site(request)
    return site['posts']
