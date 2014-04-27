import cgi
import os
import re
import datetime
import logging
import random
import string
import hashlib
import urllib 
import wsgiref.handlers

from google.appengine.ext import db 
from google.appengine.api import users
from google.appengine.api import memcache 
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.util import run_wsgi_app

from datetime import datetime, timedelta

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_username(username):
    return USER_RE.match(username)

def valid_password(password):
    return PASSWORD_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)

form = """ 
          <html><body><form method="post"> 
            <div><input type="text" name="subject" value="%(subject)s"></div> 
            <div><textarea name="content" value="%(content)s" rows="3" cols="60"></textarea></div> 
            <div><input type="submit" value="Submit"></div> 
          </form> 
          <hr> 
        </body></html>"""

forma = """ 
  <html> 
  <body> 
  <form method="post">

  <br><b>Sign up</b><br>

  <table>
      <tr>
      <td class='label'>User Name</td>
      <td><input type='text' name='username' value='%(username)s'></td>
      </tr>
      <tr>
      <td class='label'>Password</td>
      <td><input type='password' name='password' value=''></td>
      </tr>
      <tr>
      <td class='label'>Verify Password</td>
      <td><input type='password' name='verify' value=''></td>
      </tr>
      <tr>
      <td class='label'>e-mail</td>
      <td><input type='text' name='email' value='%(email)s'></td>
      </tr>
      </table>

      <div><input type="submit" value="Sign up"></div> 
  </form> 
  </body> 
  </html>"""

formn = """ 
  <html> 
  <body> 
  <form method="post">

  <br><b>Log in</b><br>

  <table>
      <tr>
      <td class='label'>User Name</td>
      <td><input type='text' name='username' value='%(username)s'></td>
      </tr>
      <tr>
      <td class='label'>Password</td>
      <td><input type='password' name='password' value=''></td>
      </tr>
      </table>

      <div><input type="submit" value="Submit login data"></div> 
  </form> 
  </body> 
  </html>"""

formb = """ 
  <html>
  <head><title>Rot 13</title></head>
  <body>
  <h2>Enter some text:</h2>
  <form method="post">
      <input type='text' name='text' value='%(text)s'><br>
      <input type="submit" value="Rot 13"> 
  </form> 
  </body> 
  </html>"""

############## BLOG

class Post(db.Model): 
  subject = db.StringProperty() 
  content = db.TextProperty() 
  date = db.DateTimeProperty(auto_now_add=True) 

class MainPage(webapp.RequestHandler):
  def get(self): 
    self.response.out.write('<b>Hello!</b><br>')
    self.response.out.write(""" 
          <html><form action="/blog/signup"> 
            <div><input type="submit" value="Sign up"></div> 
          </form></html>""")
    self.response.out.write(""" 
          <html><form action="/blog/login"> 
            <div><input type="submit" value="Log in"></div> 
          </form></html>""")
    self.response.out.write(""" 
          <html><form action="/users"> 
            <div><input type="submit" value="List of Users"></div> 
          </form></html>""")
    self.response.out.write(""" 
          <html><form action="/blog"> 
            <div><input type="submit" value="Go to Blog"></div> 
          </form></html>""")
    self.response.out.write(""" 
          <html><form action="/blog/delete"> 
            <div><input type="submit" value="Delete a post"></div> 
          </form></html>""")
    self.response.out.write(""" 
          <html><form action="/rot13"> 
            <div><input type="submit" value="Go to Rot13"></div> 
          </form></html>""")

class BlogHandler(webapp.RequestHandler): 

    def get(self): 
        self.response.out.write('<b>Welcome to my blog!</b><br>')
        self.response.out.write(""" 
            <html><form action="/blog/newpost"> 
              <div><input type="submit" value="New Post"></div> 
            </form></html>""")

        self.response.out.write('<html><body>') 
 
        posts = db.GqlQuery("SELECT * " 
                            "FROM Post " 
                            "ORDER BY date DESC LIMIT 10") 

        #posts = self.get_posts()
 
        for post in posts: 
            self.response.out.write('<hr>%s<br>' % str(post.date.strftime('%a %b %d %H:%M:%S %Y')))
            self.response.out.write('<hr><b>%s</b>' % cgi.escape(post.subject)) 
            self.response.out.write('<blockquote>%s</blockquote>' % cgi.escape(post.content)) 

        #global save_time
        #now_time = datetime.utcnow()
        #age = (now_time - save_time).total_seconds()
        #self.response.out.write('<hr>Saved time %s<br>' % save_time)
        #self.response.out.write('UTC %s<br>' % now_time)
        #self.response.out.write('Age %s<br>' % age)
        self.response.out.write('</body></html>') 

#    def get_posts(self):
#        posts = memcache.get("posts")
#        if posts is not None:
#            return posts
#        else:
#            posts = self.render_posts()
#            global save_time
#            save_time = datetime.utcnow()
#            if not memcache.add("posts", posts, 10):
#                logging.error("Memcache set failed")
#            return posts    

#    def render_posts(self):

#        results = db.GqlQuery("SELECT * " 
#                            "FROM Post " 
#                            "ORDER BY date DESC").fetch(10)
#        return results 
 
class PostPage(webapp.RequestHandler):
      def get(self, post_id):
          key = db.Key.from_path('Post', int(post_id))
          postxx = db.get(key)
          if not postxx:
              self.error(404)
              return
          self.response.out.write('<blockquote>%s</blockquote>' % (postxx.subject)) 
          self.response.out.write('<blockquote>%s</blockquote>' % (postxx.content)) 
          self.response.out.write('<blockquote>%s</blockquote>' % (postxx.date))
          self.response.out.write('<blockquote>%s</blockquote>' % (post_id))
          self.response.out.write('<blockquote>%s</blockquote>' % (key))
          return postxx

class FormHandler(webapp.RequestHandler): 

  def write_form(self, subject='', content=''):
    self.response.out.write(form % {'subject': cgi.escape(subject), 'content': cgi.escape(content)}) 

  def get(self): 
    self.response.out.write('<b>New Post:</b><br>')
    self.write_form() 
 
  def post(self): 
    subject = self.request.get('subject')
    content = self.request.get('content') 

    if subject and content:
        
        post = Post(key_name = subject) 
        post.subject = subject
        post.content = content 
        post.put() 
        #self.redirect('/blog/%s' % str(post.key().id()))
        self.redirect('/blog')

    else:
        self.response.out.write('<b>New Post:</b><br>')
        self.write_form(subject, content)
        self.response.out.write('<br><div style="color: red">Please, enter both, subject and some content</div>')

class DeleteHandler(webapp.RequestHandler): 

  def write_form(self, subject='', content=''):
    self.response.out.write(form % {'subject': cgi.escape(subject), 'content': cgi.escape(content)}) 

  def get(self): 
    self.response.out.write('<b>Delete Post:</b><br>')
    self.write_form() 
 
  def post(self): 
    subject = self.request.get('subject')

    if subject:
        
        post = Post(key_name = subject) 
        post.delete() 
        self.redirect('/blog')

    else:
        self.response.out.write('<b>Delete Post:</b><br>')
        self.write_form(subject, content)
        self.response.out.write('<br><div style="color: red">Please, enter a subject of the post to be deleted</div>')


########## SIGN UP

class Register(db.Model): 
  regid = db.StringProperty() 
  regpw = db.StringProperty() 
  regml = db.StringProperty() 

class SignupPage(webapp.RequestHandler):
 
    def write_forma(self, username='', email=''): 
        self.response.out.write(forma % {'username': cgi.escape(username),
                                        'email': cgi.escape(email)}) 

    def make_name_hash(self, name1, name2):
        h = hashlib.sha256(name1 + name2).hexdigest()
        return '%s|%s' % (name1, h)

    def get(self): 
        self.write_forma()

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')
        have_error = False

        q = db.GqlQuery("SELECT * " 
                        "FROM Register "
                        "WHERE regid = :1", user_username) 
        qq = q.get()
        
        if not valid_username(user_username):
           have_error = True
           self.response.out.write('<div style="color: red">The username <b>%s</b> is not valid</div>' % user_username)

        if qq:
           have_error = True
           self.response.out.write('<br>')
           self.response.out.write('<div style="color: red">The user <b>%s</b> already signed up</div>' % user_username)

        if not valid_email(user_email):
           have_error = True
           self.response.out.write('<div style="color: red">The email <b>%s</b> is not valid</div>' % user_email)

        if not valid_password(user_password):
           have_error = True
           self.response.out.write('<div style="color: red">The password <b>%s</b> is not valid</div>' % user_password)

        if (user_password != user_verify):
           have_error = True
           self.response.out.write('<div style="color: red"><b>%s</b>, your passwords differ</div>' % user_username)

        if have_error:
           self.write_forma(user_username, user_email)
           self.response.out.write('<br>')
           self.response.out.write('<div style="color: red"><b>%s</b>, please resubmit your login details</div>' % user_username)
        else:
            h_username = str(self.make_name_hash(user_username, user_password))

            register = Register() 
            register.regid = user_username
            register.regpw = h_username
            register.regml = user_email
            register.put()
            
            self.redirect('/blog/welcome')
            self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % h_username)
                    
class WelcomePage(webapp.RequestHandler): 
    def get(self): 
        h_username = self.request.cookies.get('user_id')
        if h_username:
            username = h_username.split('|')[0]
            self.response.out.write('Welcome, <b>%s</b>!' % username)
            self.response.out.write("""
                   <html><form action="/blog">
                   <br><div><input type="submit" value="Go to Blog"></div>
                   </form></html>""")
        else:    
            self.redirect('/blog/login')

########## LOG IN

class LoginPage(webapp.RequestHandler):

    def write_formn(self, username=''): 
        self.response.out.write(formn % {'username': cgi.escape(username)}) 

    def make_name_hash(self, name1, name2):
        h = hashlib.sha256(name1 + name2).hexdigest()
        return '%s|%s' % (name1, h)

    def get(self): 
        self.write_formn()

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')

        q = db.GqlQuery("SELECT * " 
                        "FROM Register "
                        "WHERE regid = :1", user_username) 
        qq = q.get()
        
        if qq:
           self.response.out.write('<br>')
           r_username = qq.regpw
           h_username = str(self.make_name_hash(user_username, user_password))
           if (r_username == h_username):
               self.redirect('/blog/welcome')
               self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % h_username)
           else:
               self.write_formn()
               self.response.out.write('<div style="color: red">Incorrect password for the user <b>%s</b></div>' % user_username)

        else:
           self.write_formn()
           self.response.out.write('<div style="color: red">The user <b>%s</b> not found</div>' % user_username)


class LogoutPage(webapp.RequestHandler):

    def get(self): 
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect('/blog/signup')


class UserList(webapp.RequestHandler):
 
    def get(self): 
        registers = db.GqlQuery("SELECT * " 
                            "FROM Register ") 

        for register in registers: 
          self.response.out.write('<b>%s - </b>' % cgi.escape(register.regid)) 
          self.response.out.write('<b>%s - </b>' % cgi.escape(register.regpw)) 
          self.response.out.write('<b>%s</b><br>' % cgi.escape(register.regml)) 



########## ROT 13

class Rot13(webapp.RequestHandler):
 
    def write_formb(self, text=''): 
        self.response.out.write(formb % {'text': text}) 

    def get(self): 
        self.write_formb()

    def post(self):
        rot13=''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')
            
        self.write_formb(rot13)
                    

application = webapp.WSGIApplication( 
                                     [('/', MainPage),
                                      ('/blog', BlogHandler),
                                      ('/blog/newpost', FormHandler),
                                      ('/blog/delete', DeleteHandler),
                                      ('/blog/([0-9]+)', PostPage),
                                      ('/blog/signup', SignupPage),
                                      ('/blog/login', LoginPage),
                                      ('/blog/logout', LogoutPage),
                                      ('/blog/welcome', WelcomePage),
                                      ('/users', UserList),
                                      ('/rot13', Rot13)], 
                                     debug=True) 
 
def main(): 
    run_wsgi_app(application) 
 
if __name__ == "__main__": 
    main()
