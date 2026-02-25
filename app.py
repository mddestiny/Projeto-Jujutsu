from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "jujutsu_secreto"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# -----------------------------
# Models
# -----------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Ficha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cla = db.Column(db.String(100), nullable=False)
    nivel = db.Column(db.String(100), nullable=False)
    energia = db.Column(db.Integer, nullable=False)
    tecnica = db.Column(db.String(200), nullable=False)
    habilidades = db.Column(db.Text, nullable=False)
    forca = db.Column(db.Integer, default=50)
    agilidade = db.Column(db.Integer, default=50)
    defesa = db.Column(db.Integer, default=50)
    especial = db.Column(db.String(200), default="")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------------
# Rotas de autenticação
# -----------------------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Usuário já existe!")
            return redirect(url_for("register"))
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash("Conta criada! Faça login.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        flash("Usuário ou senha incorretos!")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# -----------------------------
# Home / CRUD fichas
# -----------------------------
@app.route("/")
@login_required
def home():
    fichas = Ficha.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", fichas=fichas)

@app.route("/criar_ficha", methods=["POST"])
@login_required
def criar_ficha():
    nova_ficha = Ficha(
        nome=request.form.get("nome"),
        cla=request.form.get("cla"),
        nivel=request.form.get("nivel"),
        energia=int(request.form.get("energia")),
        tecnica=request.form.get("tecnica"),
        habilidades=request.form.get("habilidades"),
        forca=int(request.form.get("forca",50)),
        agilidade=int(request.form.get("agilidade",50)),
        defesa=int(request.form.get("defesa",50)),
        especial=request.form.get("especial",""),
        user_id=current_user.id
    )
    db.session.add(nova_ficha)
    db.session.commit()
    flash("Feiticeiro criado!")
    return redirect(url_for("home"))

@app.route("/editar_ficha/<int:ficha_id>", methods=["GET","POST"])
@login_required
def editar_ficha(ficha_id):
    ficha = Ficha.query.get_or_404(ficha_id)
    if ficha.user_id != current_user.id:
        flash("Não autorizado")
        return redirect(url_for("home"))
    if request.method == "POST":
        ficha.nome = request.form.get("nome")
        ficha.cla = request.form.get("cla")
        ficha.nivel = request.form.get("nivel")
        ficha.energia = int(request.form.get("energia"))
        ficha.tecnica = request.form.get("tecnica")
        ficha.habilidades = request.form.get("habilidades")
        ficha.forca = int(request.form.get("forca"))
        ficha.agilidade = int(request.form.get("agilidade"))
        ficha.defesa = int(request.form.get("defesa"))
        ficha.especial = request.form.get("especial")
        db.session.commit()
        flash("Ficha atualizada!")
        return redirect(url_for("home"))
    return render_template("editar_ficha.html", ficha=ficha)

@app.route("/deletar_ficha/<int:ficha_id>")
@login_required
def deletar_ficha(ficha_id):
    ficha = Ficha.query.get_or_404(ficha_id)
    if ficha.user_id != current_user.id:
        flash("Não autorizado")
        return redirect(url_for("home"))
    db.session.delete(ficha)
    db.session.commit()
    flash("Ficha deletada!")
    return redirect(url_for("home"))

# -----------------------------
# Rodar app
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)