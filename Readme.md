<h1>Multi-User Blog</h1>

Version 1.0

URL: https://blogks1.appspot.com/blog/

Multi-User Blog is an online-platform where users can create their own blog 
as well as view, like and comment on blog posts of other users.

The back-end of Multi-User Blog has been implemented in Python employing
Google App Engine to deploy the files as a web server in the cloud.

<h2>1. Content</h2>
    - Blog
    |-- app.yaml
    |-- db_model.py
    |-- index.py
    |-- index.yaml
    |-- Readme.md
    |-- tools.py
    |-- User.py
    |-- css/
        |-- bootstrap.css
        |-- bootstrap.min.css
        |-- bootstrap-theme.css
        |-- bootstrap-theme.min.css
        |-- main.css
    |-- templates/
        |-- base.html
        |-- front.html
        |-- login.html
        |-- new_post.html
        |-- permalink.html
        |-- signup.html
        |-- welcome.html

<h2>2. Prerequisites</h2>
Google App Server needs to be installed on the machine. 
More information about how to download and set up Google App Engine can be found <a href="https://cloud.google.com/appengine/downloads">here</a>.

Movie_Gallery uses Jinja2 to render dynamic HTML content. To install Jinja2 and make it available to Python
open a terminal and type

    > pip install Jinja2
    
<h2>3. Locally deploy the server</h2>
To create the http listeners and deploy the content on the local machine, open a terminal, navigate to the folder <i>Blog</i> and run

    > python <path/to/google_app_engine>/dev_appserver.py .

<h2>4. Blog Features</h2>

<b>4.1. Signup as a new user:</b>
    New users have to signup on https://blogks1.appspot.com/blog/signup. Users who are currently not logged in and try to access the blog 
    are automatically redirected to the signup page.
    Valid usernames are between 3 and 20 characters and may only contain alphabetical characters as well as a dash (-) and underscore (_).
    Valid passwords may contain all characters and are between 3 and 20 characters long.
    Note, that the email address is an optional input on the signup page.
    
<b>4.2. Login:</b>
    Users log in at the URL https://blogks1.appspot.com/blog/login. After successful login, a secure authentication cookie is created.
    
<b>4.3. Logout:</b>
    Users log out at the URL https://blogks1.appspot.com/blog/logout. After logging out, the authentication cookie is cleared.
    
<b>4.4. Blog Page:</b>
    Blog posts can be seen at https://blogks1.appspot.com/blog/ . Posts that the current user created can be edited or deleted with the buttons 
    below the post. However, only other users can user the buttons to like/dislike the post. A post can only liked or disliked once. If the user
    disobeys this rule, an error message occurs.
    Users can comment on posts that a other users created but they cannot comment on their own posts. Comments can be edited or deleted.
    
<b>4.5. Create New Posts:</b>
    Blog posts can be created at https://blogks1.appspot.com/blog/newPost. Every post needs a subject and a blog text. After creation of a new post, 
    the user is redirected to a permalink, showing the new post.
    





        
    
    
    

    

