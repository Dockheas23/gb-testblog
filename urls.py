from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('blog.views',
    url(r'^$', 'home', name='home'),
    url(r'^all$', 'all_posts', name='all'),
    url(r'^add$', 'add_post', name='add'),
    url(r'^view/(?P<post_id>\d+)$', 'view_post', name='view'),
    url(r'^edit/(?P<post_id>\d+)$', 'edit_post', name='edit'),
    url(r'^delete/(?P<post_id>\d+)$', 'delete_post', name='delete'),
    url(r'^comment/(?P<post_id>\d+)$', 'add_comment', name='comment'),
    url(r'^delete-comment/(?P<post_id>\d+)/(?P<comment_id>\d+)$',
        'delete_comment', name='delete-comment'),
)
