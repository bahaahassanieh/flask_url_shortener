from flask import Flask, request, jsonify, redirect, abort, render_template
import sqlite3
import string
import random
from urllib.parse import urlparse
from datetime import datetime


app = Flask(__name__)


DATABASE_NAME = "shortener.sqlite"


def get_db_connection():
    """
    Get a connection to the SQLite database.
    This will create the .db file if it doesn't exist.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    return conn
    shortner


def init_db():
    """
    Initialize the database with required tables.
    """
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()

            # Create the url_mapping table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS url_mapping (
                    short_code TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL
                )
            ''')

            # Create the updated url_analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS url_analytics (
                    short_code TEXT,
                    original_url TEXT,
                    click_date DATE,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT
                )
            ''')

    except sqlite3.Error as e:
        print("Error initializing database:", e)
        return False
    finally:
        conn.close()
    return True



def generate_shortcode(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('url')

    if not original_url or not urlparse(original_url).scheme:
        return jsonify(error="Invalid URL provided"), 400

    short_code = generate_shortcode()

    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO url_mapping (short_code, original_url) VALUES (?, ?)", (short_code, original_url))
    except sqlite3.Error as e:
        print("Database error:", e)
        return jsonify(error="Database error"), 500


    return jsonify({
        "shortened_url": f"{request.host_url}{short_code}"
    })


@app.route('/<short_code>', methods=['GET'])
def redirect_to_original(short_code):
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            # Fetch the original URL for the given short code
            cursor.execute("SELECT original_url FROM url_mapping WHERE short_code = ?", (short_code,))
            result = cursor.fetchone()

            if result:
                original_url = result[0]

                # Log the access to the analytics table
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent')
                referrer = request.referrer
                today_date = datetime.today().date()  # get the current date without the time component

                cursor.execute(
                    """
                    INSERT INTO url_analytics 
                    (short_code, original_url, click_date, ip_address, user_agent, referrer) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (short_code, original_url, today_date, ip_address, user_agent, referrer)
                )

                return redirect(original_url)
            else:
                abort(404)

    except sqlite3.Error as e:
        print("Database error:", e)
        return jsonify(error="Database error"), 500


@app.route('/analytics/<short_code>', methods=['GET'])
def get_analytics(short_code):
    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            cursor = conn.cursor()

            # Query to fetch all entries for the given short code
            cursor.execute('''
                SELECT click_date, accessed_at, ip_address, user_agent, referrer, original_url
                FROM url_analytics
                WHERE short_code = ?
                ORDER BY accessed_at DESC
            ''', (short_code,))

            result = cursor.fetchall()

            if result:
                # Convert the result into a list of dictionaries for JSON response
                data = [{"click_date": row[0], "accessed_at": row[1], "ip_address": row[2], "user_agent": row[3],
                         "referrer": row[4], "original_url": row[5]} for row in result]
                return jsonify(data)
            else:
                return jsonify(error="No analytics data found for this short code"), 404

    except sqlite3.Error as e:
        print("Database error:", e)
        return jsonify(error="Database error"), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify(error="URL not found"), 404


if __name__ == '__main__':
    if not init_db():
        print("Failed to initialize database.")
        exit(1)
    app.run(host="0.0.0.0", debug=True)
