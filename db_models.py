from google.appengine.ext import db


class BlogEntry(db.Model):

    subject = db.StringProperty(required=True)
    text = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now=True)
    user_id = db.IntegerProperty(required=True)
    username = db.StringProperty(required=True)
    likes = db.IntegerProperty(required=True, default=0)

    @classmethod
    def by_id(cls, uid):
        return BlogEntry.get_by_id(uid)


class Comment(db.Model):

    text = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    user_id = db.IntegerProperty(required=True)
    username = db.StringProperty(required=True)
    post_id = db.IntegerProperty(required=True)

    @classmethod
    def by_id(cls, uid):
        return Comment.get_by_id(uid)


class Like(db.Model):

    user_id = db.IntegerProperty(required=True)
    post_id = db.IntegerProperty(required=True)
    type = db.IntegerProperty(required=True)  # 1 for Like and -1 for Dislike

