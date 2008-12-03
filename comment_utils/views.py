
from django.contrib.comments.models import Comment
from akismet import Akismet
from django.contrib.sites.models import Site
from django.utils.encoding import smart_str
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404

def _prepare_akismet_data(comment):
    return { 'comment_type': 'comment',
             'referrer': '',
             'comment_author': smart_str(comment.user_name),
             'comment_author_url': smart_str(comment.user_url),
             'comment_author_email': smart_str(comment.user_email),
             'user_ip': comment.ip_address,
             'user_agent': '' }


def _do_akismet(id, make_spam):
    """
    Mark the comment whose `id' is provided as spam or ham, depending
    on whether `make_spam' is True. Afterwards, redirect to the
    comments page in admin.
    """
    id = int(id)
    comment = get_object_or_404(Comment, pk=id)
    comment.is_public = not make_spam
    comment.save()

    akismet_api = Akismet(key=settings.AKISMET_API_KEY, blog_url='http://%s/' % Site.objects.get_current().domain)
    if akismet_api.verify_key():
        if make_spam:
            akismet_api.submit_spam(smart_str(comment.comment), data=_prepare_akismet_data(comment), build_data=True)
        else:
            akismet_api.submit_ham(smart_str(comment.comment), data=_prepare_akismet_data(comment), build_data=True)
    else:
        pass #TODO some sensible error
    return HttpResponseRedirect('/admin/comments/comment/%s/' % comment.pk)

@staff_member_required
def this_is_akismet_ham(request, id=None):
    """Mark a comment as not spam, make it public and redirect to its page
    in admin."""
    return _do_akismet(id, False)

@staff_member_required
def this_is_akismet_spam(request, id=None):
    """Mark a comment as spam, make it not public and redirect to its page
    in admin."""
    return _do_akismet(id, True)



