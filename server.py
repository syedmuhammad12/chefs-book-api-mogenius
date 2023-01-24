# from flask import Flask
# server = Flask(__name__)

# @server.route("/")
# def hello():
#     return "Hello World!"

# if __name__ == "__main__":
#    server.run(host='0.0.0.0', port=1337)



import psycopg
from flask import Flask, flash, request, redirect, url_for, jsonify, send_file, make_response
from flask_cors import CORS, cross_origin
import cloudinary
from cloudinary.uploader import upload, destroy
from cloudinary.utils import cloudinary_url

cloud = cloudinary.config(cloud_name = "dsx7e9ziz",
  api_key = "248644393929331",
  api_secret = "C2Dj4VA7fXzHhhj53FTvfN1yClo",
  secure = True)
# import urrlib
conn = psycopg.connect("postgres://flzvmlew:NJsYT-XPes7M6H_LIVItrChXN2hwongl@surus.db.elephantsql.com/flzvmlew")
cur = conn.cursor()
conn.autocommit = True

app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
def hello():
    return "Hello World!"

@app.route('/user_signup', methods=['POST'])
@cross_origin(supports_credentials=True)
def signup_user():
    email = request.get_json()["email"]
    password = request.get_json()["password"]
    name = request.get_json()["name"]
    try:
        with conn.cursor() as cur: 
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS Users (
                        id serial PRIMARY KEY,
                        name text,
                        email text,
                        password text)
                    """)
            a = cur.execute(f"SELECT * FROM Users WHERE email='{email}'")
            if len(a.fetchall())>0:
                return jsonify("Account already present")
            else:
                cur.execute(f"""
                            INSERT INTO Users (name, email, password) VALUES ('{name}', '{email}', '{password}')

                            """)
        return jsonify("Account Added Successfully")
    except Exception as e:
        print(e)
        return jsonify("Server Down!!!!!!!")
    
    
@app.route('/user_signin', methods=['POST'])
@cross_origin(supports_credentials=True)
def signin_user():
    email = request.get_json()["email"]
    password = request.get_json()["password"]
    print(email)
    try:
        with conn.cursor() as cur: 
            dat = cur.execute(f"""
                    SELECT * FROM Users WHERE email='{email}' AND password='{password}'
                    """)
            data = dat.fetchall()
            if len(data)>0:
                data = data[0][1:]
                return jsonify({"name":data[0], "email":data[1], "password":data[2]})
            else:
                return jsonify("Account not found")

                            
    except:
        return jsonify("Account not found")
    

    
@app.route('/chef_signup', methods=['POST'])
@cross_origin(supports_credentials=True)
def signup_chef():
    email = request.get_json()["email"]
    password = request.get_json()["password"]
    name = request.get_json()["name"]
    username = request.get_json()["username"]
    try:
        with conn.cursor() as cur: 
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS Chefs (
                        username text PRIMARY KEY,
                        name text,
                        email text,
                        password text)
                    """)
            a = cur.execute(f"SELECT * FROM Chefs WHERE email='{email}'")
            b = cur.execute(f"SELECT * FROM Chefs WHERE username='{username}'")
            if len(a.fetchall())>0:
                return jsonify("Email already present")
            elif len(b.fetchall())>0:
                return jsonify("Username already present")
            else:
                cur.execute(f"""
                INSERT INTO Chefs (username, name, email, password) VALUES ('{username}', '{name}', '{email}', '{password}')
                            """)
        return jsonify("Account Added Successfully")
    
    except:
        
        return jsonify("Server Down!!!!!!!")
    
    
    
@app.route('/chef_signin', methods=['POST'])
@cross_origin(supports_credentials=True)
def signin_chef():
    
    email = request.get_json()["email"]
    password = request.get_json()["password"]
    
    try:
        with conn.cursor() as cur:
            dat = cur.execute(f"""
                    SELECT * FROM Chefs WHERE email='{email}' AND password='{password}'
                    """)
            data = dat.fetchall()
            if len(data)>0:
                data = data[0]
                return jsonify({"username":data[0], "name":data[1], "email":data[2], "password":data[3] })
            else:
                return jsonify("Account not found")

                            
    except:
        return jsonify("Account not found")

@app.route('/addrecipe', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_recipe():
    
    image_file = request.get_json()["file"]
    rec_name = request.get_json()["recname"]
    rec_ing = request.get_json()["recing"]
    rec_method = request.get_json()["recmethod"]
    user = request.get_json()["username"]
    
    try:
        with conn.cursor() as cur:
            dat = cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS Recipes (
                        id serial PRIMARY KEY,
                        username text REFERENCES Chefs (username),
                        recipe_name text,
                        recipe_ingredients text,
                        recipe_methods text,
                        img_name text)
                    """)
            
            a = cur.execute(f"SELECT * FROM Recipes")
            data = len(a.fetchall())
            image_name = f"{user}_{data+1}"
            cur.execute(f"""
                INSERT INTO Recipes (username, recipe_name, recipe_ingredients, recipe_methods, img_name) VALUES ('{user}', '{rec_name}', '{rec_ing}', '{rec_method}', '{image_name}')
                            """)
            
            upload(image_file, public_id=image_name)
        return jsonify("done sending file :)")
                            
    except:
        return jsonify("Server Down!!!!")
    

@app.route('/chefrecipe', methods=['POST'])
@cross_origin(supports_credentials=True)
def get_rec_chef():
    user = request.get_json()["username"]
    
    try:
        with conn.cursor() as cur:

            dat = cur.execute(f"""
                    SELECT * FROM Recipes WHERE username='{user}'
                    """)
            data = dat.fetchall()
            if len(data)==0:
                return jsonify({"data": []})
            else:
                all_data = []
                for i in data:
                    url, options = cloudinary_url(i[-1], width=800, height=500, crop="fill")
                    dic = {"recid": i[0], "username": i[1], "recname": i[2], "recing": i[3], "recmethod": i[4], "recimg": url}
                    all_data.append(dic)
                return jsonify({"data": all_data})
                            
    except:
        return jsonify({"data": []})

@app.route('/getrecipe', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_rec():
    
    try:
        with conn.cursor() as cur:

            dat = cur.execute(f"""
                    SELECT * FROM Recipes,Chefs WHERE Recipes.username=Chefs.username
                    """)
            data = dat.fetchall()
            if len(data)==0:
                return jsonify({"data": []})
            else:
                all_data = []
                for i in data:
                    url, options = cloudinary_url(i[5], width=800, height=500, crop="fill")
                    dic = {"username": i[1], "recname": i[2], "recing": i[3], "recmethod": i[4], "recimg": url, "chef_name": i[7]}
                    all_data.append(dic)
                return jsonify({"data": all_data})
                            
    except:
        return jsonify("No Recipes Available :(")
    
    
@app.route('/viewrecipe', methods=['POST'])
@cross_origin(supports_credentials=True)
def view_rec():
    rec_id = request.get_json()["id"]
    
    try:
        with conn.cursor() as cur:

            dat = cur.execute(f"""
                    SELECT * FROM Recipes WHERE id='{rec_id}'
                    """)
            data = dat.fetchone()
#             all_data = []
            url, options = cloudinary_url(data[-1], width=800, height=500, crop="fill")
            dic = {"recid": data[0], "username": data[1], "recname": data[2], "recing": data[3], "recmethod": data[4], "recimg": url}
#             all_data.append(dic)
            return jsonify(dic)
                            
    except:
        return jsonify("Server Down!!!!")
    
    
@app.route('/updaterecipe', methods=['POST'])
@cross_origin(supports_credentials=True)
def update_rec():
    
#     image_file = request.get_json()["file"]
    rec_name = request.get_json()["recname"]
    rec_ing = request.get_json()["recing"]
    rec_method = request.get_json()["recmethod"]
#     user = request.get_json()["username"]
    rec_id = request.get_json()["recid"]
    print(rec_name)
    print(rec_ing)
    print(rec_method)
    print(rec_id)
    try:
        with conn.cursor() as cur:

            cur.execute(
               "UPDATE Recipes SET recipe_name = %s, recipe_ingredients = %s, recipe_methods = %s WHERE id = %s", (rec_name, rec_ing, rec_method, rec_id)
                            )

    #             upload(image_file, public_id=image_name)
        return jsonify("done sending file :)")
                            
    except:
        return jsonify("Server Down!!!!")


@app.route('/deleterecipe', methods=['POST'])
@cross_origin(supports_credentials=True)
def delete_rec():
    rec_id = request.get_json()["id"]
    rec_img = request.get_json()["img_path"]
    
    try:
        with conn.cursor() as cur:

            cur.execute(
               f"""DELETE FROM Recipes WHERE id='{rec_id}'"""
                            )
        
        destroy(rec_img)

    #             upload(image_file, public_id=image_name)
        return jsonify("done :)")
                            
    except:
        return jsonify("Server Down!!!!")
    



app.run(host='0.0.0.0', port=1337)
