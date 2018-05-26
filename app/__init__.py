from flask import Flask, url_for

app = Flask(__name__)


from app import views           # set the url map module ---- views.py  (visual function)
# @app.route('/')
# def index():
#     return 'Index Page'

# @app.route('/hello')
# def hello():
#     return 'Hello, World'

# @app.route('/user/<username>')
# def show_user_profile(username):
#     return 'User %s' % username

# @app.route('/post/<int:post_id>')
# def show_post(post_id):
#     return 'Post %d' % post_id

# @app.route('/path/<path:subpath>')
# def show_subpath(subpath):
#     return 'Subpath %s' % subpath

# @app.route('/projects/')
# def projects():
#     return 'The project is similar to the folder in a file system'

# @app.route('/about')
# def about():
#     return 'The about is similar to the pathname of a file'

# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('hello', next = '/'))
#     print(url_for('show_user_profile', username='John Doe'))

# if __name__ == '__main__':
# 	app.run(debug=True)