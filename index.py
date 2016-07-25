# Python StdLib
import os

# External Libraries
import jinja2
import webapp2
from google.appengine.ext import db

# Own Libraries
from tools import *
from User import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

SECRET = 'asdf'


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

    def delete_db_model(self, db_model):
        all_entries = db.GqlQuery("SELECT * FROM " + db_model)
        for entry in all_entries:
            entry.delete()


class BlogEntry(db.Model):

    subject = db.StringProperty(required=True)
    text = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    user_id = db.IntegerProperty(required=True)


class BlogArticleHandler(Handler):

    def render_new_post(self, subject="", text="", error=""):

        path = self.request.path
        blog_id = path[6:]  # returns only the id part of the URL

        b = BlogEntry.get_by_id(int(blog_id))

        self.render('permalink.html', blog_entry=b)

    def get(self):

        self.render_new_post()


class NewBlogPage(Handler):

    def render_new_post_page(self, subject="", blog="", error=""):
        self.render('new_post.html', subject=subject, blog=blog, error=error)

    def get(self):
        self.render_new_post_page()

    def post(self):
        subject = self.request.get('subject')
        text = self.request.get('text')

        str_user_id = self.read_secure_cookie('user_id')

        if subject and text and str_user_id:

            int_user_id = int(str_user_id)

            a = BlogEntry(subject=subject, text=text, user_id=int_user_id)
            a.put()

            # Creation of a Permalink
            link_id = a.key().id()
            self.redirect('/blog/' + str(link_id))
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


class DeletePage(Handler):
    def get(self):

        db_model = self.request.get('model')
        self.write(db_model)
        entries = db.GqlQuery("SELECT * FROM " + db_model)
        for entry in entries:
            entry.delete()


class MyBlogPage(Handler):

    def render_my_blog(self, str_user_id):

        query = "SELECT * FROM BlogEntry WHERE user_id=" + str_user_id + " ORDER BY created DESC";
        blog_entries = db.GqlQuery(query)
        #self.write(query)

        self.render('front.html', blog_entries=blog_entries)

    def get(self):
        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:
            self.render_my_blog(str_user_id)
        else:
            self.redirect('/signup')


class MainPage(Handler):

    def render_front(self):

        blog_entries = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY created DESC")

        self.render('front.html', blog_entries=blog_entries)

    def get(self):
        self.render_front()


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/myblog', MyBlogPage),
    ('/blog/NewPost', NewBlogPage),
    ('/blog/[0-9]+', BlogArticleHandler),
    ('/signup', SignUpPage),
    ('/welcome', WelcomePage),
    ('/login', LoginPage),
    ('/logout', LogoutPage),
    ('/delete', DeletePage)
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()
