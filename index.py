# Python StdLib
import os
import time

# External Libraries
import jinja2
import webapp2
from google.appengine.ext import db

# Own Libraries
import tools
import User
from db_models import BlogEntry, Comment, Like

# Initialize Jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    """
    Base class all other request handlers in this script inherit from
    """

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    @staticmethod
    def render_str(template, params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, kw))

    def set_secure_cookie(self, name, val):
        cookie_val = tools.make_secure_val(val)
        self.response.headers.add_header(
            'set-cookie',
            '%s=%s; Path=/' % (name, cookie_val)
        )

    def read_secure_cookie(self, name):
        """
        Returns the value of a cookie only if it is valid
        :param name: Name of Cookie
        :return: value of cookie only if valid
        """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and tools.check_secure_val(cookie_val)

    def login(self, user):
        """
        Method is called when a user logs in.
        A secure authentication cookie is set.
        :param user: User database object
        """
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        """
        Method is called when a user logs out.
        Authentication cookie is set empty.
        """
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')


class BlogArticleHandler(Handler):
    def render_new_post(self):
        """
        Render permalink page which is created after a new post
        has been created
        """
        path = self.request.path  # returns URL
        blog_id = path[6:]  # returns only the id part of the URL

        b = BlogEntry.get_by_id(int(blog_id))

        return self.render('permalink.html', blog_entry=b)

    def get(self):
        str_user_id = self.read_secure_cookie('user_id')
        if not str_user_id:
            return self.redirect('/blog/signup')
        else:
            return self.render_new_post()


class NewBlogPage(Handler):
    def render_new_post_page(self, subject="", text="", error=""):
        return self.render('new_post.html',
                    subject=subject,
                    text=text,
                    error=error)

    def get(self):
        """
        Get Method is called if user wants to create a new
        post.
        """

        # Check first if user has valid cookie. Otherwise redirect...
        str_user_id = self.read_secure_cookie('user_id')
        if not str_user_id:
            return self.redirect('/blog/signup')
        else:
            return self.render_new_post_page()

    def post(self):
        """
        Post method is called when a new post is created
        """

        # Check first if user has valid cookie. Otherwise redirect...
        str_user_id = self.read_secure_cookie('user_id')
        if not str_user_id:
            return self.redirect('/blog/signup')
        else:
            subject = self.request.get('subject')
            text = self.request.get('text')

            if subject and text:

                # get user object from cookie
                str_user_id = self.read_secure_cookie('user_id')
                int_user_id = int(str_user_id)
                user = User.User.by_id(int_user_id)

                blog_entry = BlogEntry(subject=subject,
                                       text=text,
                                       user_id=int_user_id,
                                       username=user.name)
                blog_entry.put()

                # Creation of a Permalink
                link_id = blog_entry.key().id()
                return self.redirect('/blog/' + str(link_id))
            else:
                error = "We need both a subject and content"
                return self.render_new_post_page(subject, text, error)


class EditBlogPage(Handler):
    def render_edit_post_page(self, subject="", text="", post_id="", error=""):
        return self.render('edit_post.html',
                           subject=subject,
                           text=text,
                           post_id=post_id,
                           error=error)

    def get(self):
        """
        Get Method is called either if user wants to edit an existing
        post from the main blog page.
        """

        # Check first if user has valid cookie. Otherwise redirect...
        str_user_id = self.read_secure_cookie('user_id')
        if not str_user_id:
            return self.redirect('/blog/signup')
        else:
            # an existing post is edited
            str_post_id = self.request.get('post_id')
            blog_entry = BlogEntry.get_by_id(int(str_post_id))
            return self.render_edit_post_page(subject=blog_entry.subject,
                                              text=blog_entry.text,
                                              post_id=str_post_id)

    def post(self):
        """
        Post method is called when an existing post is edited.
        """

        # Check first if user has valid cookie. Otherwise redirect...
        str_user_id = self.read_secure_cookie('user_id')
        if not str_user_id:
            return self.redirect('/blog/signup')
        else:
            subject = self.request.get('subject')
            text = self.request.get('text')

            str_post_id = self.request.get('post_id')
            int_post_id = int(str_post_id)

            if subject and text:

                blog_entry = BlogEntry.by_id(int_post_id)
                blog_entry.text = text  # update existing blog entry with edited value
                blog_entry.subject = subject  # update existing blog entry with edited value
                blog_entry.put()

                return self.redirect('/blog/' + str_post_id)
            else:
                error = "We need both a subject and content"
                return self.render_edit_post_page(subject=subject,
                                                  text=text,
                                                  post_id=str_post_id,
                                                  error=error)


class SignUpPage(Handler):
    def get(self):
        return self.render("signup.html")

    def post(self):
        """
        Post method is called when user signs up for blog.
        Validation functions are implemented in tools.py.
        After successful login the user is redirected to a "welcome" page.
        """
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        if not username:
            return self.render('signup.html', username=username, email=email,
                               error_username="Username is empty")
        elif not tools.valid_username(username):
            return self.render('signup.html', username=username, email=email,
                               error_username="Username does not match "
                                       "required specifications")
        elif not password:
            return self.render('signup.html', username=username, email=email,
                               error_password="Password is empty")
        elif not tools.valid_password(password):
            return self.render('signup.html', username=username, email=email,
                               error_password="Password does not match "
                                       "required specifications")
        elif not password == verify:  # invalid user data
            return self.render('signup.html', username=username, email=email,
                               error_password="Passwords do not match")
        elif not tools.valid_email(email):
            return self.render('signup.html', username=username,
                               error_password="eMail address is not valid")
        else:  # valid user data
            # make sure the user doesn't already exist
            u = User.User.by_name(username)
            if u:
                msg = 'That user already exists.'
                return self.render('signup.html', error_username=msg)
            else:
                u = User.User.register(username, password, email)
                u.put()

                self.login(u)
                return self.redirect('/blog/welcome')


class LoginPage(Handler):
    def get(self):
        return self.render("login.html")

    def post(self):
        """
        Post method is called when user tries to login.
        Login credentials are checked in the following way:
            - It is checked if the username exists in the database
            - It is checked if the the hashed password matches the password
              hash as stored in the database
        After successful login the user is redirected to a "welcome" page.
        """
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.User.by_name(username)

        if not user:
            error_username = "This username does not exist"
            return self.render('login.html', error_username=error_username)
        elif not User.valid_pw(username, password, user.pw_hash):
            error_password = "The password is not correct"
            return self.render('login.html',
                               username=username,
                               error_password=error_password)
        else:
            self.login(user)  # Sets the cookie with user id
            return self.redirect('/blog/welcome')


class LogoutPage(Handler):
    def get(self):
        """
        If user navigates to this page, his authentication cookie is deleted.
        The user is then redirected to the signup page.
        """
        self.logout()  # Sets the user id cookie to an empty value
        return self.redirect('/blog/signup')


class WelcomePage(Handler):
    def get(self):
        """
        Render Welcome Page and greet the user.
        The user id is read from the cookie "user_id"
        """
        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:  # user_id either empty or hashed user_id did not match the hash in cookie
            user_id = int(str_user_id)
            user = User.User.by_id(user_id)
            return self.render("welcome.html", username=user.name)

        else:
            return self.redirect('/blog/signup')


class MyBlogPage(Handler):

    def handle_delete_post(self, str_post_id, str_user_id):

        int_post_id = int(str_post_id)
        blog_entry = BlogEntry.by_id(int_post_id)
        blog_entry.delete()

        # delete all comments that are associated with post
        comments = db.GqlQuery("SELECT * "
                               "FROM Comment "
                               "WHERE post_id=" + str_post_id)
        for comment in comments:
            comment.delete()

        # delete all likes that are associated with post
        likes = db.GqlQuery("SELECT * "
                            "FROM Like "
                            "WHERE post_id=" + str_post_id)
        for like in likes:
            like.delete()

        time.sleep(1)  # To prevent "Eventual Inconsistency" in Datastore
        return self.render_my_blog(str_user_id)

    def render_my_blog(self, str_user_id):
        """
        Renders own blog page with only the posts that this user created
        :param str_user_id: User id as string
        """
        query = "SELECT * " \
                "FROM BlogEntry " \
                "WHERE user_id=" + str_user_id + " ORDER BY created DESC"
        blog_entries = db.GqlQuery(query)

        return self.render('front.html',
                           blog_entries=blog_entries,
                           user_id=str_user_id)

    def get(self):
        """
        If user id is valid, render myblog page.
        Otherwise redirect to the signup page.
        """
        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:
            return self.render_my_blog(str_user_id)
        else:
            return self.redirect('/blog/signup')

    def post(self):  # only post method when pushing the "delete" button
        """
        Post Method is called when user deletes a post.
        Not only the blog entry is deleted but also associated
        comments and likes. Eventually, the page is re-rendered.
        """

        # Check first if user has valid cookie. Otherwise redirect...
        str_user_id = self.read_secure_cookie('user_id')
        if not str_user_id:
            return self.redirect('/blog/signup')
        else:
            str_post_id = self.request.get('post_id')
            return self.handle_delete_post(str_post_id, str_user_id)


class MainPage(Handler):
    def render_front(self, str_user_id, err_post_id="", err_msg=""):
        """
        Renders the main blog page

        :param str_user_id: User id as string
        :param err_post_id: post id where user interaction created an error
        :param err_msg: error message
        """

        blog_entries = db.GqlQuery("SELECT * "
                                   "FROM BlogEntry "
                                   "ORDER BY created DESC")
        comments = db.GqlQuery("SELECT * "
                               "FROM Comment "
                               "ORDER BY created DESC")

        return self.render('front.html',
                           blog_entries=blog_entries,
                           user_id=str_user_id,
                           err_post_id=err_post_id,
                           err_msg=err_msg,
                           comments=comments)

    def delayed_render_front(self, str_user_id):
        """
        Calls render_front if user_id is valid after
        waiting one second. A short delay before rendering
        the blog is necessary if the datastore has been
        updated because there is a short inconsistency in
        the tables after they are updated.
        """

        time.sleep(1)  # To prevent "Eventual Inconsistency" in Datastore
        return self.render_front(str_user_id)

    def get(self):
        """
        If user id is valid, render front page.
        Otherwise redirect to the signup page
        """
        str_user_id = self.read_secure_cookie('user_id')
        if str_user_id:
            return self.render_front(str_user_id)
        else:
            return self.redirect('/blog/signup')

    def post(self):  # implementation of delete, like, comment buttons
        """
        Implementation of button interactions of users. The user can
            - like/dislike a post (if user is not creator of post)
            - comment on post (if user is not creator of post)
            - edit a comment (if user created the comment)
            - delete a comment (if user created the comment)
            - delete a post (if user is not creator of post)

        The function notices which type of user interaction was
        triggered by checking the hidden input field "actionType". All
        interactions are implementated in separate class methods.

        Each user interaction modifies the existing database tables
        in an intended way. Subsequently, the blog page is re-rendered.
        """

        # Check first if user has valid cookie. Otherwise redirect...
        str_user_id = self.read_secure_cookie('user_id')
        if not str_user_id:
            return self.redirect('/blog/signup')
        else:
            action_type = self.request.get('actionType')

            if action_type == "like":  # User likes/dislikes post
                str_like_val = self.request.get('like')  # has the format 1|post_id or -1|post_id
                return self.handle_like(str_like_val, str_user_id)

            elif action_type == "create_comment":  # User comments on post
                str_comment = self.request.get('comment')
                str_post_id = self.request.get('post_id')
                return self.handle_comment(str_comment, str_post_id, str_user_id)

            elif action_type == "edit_comment":  # User edits a comment
                str_new_comment = self.request.get('comment-text')
                str_post_id = self.request.get('post_id')
                str_comment_id = self.request.get('comment_id')
                return self.handle_edit_comment(str_new_comment, str_comment_id, str_post_id, str_user_id)

            elif action_type == "delete_comment":  # User edits a comment
                str_comment_id = self.request.get('comment_id')
                return self.handle_delete_comment(str_comment_id, str_user_id)

            elif action_type == "delete":  # User deletes a post
                str_post_id = self.request.get('post_id')
                return self.handle_delete_post(str_post_id, str_user_id)

    def handle_comment(self, str_comment, str_post_id, str_user_id):

        if not str_comment:  # if comment is empty render error message
            return self.render_front(str_user_id,
                                     str_post_id,
                                     "Your Comment may not be empty")
        else:
            int_user_id = int(str_user_id)

            user = User.User.by_id(int_user_id)
            str_username = user.name

            int_post_id = int(str_post_id)

            db_comment = Comment(text=str_comment,
                                 user_id=int_user_id,
                                 post_id=int_post_id,
                                 username=str_username)
            db_comment.put()

            return self.delayed_render_front(str_user_id)

    def handle_edit_comment(self, str_new_comment, str_comment_id, str_post_id, str_user_id):

        if not str_new_comment:
            return self.render_front(str_user_id,
                                     str_post_id,
                                     "Your Comment may not be empty")
        else:
            # get original comment and adjust
            comment = Comment.by_id(int(str_comment_id))
            comment.text = str_new_comment
            comment.put()
            return self.delayed_render_front(str_user_id)

    def handle_delete_comment(self, str_comment_id, str_user_id):
        # get original comment and delete
        comment = Comment.by_id(int(str_comment_id))
        comment.delete()

        return self.delayed_render_front(str_user_id)

    def handle_delete_post(self, str_post_id, str_user_id):

        int_post_id = int(str_post_id)
        blog_entry = BlogEntry.by_id(int_post_id)
        blog_entry.delete()

        # delete all comments that are associated with post
        comments = db.GqlQuery("SELECT * "
                               "FROM Comment "
                               "WHERE post_id=" + str_post_id)
        for comment in comments:
            comment.delete()

        # delete all likes that are associated with post
        likes = db.GqlQuery("SELECT * "
                            "FROM Like "
                            "WHERE post_id=" + str_post_id)
        for like in likes:
            like.delete()

        return self.delayed_render_front(str_user_id)

    def handle_like(self, str_like_val, str_user_id):

        str_like = str_like_val.split('|')[0]  # +1 for like or -1 for dislike
        str_post_id = str_like_val.split('|')[1]
        int_post_id = int(str_post_id)

        # check if user already liked this post
        like_entries = db.GqlQuery("SELECT * "
                                   "FROM Like "
                                   "WHERE user_id=" + str_user_id +
                                   " AND post_id=" + str_post_id)

        if like_entries.get():  # User already liked/disliked
            return self.render_front(str_user_id,
                                     str_post_id,
                                     "You already liked this post")
        else:
            blog_entry = BlogEntry.by_id(int_post_id)
            blog_entry.likes += int(str_like)
            blog_entry.put()

            # Update Like table
            int_user_id = int(str_user_id)
            like = Like(post_id=int_post_id, user_id=int_user_id)
            like.put()

            return self.delayed_render_front(str_user_id)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/', MainPage),
    ('/blog/myblog', MyBlogPage),
    ('/blog/newPost', NewBlogPage),
    ('/blog/editPost', EditBlogPage),
    ('/blog/[0-9]+', BlogArticleHandler),
    ('/blog/signup', SignUpPage),
    ('/blog/welcome', WelcomePage),
    ('/blog/login', LoginPage),
    ('/blog/logout', LogoutPage)
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()
