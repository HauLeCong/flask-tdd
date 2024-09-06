import sqlite3
from functools import wraps
from flask import (
        Flask, 
        g, 
        render_template, 
        request, 
        session, 
        flash, 
        redirect, 
        url_for, 
        abort, 
        jsonify
    )

DATABASE = "flaskr.db" 
USERNAME = "admin"
PASSWORD = "admin"
SECRET_KEY = "change_me"

app = Flask(__name__)

app.config.from_object(__name__)

@app.route('/')
def index():
    """Searches the database for entries, then displays them."""
    db = get_db()
    cur = db.execute('select * from entries order by id desc')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_entry():
    
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute(
        'insert into entries (title, text) values (?,?)',
        [request.form['title'], request.form['text']]
    )
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('index'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in.')
            return jsonify({'status': 0, 'message': 'Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/delete/<post_id>', methods=['GET'])
def delete_entry(post_id):
    """Delete post from database"""
    result = {'status': 0, 'message': 'Error'}
    try:
        db = get_db()
        db.execute('delete from entries where id=' + post_id)
        db.commit()
        result = {'status': 1, 'message': "Post Deleted"}
    except Exception as e:
        result = {'status': 0, 'message': repr(e)}
    return jsonify(result)

def connect_db():
    """Connects to the database."""
    rv = sqlite3.connect(app.config["DATABASE"])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()
        

if __name__ == "__main__":
    app.run()
    

    
