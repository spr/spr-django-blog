from settings import AKISMET_API_KEY

def akismet(request, comment):
    from akismet import Akismet
    from django.contrib.sites.models import Site
    # Lifted from comment_utils by James Bennett
    if AKISMET_API_KEY == None:
        return False
    akismet_api = Akismet(key=AKISMET_API_KEY,
            blog_url='http://%s/' % Site.objects.get_current().domain)
    if akismet_api.verify_key():
        akismet_data = { 'comment_type': 'comment',
                'comment_author_url': comment.website,
                'comment_author_email': comment.email,
                'comment_author': comment.name,
                'referrer': request.META['HTTP_REFERER'],
                'user_ip': comment.ip,
                'user_agent': request.META['HTTP_USER_AGENT'] }
        return akismet_api.comment_check(comment.comment,
                data=akismet_data, build_data=True)
    return False
