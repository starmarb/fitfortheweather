from flask import Flask, request, render_template, session, redirect, url_for, jsonify, send_file
import sqlite3
from temperature import getseason, season_query
import json
from werkzeug.utils import secure_filename
import base64
import io

app = Flask(__name__, template_folder='templates')
app.secret_key = '419project'

#--------------------------------------------------------------------------------------
#get user from database that matches account info
def authenticate_user(username, password):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user_id = cursor.fetchone()
    connection.close()
    return user_id

#use flask's session to get user_id
def get_user_id():
    return session.get('user_id')
#--------------------------------------------------------------------------------------
#Display login page if not logged in (else render user's homepage)
@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET'])
def login():
    user_id = get_user_id()
    # if user_id is not None: 
    #     return render_template('index.html')
    return render_template('login.html')

#--------------------------------------------------------------------------------------

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    user_id = authenticate_user(username, password)
    if user_id is not None:
        # User is authenticated, store user_id in the session
        session['user_id'] = user_id[0]
        return redirect(url_for('index'))
    else:
         error_message = "Login failed. Please try again."
         return render_template('login.html', error_message=error_message)

#--------------------------------------------------------------------------------------

@app.route('/signup', methods=['GET'])
def signup():
     return render_template('signup.html')

#--------------------------------------------------------------------------------------

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    password = request.form['password']
    if not (username and password):
        error_message = "Please fill out all fields."
        return render_template('signup.html', error_message=error_message)
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user is None:
            # Insert user input into the database
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                            (username, password))
            conn.commit()
            success_message = "Account successfully created."
            return render_template('signup.html', success_message=success_message)
        else:
             error_message = "Username already taken"
             return render_template('signup.html', error_message=error_message)

#--------------------------------------------------------------------------------------
#pop out of session to logout
@app.route('/logout')
def logout():
    session.pop('user_id', default=None)
    return render_template('login.html')

#--------------------------------------------------------------------------------------

@app.route('/home', methods=['GET'])
def index():
    user_id = get_user_id()
    if user_id is None: 
        error_message = "You must be signed in to view the home webpage."
        return render_template('login.html', error_message=error_message)
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
    conn.commit()
    # Retrieve data from the database to display
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()
    return render_template('index.html', username=username[0])

#--------------------------------------------------------------------------------------

@app.route('/getseason',methods=['POST'])
def get_season_api():
    temperature = float(request.form['temperature'])  # Retrieve temperature from form data
    season = getseason(temperature)
    return season 
    
#--------------------------------------------------------------------------------------

@app.route('/getclothes',methods=['POST'])
def get_clothing_recommendations():
    temperature = float(request.form['temperature'])  # Retrieve temperature from form data
    season = getseason(temperature)
    user_id = get_user_id()
    clothing_recs = season_query(season, user_id)  #Retrive clothing items based on season (i.e. temperature)
    encoded_clothing_recs = {}
    for blob, clothing_type in clothing_recs.items():
        # Assuming blob is a byte-like object
        encoded_blob = base64.b64encode(blob).decode('utf-8')
        encoded_clothing_recs[encoded_blob] = clothing_type
    # print(type(clothing_recs.keys()))
    # image_base64 = base64.b64encode(clothing_recs.keys()).decode('utf-8')
    # return jsonify({image_base64: clothing_recs.values()[0]}), 200
    return jsonify(encoded_clothing_recs)

#--------------------------------------------------------------------------------------

@app.route('/closet', methods=['GET'])
def closet():
    user_id = get_user_id()
    if user_id is None: 
        error_message = "You must be signed in to view the closet webpage."
        return render_template('login.html', error_message=error_message)
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
    conn.commit()
    # Retrieve data from the database to display
    cursor.execute("SELECT * FROM clothes WHERE user_id = ?", (user_id,))
    all_items = cursor.fetchall()
    processed_items = []
    for item in all_items:
        # If item has an image, encode it; otherwise, use default image
        if item[3]:  # assuming item[3] is the image blob
            img_data = base64.b64encode(item[3]).decode('utf-8')
        else:
            with open('/Users/agapeseed/Documents/GitHub/project-project-group-9/Unknown.png', 'rb') as dummy_img:
                img_data = base64.b64encode(dummy_img.read()).decode('utf-8')
        processed_item = item[:3] + (img_data,) + item[4:]
        # print(processed_item)
        processed_items.append(processed_item)
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()
    # Redirect to a confirmation page
    item_removed = request.args.get('item_removed', False)
    return render_template('closet.html', all_items=processed_items, item_removed=item_removed, username=username[0] if username else 'User')

#--------------------------------------------------------------------------------------
#allowed image files
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#get user input, store in database, and display on webpage
@app.route('/add_item', methods=['POST'])
def add_item():
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    if request.method == 'POST':
        user_id = get_user_id()

        img = request.files['img']
        description = request.form.get('description')
        item_type = request.form.get('type')
        seasons = request.form.getlist('season')
        colors = request.form.getlist('colors')

        if not img:
            error_message = "Please select an image file."
        elif not allowed_file(img.filename):
            error_message = "Invalid image file type. Allowed types are: {}".format(', '.join(ALLOWED_EXTENSIONS))
        elif not description or not item_type or not seasons:
            error_message = "Please fill out all fields."
        else:
            filename = secure_filename(img.filename)
            file_stream = img.read()

            color_str = ', '.join(colors)        
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                # Insert user input into the database
                cursor.execute("""
                    INSERT INTO clothes (user_id, img, description, type, summer, fall, winter, spring, color)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, file_stream, description, item_type, 'Summer' in seasons, 'Fall' in seasons, 'Winter' in seasons, 'Spring' in seasons, color_str))
                conn.commit()
            return redirect(url_for('closet'))

        # Render the closet page with an error message
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            # Retrieve data from the database to display
            cursor.execute("SELECT * FROM clothes WHERE user_id = ?", (user_id,))
            all_items = cursor.fetchall()
            processed_items = []
            for item in all_items:
                # If item has an image, encode it; otherwise, use default image
                if item[3]:  # assuming item[3] is the image blob
                    img_data = base64.b64encode(item[3]).decode('utf-8')
                else:
                    with open('/Users/agapeseed/Documents/GitHub/project-project-group-9/Unknown.png', 'rb') as dummy_img:
                        img_data = base64.b64encode(dummy_img.read()).decode('utf-8')
                processed_item = item[:3] + (img_data,) + item[4:]
                processed_items.append(processed_item)
           
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            username = cursor.fetchone()
           
            return render_template('closet.html', all_items=processed_items, error_message=error_message, username=username[0] if username else 'User')
    
#--------------------------------------------------------------------------------------
# Remove an item by its specified name and user
@app.route('/remove_item/<int:item_id>')
def remove_item(item_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Execute SQL query to remove the item by ID
    cursor.execute("DELETE FROM clothes WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('closet', item_removed=True))

#--------------------------------------------------------------------------------------
# Remove outfit by its specified name and user
@app.route('/remove_outfit', methods=['POST'])
def remove_outfit():
    user_id = get_user_id()
    outfit_name_to_remove = request.form['outfit_name']

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM outfit
            WHERE user_id = ? AND outfitname = ?
        """, (user_id, outfit_name_to_remove))

        conn.commit()

    return redirect(url_for('favorites'))

#--------------------------------------------------------------------------------------
#insert each item in an outfit as an entry in database (with the same name)
@app.route('/saveoutfit', methods=['POST'])
def saveoutfit():
    if request.method == 'POST':
        # print('Request received')
        # print('Form data:', request.form)
        user_id = get_user_id()
        outfitname = request.form['outfitname']
        saveitems = request.form.getlist('senditems[]')
        # print('User ID:', user_id)
        # print('Outfit Name:', outfitname)
        # print('Save Items:', saveitems)
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            for item in saveitems:
                cursor.execute("INSERT INTO outfit (user_id, outfitname, outfitvalue) VALUES (?, ?, ?)",
                                (user_id, outfitname, item))
                conn.commit()
        return redirect(url_for('index'))
    
#display outfit by getting items that have the same outfitname
@app.route('/favorites', methods=['GET'])
def favorites():
    user_id = get_user_id()
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
    cursor.execute("""
        SELECT outfitname, GROUP_CONCAT(outfitvalue) as outfit_values
        FROM outfit
        WHERE user_id = ?
        GROUP BY outfitname
        ORDER BY outfitname
    """, (user_id,))
    outfits_data = cursor.fetchall()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    username = cursor.fetchone()
    return render_template('favorites.html', outfits_data=outfits_data, username=username[0])

#--------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run()
