import sqlite3
import sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'root': {
        'level': 'INFO'
    }
})

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    app.db_connection_count+=1
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    app.logger.info('"%s" article retrieved', post['title'])
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
app.db_connection_count = 1

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.info('Article does not exist')
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('"About" Us page retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('"%s" article created', title)
            return redirect(url_for('index'))

    return render_template('create.html')

#Healthcheck endpoint
@app.route('/healthz')
def healthz():
    error = 0
    try:
        connection = get_db_connection()
        post = connection.execute('SELECT * FROM posts').fetchone()
    except:
        e = sys.exc_info()[1]
        app.logger.error('Unexpected error: "%s"', e)
        error = 1
    finally:
        try:
            connection.close()
        except:
            app.logger.info('Error al cerrar la conexion')
    
    if error == 1:
        response = app.response_class(
            response=json.dumps({"result":"ERROR - unhealthy"}),
            status=500,
            mimetype='application/json')
    else:
        response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json')

    return response

#Metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    response = app.response_class(
            response=json.dumps({'db_connection_count':'{}'.format(app.db_connection_count),'post_count':'{}'.format(len(posts))}),
            status=200,
            mimetype='application/json'
    )

    return response

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
