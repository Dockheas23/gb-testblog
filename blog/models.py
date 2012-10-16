from google.appengine.ext import db

class BlogPost(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    author = db.UserProperty(auto_current_user_add=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)
    @classmethod
    def get_last(cls, num_posts):
        '''Get the last num_posts posts'''
        posts = cls.all()
        posts.order('-created')
        return posts.run(limit=num_posts)
    @classmethod
    def get_all(cls):
        '''Get all blog posts, in descending order of creation time'''
        posts = cls.all()
        posts.order('-created')
        return posts.run()

class Comment(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    author = db.UserProperty(auto_current_user_add=True)
    created = db.DateTimeProperty(auto_now_add=True)
