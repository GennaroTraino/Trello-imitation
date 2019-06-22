from flask import Flask, session, redirect, url_for, request, render_template
import sqlite3 as sql

app = Flask(__name__)

conn = sql.connect('database.db')
conn.execute('DROP TABLE users')
conn.execute('DROP TABLE cards')
conn.execute('DROP TABLE cards_items')

conn.execute('CREATE TABLE users (username TEXT PRIMARY KEY, email TEXT, password TEXT)')
conn.execute('CREATE TABLE cards (nome TEXT PRIMARY KEY, proprietario TEXT)')
conn.execute('CREATE TABLE cards_items (nomeoggetto TEXT PRIMARY KEY, nome_card TEXT, descrizione TEXT, svolto INT)')
#POPOLAMENTO
conn.execute("INSERT INTO users VALUES ('pippo42','pippo42@gmail.com','pippo42');")
conn.execute("INSERT INTO users VALUES ('sasybello','sasybello@gmail.com','sasybello');")
conn.execute("INSERT INTO users VALUES ('belgatto','belgatto@gmail.com','belgatto');")
conn.execute("INSERT INTO users VALUES ('utente1','utente1@gmail.com','utente1');")
conn.execute("INSERT INTO users VALUES ('utente2','utente2@gmail.com','utente2');")

conn.execute("INSERT INTO cards VALUES  ('Progetto TecWeb6','pippo42');")
conn.execute("INSERT INTO cards VALUES  ('Progetto Terminali','pippo42');")
conn.execute("INSERT INTO cards VALUES  ('Lista Spesa','pippo42');")
conn.execute("INSERT INTO cards VALUES  ('Vacanza','belgatto');")
conn.execute("INSERT INTO cards VALUES  ('Studiare','pippo42');")

conn.execute("INSERT INTO cards_items VALUES ('Flask','Progetto TecWeb6','Implementare Flask in Python',1);")
conn.execute("INSERT INTO cards_items VALUES ('MongoDB','Progetto TecWeb6','Implementare MongoDB in Flask',0);")
conn.execute("INSERT INTO cards_items VALUES ('Controllare CSS','Progetto TecWeb6','controllare codice css',0);")
conn.execute("INSERT INTO cards_items VALUES ('Virtual Device','Progetto Terminali','configurare emulatore android studio',0);")
conn.execute("INSERT INTO cards_items VALUES ('Architettura Android','Progetto Terminali','studiare architettura di android',0);")


conn.commit() 
conn.close()
app.secret_key='chiavesegretaIHVIHVIbshwvihsiwbs'

@app.route('/')
def init():
    if session.get('username') == None:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

########## HOME ############
@app.route('/home')
def home():
    # Se non sei loggato vai a login
    if session.get('username') == None:
        return redirect(url_for('login'))


    con = sql.connect("database.db")
    con.row_factory = sql.Row
    username = session.get('username')
    cur = con.cursor()
    cur.execute("select * from users join cards on username = proprietario where username = ?",(username,))
    row = cur.fetchall()

    return render_template("index.html",username = session.get('username'),row = row)

################ Card Items ##########
@app.route('/card/<nome>',methods=['GET'])
def card(nome):
    nome_card = nome
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from cards join cards_items on nome = nome_card where nome = ?",(nome_card,))
    rows = cur.fetchall()

    return render_template("card.html",rows = rows,nome_card = nome_card,username = session.get('username'))

########### Elimina Card Items ############
@app.route('/delete/<item>')
def delete(item):
    item = item
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    con.execute("DELETE FROM cards_items where nomeoggetto = ?",(item,))
    con.commit()

    return redirect('/')
########## ADD ITEMS #########
@app.route('/add/<card>',methods = ['POST'])
def add(card):
    card = card
    if request.method == 'POST':
        con = sql.connect("database.db")
        con.row_factory = sql.Row
        nomeoggetto = request.form['nome']
        descrizione = request.form['descrizione']
        con.execute("INSERT INTO cards_items VALUES (?,?,?,?)",(nomeoggetto,card,descrizione,0,))
        con.commit()
    return redirect(url_for('/'))

############# ITEM CARD SVOLTO #########
@app.route('/done/<item>')
def done(item):
    item = item
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    con.execute("UPDATE cards_items SET svolto = 1 where nomeoggetto = ?",(item,))
    con.commit()

    return redirect('/')



######### LIST TEMP ################
@app.route('/list')
def list():
    username = session.get('username')
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    username = session.get('username')
    cur = con.cursor()
    #cur.execute("select * from (users join cards on username = proprietario )join cards_items on nome = nome_card where username = ?",(username,))
    cur.execute("select * from users join cards on username = proprietario where username = ?",(username,))
    rows = cur.fetchall()
    return render_template("list.html",rows = rows)

####### Logout ########
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('init')) 

@app.route('/login')
def login():
    return render_template("login.html")

############ Esegui Login #############
@app.route('/loginexec', methods = ['POST', 'GET'])
def loginexec():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        con = sql.connect("database.db")
        cursor = con.cursor()
        cursor.execute("select * from users where username = (?)",[username])
        for row in cursor:
            if row[0] == username and row[2] == password:
                session['username'] = row[0]
                session['email'] = row[1]
                con.close()
                return redirect(url_for('init'))
            return redirect(url_for('init'))
    return redirect(url_for('init'))

####### Esegui Registrazione #######
@app.route('/signupexec', methods = ['POST', 'GET'])
def signupexec():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            with sql.connect("database.db") as con:
                cur = con.cursor()
            
                cur.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)",(username,email,password) )
                con.commit()
                session['username'] = username
                session['email'] = email
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"
            return redirect(url_for('init'))
        finally:
            return redirect(url_for('init'))
            con.close()
    return redirect('/')

######## INSERT CARD ######## 
@app.route('/insertcard',methods = ['POST','GET'])
def insertcard():
    if request.method == 'POST':
        card = request.form['nome']
        username = session.get('username')
        con = sql.connect("database.db")
        con.row_factory = sql.Row
        con.execute("INSERT INTO cards VALUES (?,?)",(card,username,))
        con.commit()

        return redirect('/')
    return redirect('/')

########## DELETE CARD ######
@app.route('/deletecard/<card>')
def deletecard(card):
    card = card
    con = sql.connect("database.db")
    con.row_factory = sql.Row
    con.execute("DELETE FROM cards where nome = ?",(card,))
    con.commit()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug = True)