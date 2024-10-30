from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Connessione a MongoDB
client = MongoClient("mongodb+srv://jofrancalanci:Cf8m2xsQdZgll1hz@element.2o7dxct.mongodb.net/")
db = client['Healthcare']
collection = db['Pediatri']

@app.route('/')
def home():
    query = request.args.get('search')
    
    if query:
        # Cerca nei campi nome, zona, e specializzazione
        pediatri = collection.find({
            "$or": [
                {"Name_med": {"$regex": query, "$options": "i"}},
                {"Surname_med": {"$regex": query, "$options": "i"}},
                {"Zone": {"$regex": query, "$options": "i"}}
            ]
        })
    else:
        pediatri = collection.find()

    return render_template('index.html', pediatri=pediatri)

if __name__ == '__main__':
    app.run(debug=True)
