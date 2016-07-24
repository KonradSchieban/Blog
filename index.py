import os

import jinja2
import webapp2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, kw))


class BlogEntry(db.Model):

    subject = db.StringProperty(required=True)
    text = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


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

        if subject and text:
            a = BlogEntry(subject=subject, text=text)
            a.put()

            # Creation of a Permalink
            link_id = a.key().id()
            self.redirect('/blog/' + str(link_id))
        else:
            error = "We need both a subject and content"
            self.render_new_post_page(subject, text, error)


class MainPage(Handler):

    def render_front(self):

        blog_entries = db.GqlQuery("SELECT * FROM BlogEntry ORDER BY created DESC")

        self.render('front.html', blog_entries=blog_entries)

    def get(self):
        self.render_front()


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/NewPost', NewBlogPage),
    ('/blog/[0-9]+', BlogArticleHandler)
], debug=True)


def main():
    app.run()


if __name__ == '__main__':
    main()
