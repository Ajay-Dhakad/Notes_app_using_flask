from flask import Flask,redirect,render_template,request,session
from flask_sqlalchemy import SQLAlchemy
import bcrypt


app=Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notesapp.db'


db=SQLAlchemy(app)

app.secret_key="your_secret_key"

class Notes(db.Model):
    id= db.Column('id',db.Integer ,primary_key=True )
    userid= db.Column('userid',db.String(50),nullable=False)
    notetitle=db.Column('notetitle',db.String(100),nullable=True)
    notedesc=db.Column('notedesc',db.String(250),nullable=False)


class Users(db.Model):
    id = db.Column('id',db.Integer ,primary_key=True )
    name = db.Column("name",db.String(50),nullable=False,) 
    email = db.Column("email",db.String(50),unique=True,nullable=False)  
    password = db.Column("password",db.String(50),nullable=False)


    def __init__(self,name,email,password):

        self.name=name
        self.email=email
        self.password=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')

    def check_pass(self,password):  

        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    

with app.app_context():
    db.create_all()

@app.route('/signup',methods=['GET','POST'])

def signup():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')

        new_user=Users(name=name,email=email,password=password)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template('signup.html')




@app.route('/login',methods=['GET','POST'])

def login():

    if 'user' in session:
        return redirect("/")
    
    elif request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        user=Users.query.filter_by(email=email).first()

        if user and Users.check_pass:

            session['user']=user.email

            return redirect("/")




    return render_template('login.html')


@app.route("/",methods=['GET','POST'])
def notes():    

    if 'user' in session:
        if request.method=='POST':

            title = request.form.get('title')
            desc= request.form.get('desc')

            new_note=Notes(notetitle=title,notedesc=desc,userid=session['user'])
            
            db.session.add(new_note)
            db.session.commit()

        user = Users.query.filter_by(email=session['user']).first() #to get the name

        notes=Notes.query.filter_by(userid=session['user']).all()       #to get the notes of the user

        notes=reversed(notes)

        return render_template("notes.html" , user = user,notes=notes)
    
    return render_template('login.html')



@app.route('/delete/<int:id>')

def delete(id):
    if "user" in session :
        note= Notes.query.filter_by(id=int(id)).first()
        db.session.delete(note)
        db.session.commit()

        return redirect('/')
    return redirect('/login')


@app.route('/edit/<int:id>',methods=['GET','POST'])

def update(id):

    if  "user" in session:
        

        if request.method=='POST':

            note= Notes.query.filter_by(id=int(id)).first()

            title=request.form.get('title')
            desc=request.form.get('desc')

            note.notetitle=title
            note.notedesc=desc

            db.session.commit()

            return redirect('/')
        
        notes=Users.query.filter_by(email=session['user']).first()
        note= Notes.query.filter_by(id=int(id)).first()
        return render_template ('update.html',note=note,notes=notes)


@app.route('/logout')
def logout():
    
        
    
    session.pop('user',None)

    
    return redirect('/login')


if __name__=="__main__":
    app.run(debug=True)

