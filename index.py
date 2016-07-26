# Python StdLib
import os
import time

# External Libraries
import jinja2
import webapp2
from google.appengine.ext import db

# Own Libraries
from tools import *
from User import *
from db_models import *

# Initialize Jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    @staticmethod
    def render_str(template, params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'set-cookie',
            '%s=%s; Path=/' % (name, cookie_val)
        )

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')


class BlogArticleHandler(Handler):

    def render_new_post(self, subject="", text="", error=""):

        path = self.request.path
        blog_id = path[6:]  # returns only the id part of the URL

        b = BlogEntry.get_by_id(int(blog_id))

        self.render('permalink.html', blog_entry=b)

    def get(self):

        self.render_new_post()


class NewBlogPage(Handler):

    def render_new_post_page(self, subject="", text="", post_id="", error=""):
        self.render('new_post.html', subject=subject, text=text, post_id=post_id, error=error)

    def get(self):

        # Check first if user has valid cookie. Otherwise redirect...
        str_user_id = self.read_secure_cookie('user_id')
        if not str_user_id:
            self.redirect('/signup')
        else:
            # Check if this an existing post is edited
            str_post_id = self.request.get('post')
            if str_post_id:  # edit
                blog_entry = BlogEntry.get_by_id(int(str_post_id))
                self.render_new_post_page(subject=blog_entry.subject, text=blog_entry.text, post_id=str_post_id)
            else:  # new post
                self.render_new_post_page()

    def post(self):
        subject = self.request.get('subject')
        text = self.request.get('text')
        str_post_id = self.request.get('post_id')  # only nonempty if post is edited

        if subject and text:

            # get user object from cookie
            str_user_id = self.read_secure_cookie('user_id')
            int_user_id = int(str_user_id)
            user = User.by_id(int_user_id)

            if not str_post_id:  # new creation of blog post
                a = BlogEntry(subject=subject, text=text, user_id=int_user_id, username=user.name)
                a.put()

                # Creation of a Permalink
                link_id = a.key().id()
                self.redirect('/blog/' + str(link_id))
            else:  # blog post is only updated, not created
                int_post_id = int(str_post_id)
                blog_entry = BlogEntry.by_id(int_post_id)
                blog_entry.text = text  # update existing blog entry with edited value
                blog_entry.subject = subject  # update existing blog entry with edited value
                blog_entry.put()
                self.redirect('/blog/' + str_post_id)
        else:
            error = "We need both a subject and content"
            self.render_new_post_page(subject, text, error)


class SignUpPage(Handler):

    def get(self):
        self.render("signup.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        if not password == verify:  # invalid user data
            self.render('signup.html', username=username, error_password="Passwords do not match")
        else:  # valid user data
            # make sure the user doesn't already exist
            u = User.by_name(username)
            if u:
                msg = 'That user already exists.'
                self.render('signup.html', error_username=msg)
            else:
                u = User.register(username, password, email)
                u.put()

                self.login(u)
                self.redirect('/welcome')


class LoginPage(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.by_name(username)

        if not user:
            error_username = "This username does not exist"
            self.render('login.html', error_username=error_username)
        elif not valid_pw(username, password, user.pw_hash):
            error_password = "The password is not correct"
            self.render('login.html', username=username, error_password=error_password)
        else:
            self.login(user)  # Sets the cookie with user id
            self.redirect('/welcome')


class LogoutPage(Handler):
    def get(self):
        self.logout()  # Sets the user id cookie to an empty value
        self.redirect('/signup')


class WelcomePage(Handler):

    def get(self):
        """
        Render Welcome Page and greet the user.
        The user id is read from the cookie "user_id"
        """
        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:  # user_id either empty or hashed user_id did not match the hash in cookie
            user_id = int(str_user_id)
            user = User.by_id(user_id)
            self.render("welcome.html", username=user.name)

        else:
            self.redirect('/signup')


class MyBlogPage(Handler):

    def render_my_blog(self, str_user_id):

        query = "SELECT * FROM BlogEntry WHERE user_id=" + str_user_id + " ORDER BY created DESC";
        blog_entries = db.GqlQuery(query)

        self.render('front.html', blog_entries=blog_entries, user_id=str_user_id)

    def get(self):
        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:
            self.render_my_blog(str_user_id)
        else:
            self.redirect('/signup')

    def post(self):  # implementation of "delete" button
        str_post_id = self.request.get('post')
        int_post_id = int(str_post_id)
        blog_entry = BlogEntry.by_id(int_post_id)
        blog_entry.delete()

        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:
            time.sleep(1)  # To prevent "Eventual Inconsistency" in Datastore
            self.render_my_blog(str_user_id)
        else:
            self.redirect('/signup')


class MainPage(Handler):

    def render_front(self, str_user_id, err_post_id="", err_msg=""):

        blog_entries = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY created DESC")
        comments = db.GqlQuery("SELECT * FROM Comment ORDER BY created DESC")
        self.render('front.html',
                    blog_entries=blog_entries,
                    user_id=str_user_id,
                    err_post_id=err_post_id,
                    err_msg=err_msg,
                    comments=comments)

    def delayed_render_front(self):
        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:
            time.sleep(1)  # To prevent "Eventual Inconsistency" in Datastore
            self.render_front(str_user_id)
        else:
            self.redirect('/signup')

    def get(self):
        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:
            self.render_front(str_user_id)
        else:
            self.redirect('/signup')

    def post(self):  # implementation of delete, like, comment buttons
        str_post_id = self.request.get('post')
        str_like_val = self.request.get('like')  # has the format 1|post_id or -1|post_id
        str_comment = self.request.get('comment')
        str_edit_comment = self.request.get('edit_comment')  # This is the id of the original comment
        str_delete_comment = self.request.get('delete_comment')  # This is the id of the original comment

        if str_like_val:  # User likes/dislikes post
            str_like = str_like_val.split('|')[0]  # +1 for like or -1 for dislike
            str_post_id = str_like_val.split('|')[1]
            int_post_id = int(str_post_id)

            # check if user already liked this post
            str_user_id = self.read_secure_cookie('user_id')
            like_entries = db.GqlQuery("SELECT * "
                                       "FROM Like "
                                       "WHERE user_id=" + str_user_id +
                                       " AND post_id=" + str_post_id)

            if like_entries.get():  # User already liked/disliked
                self.render_front(str_user_id, str_post_id, "You already liked this post")
            else:
                blog_entry = BlogEntry.by_id(int_post_id)
                blog_entry.likes += int(str_like)
                blog_entry.put()

                # Update Like table
                int_user_id = int(str_user_id)
                like = Like(post_id=int_post_id, user_id=int_user_id)
                like.put()

                self.delayed_render_front()

        elif str_comment:  # User comments on post
            str_user_id = self.read_secure_cookie('user_id')
            int_user_id = int(str_user_id)

            user = User.by_id(int_user_id)
            str_username = user.name

            str_post_id = self.request.get('post_id')
            int_post_id = int(str_post_id)

            db_comment = Comment(text=str_comment,
                                 user_id=int_user_id,
                                 post_id=int_post_id,
                                 username=str_username)
            db_comment.put()

            self.delayed_render_front()

        elif str_edit_comment:
            str_new_comment = self.request.get('comment-text')

            # get original comment and adjust
            comment = Comment.by_id(int(str_edit_comment))
            comment.text = str_new_comment
            comment.put()

            self.delayed_render_front()

        elif str_delete_comment:
            # get original comment and delete
            comment = Comment.by_id(int(str_delete_comment))
            comment.delete()

            self.delayed_render_front()

        else:  # User deletes a post
            int_post_id = int(str_post_id)
            blog_entry = BlogEntry.by_id(int_post_id)
            blog_entry.delete()

            # delete all comments that are associated with post
            comments = db.GqlQuery("SELECT * FROM Comment WHERE post_id=" + str_post_id)
            for comment in comments:
                comment.delete()

            # delete all likes that are associated with post
            likes = db.GqlQuery("SELECT * FROM Like WHERE post_id=" + str_post_id)
            for like in likes:
                like.delete()

            self.delayed_render_front()


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/myblog', MyBlogPage),
    ('/blog/NewPost', NewBlogPage),
    ('/blog/[0-9]+', BlogArticleHandler),
    ('/signup', SignUpPage),
    ('/welcome', WelcomePage),
    ('/login', LoginPage),
    ('/logout', LogoutPage)
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()
