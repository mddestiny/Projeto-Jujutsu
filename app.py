from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import json
import random

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    forca = db.Column(db.Integer, default=10)
    agilidade = db.Column(db.Integer, default=10)
    defesa = db.Column(db.Integer, default=10)
    especial = db.Column(db.String(200), default="")
    # Campos C.R.I.S.
    vida = db.Column(db.Integer, default=20)
    sanidade = db.Column(db.Integer, default=20)
    esforco = db.Column(db.Integer, default=10)
    nex = db.Column(db.Integer, default=0)
    pe_turno = db.Column(db.Integer, default=10)
    pericias = db.Column(db.Text, default="[]")  # JSON
    # Sistema Jujutsu
    pea = db.Column(db.Integer, default=5)  # Pontos Energia Amaldiçoada
    trilha = db.Column(db.String(100), default="Iniciante")  # Ex: Feiticeiro, Agente
    clan = db.Column(db.String(100), default="")  # Ex: Clã Gojo, Clã Zenin
    elemento = db.Column(db.String(50), default="Conhecimento")  # Elemento paranormal
    rituais = db.Column(db.Text, default="[]")  # JSON com rituais aprendidos
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def get_pericias(self):
        """Parse perícias JSON para lista de dicts"""
        try:
            return json.loads(self.pericias) if self.pericias else []
        except:
            return []

    def set_pericias(self, pericias_list):
        """Salva perícias como JSON"""
        self.pericias = json.dumps(pericias_list)

    def add_pericia(self, nome, bonus=0):
        """Adiciona uma perícia"""
        pericias = self.get_pericias()
        pericias.append({"nome": nome, "bonus": bonus})
        self.set_pericias(pericias)

    def remove_pericia(self, nome):
        """Remove uma perícia"""
        pericias = self.get_pericias()
        pericias = [p for p in pericias if p["nome"] != nome]
        self.set_pericias(pericias)

    def get_rituais(self):
        """Parse rituais JSON"""
        try:
            return json.loads(self.rituais) if self.rituais else []
        except:
            return []

    def add_ritual(self, nome, circulo=1, elemento="Conhecimento"):
        """Adiciona um ritual"""
        rituais = self.get_rituais()
        rituais.append({"nome": nome, "circulo": circulo, "elemento": elemento})
        self.rituais = json.dumps(rituais)

class Criatura(db.Model):
    """Modelo para criaturas do compêndio"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Maldição, Criatura Paranormal, etc
    elemento = db.Column(db.String(50), nullable=False)  # Conhecimento, Medo, Sangue, etc
    vd = db.Column(db.Integer, nullable=False)  # Valor de Dificuldade
    descricao = db.Column(db.Text, nullable=False)
    habilidades = db.Column(db.Text, nullable=False)  # JSON com habilidades
    imagem = db.Column(db.String(200), default="")

class Ritual(db.Model):
    """Modelo para rituais do compêndio"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    circulo = db.Column(db.Integer, nullable=False)  # 1-4
    elemento = db.Column(db.String(50), nullable=False)  # Elemento paranormal
    execucao = db.Column(db.String(50), nullable=False)  # Movimento, Padrão, etc
    alcance = db.Column(db.String(50), nullable=False)  # Pessoal, Curto, Médio, etc
    duracao = db.Column(db.String(50), nullable=False)  # Instantâneo, Sustentado, etc
    descricao = db.Column(db.Text, nullable=False)
    efeito = db.Column(db.Text, nullable=False)  # Descrição dos efeitos
    aprimoramentos = db.Column(db.Text, default="")

class ItemAmaldicoado(db.Model):
    """Modelo para itens amaldiçoados do compêndio"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    categoria = db.Column(db.Integer, nullable=False)  # I-IV
    elemento = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Arma, Armadura, Acessório, etc
    descricao = db.Column(db.Text, nullable=False)
    habilidades = db.Column(db.Text, nullable=False)  # JSON
    preco = db.Column(db.String(50), default="")  # "R$ 30,00"
    imagem = db.Column(db.String(200), default="")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Debug endpoints
@app.route("/healthcheck")
def healthcheck():
    return "OK", 200

# -----------------------------
# Rotas de autenticação
# -----------------------------
@app.route("/register", methods=["GET","POST"])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for("home"))
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
    except Exception as e:
        logger.error(f"Erro em register: {str(e)}")
        return f"<h1>Erro: {str(e)}</h1>", 500

@app.route("/login", methods=["GET","POST"])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("home"))
            flash("Usuário ou senha incorretos!")
        return render_template("login.html")
    except Exception as e:
        logger.error(f"Erro em login: {str(e)}")
        return f"<h1>Erro: {str(e)}</h1>", 500

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
    try:
        fichas = Ficha.query.filter_by(user_id=current_user.id).all()
        return render_template("home.html", fichas=fichas)
    except Exception as e:
        logger.error(f"Erro em home: {str(e)}")
        return f"<h1>Erro: {str(e)}</h1>", 500

@app.route("/criar_ficha", methods=["POST"])
@login_required
def criar_ficha():
    nova_ficha = Ficha(
        nome=request.form.get("nome"),
        cla=request.form.get("cla"),
        nivel=request.form.get("nivel"),
        energia=int(request.form.get("energia", 50)),
        tecnica=request.form.get("tecnica"),
        habilidades=request.form.get("habilidades"),
        forca=int(request.form.get("forca", 10)),
        agilidade=int(request.form.get("agilidade", 10)),
        defesa=int(request.form.get("defesa", 10)),
        especial=request.form.get("especial", ""),
        # Campos C.R.I.S.
        vida=20,
        sanidade=20,
        esforco=10,
        nex=0,
        pe_turno=10,
        # Sistema Jujutsu
        pea=int(request.form.get("pea", 5)),
        trilha=request.form.get("trilha", "Iniciante"),
        clan=request.form.get("clan", ""),
        elemento=request.form.get("elemento", "Conhecimento"),
        user_id=current_user.id
    )
    db.session.add(nova_ficha)
    db.session.commit()
    flash("Feiticeiro criado!")
    return redirect(url_for("home"))

@app.route("/editar_ficha/<int:ficha_id>", methods=["GET","POST"])
@login_required
def editar_ficha(ficha_id):
    try:
        ficha = Ficha.query.get_or_404(ficha_id)
        if ficha.user_id != current_user.id:
            flash("Não autorizado")
            return redirect(url_for("home"))
        if request.method == "POST":
            ficha.nome = request.form.get("nome")
            ficha.cla = request.form.get("cla")
            ficha.nivel = request.form.get("nivel")
            ficha.energia = int(request.form.get("energia", 50))
            ficha.tecnica = request.form.get("tecnica")
            ficha.habilidades = request.form.get("habilidades")
            ficha.forca = int(request.form.get("forca", 10))
            ficha.agilidade = int(request.form.get("agilidade", 10))
            ficha.defesa = int(request.form.get("defesa", 10))
            ficha.especial = request.form.get("especial", "")
            # Novos campos C.R.I.S.
            ficha.vida = int(request.form.get("vida", 20))
            ficha.sanidade = int(request.form.get("sanidade", 20))
            ficha.esforco = int(request.form.get("esforco", 10))
            ficha.nex = int(request.form.get("nex", 0))
            ficha.pe_turno = int(request.form.get("pe_turno", 10))
            # Campos Jujutsu
            ficha.pea = int(request.form.get("pea", 5))
            ficha.trilha = request.form.get("trilha", "Iniciante")
            ficha.clan = request.form.get("clan", "")
            ficha.elemento = request.form.get("elemento", "Conhecimento")
            db.session.commit()
            flash("Ficha atualizada!")
            return redirect(url_for("home"))
        return render_template("editar_ficha.html", ficha=ficha)
    except Exception as e:
        logger.error(f"Erro em editar_ficha: {str(e)}")
        return f"<h1>Erro: {str(e)}</h1>", 500

@app.route("/deletar_ficha/<int:ficha_id>")
@login_required
def deletar_ficha(ficha_id):
    try:
        ficha = Ficha.query.get_or_404(ficha_id)
        if ficha.user_id != current_user.id:
            flash("Não autorizado")
            return redirect(url_for("home"))
        db.session.delete(ficha)
        db.session.commit()
        flash("Ficha deletada!")
        return redirect(url_for("home"))
    except Exception as e:
        logger.error(f"Erro em deletar_ficha: {str(e)}")
        return f"<h1>Erro: {str(e)}</h1>", 500

# Endpoint para rolar dados D20
@app.route("/api/rolar-dados")
def rolar_dados():
    """Retorna valores aleatórios de D20 para os atributos"""
    dados = {
        "forca": random.randint(1, 20),
        "agilidade": random.randint(1, 20),
        "defesa": random.randint(1, 20),
        "especial": random.randint(1, 20),
        "energia": random.randint(50, 100)
    }
    return jsonify(dados)

# Endpoints para gerenciar perícias
@app.route("/api/ficha/<int:ficha_id>/pericias", methods=["GET"])
@login_required
def get_pericias(ficha_id):
    """Retorna perícias da ficha"""
    ficha = Ficha.query.get_or_404(ficha_id)
    if ficha.user_id != current_user.id:
        return jsonify({"erro": "Não autorizado"}), 403
    return jsonify(ficha.get_pericias())

@app.route("/api/ficha/<int:ficha_id>/pericias", methods=["POST"])
@login_required
def add_pericia(ficha_id):
    """Adiciona uma perícia"""
    ficha = Ficha.query.get_or_404(ficha_id)
    if ficha.user_id != current_user.id:
        return jsonify({"erro": "Não autorizado"}), 403
    
    data = request.get_json()
    nome = data.get("nome", "Nova Perícia")
    bonus = int(data.get("bonus", 0))
    
    ficha.add_pericia(nome, bonus)
    db.session.commit()
    
    return jsonify({"sucesso": True, "pericias": ficha.get_pericias()})

@app.route("/api/ficha/<int:ficha_id>/pericias/<nome>", methods=["DELETE"])
@login_required
def delete_pericia(ficha_id, nome):
    """Remove uma perícia"""
    ficha = Ficha.query.get_or_404(ficha_id)
    if ficha.user_id != current_user.id:
        return jsonify({"erro": "Não autorizado"}), 403
    
    ficha.remove_pericia(nome)
    db.session.commit()
    
    return jsonify({"sucesso": True, "pericias": ficha.get_pericias()})

# ========== COMPÊNDIO: Criaturas, Rituais e Itens ==========

@app.route("/compendio")
@login_required
def compendio():
    """Página principal do compêndio"""
    criaturas = Criatura.query.all()
    rituais = Ritual.query.all()
    itens = ItemAmaldicoado.query.all()
    return render_template("compendio.html", criaturas=criaturas, rituais=rituais, itens=itens)

@app.route("/compendio/criatura/<int:criatura_id>")
@login_required
def view_criatura(criatura_id):
    """Visualizar criatura específica"""
    criatura = Criatura.query.get_or_404(criatura_id)
    return render_template("criatura_detail.html", criatura=criatura)

@app.route("/compendio/ritual/<int:ritual_id>")
@login_required
def view_ritual(ritual_id):
    """Visualizar ritual específico"""
    ritual = Ritual.query.get_or_404(ritual_id)
    return render_template("ritual_detail.html", ritual=ritual)

@app.route("/compendio/item/<int:item_id>")
@login_required
def view_item(item_id):
    """Visualizar item amaldiçoado específico"""
    item = ItemAmaldicoado.query.get_or_404(item_id)
    return render_template("item_detail.html", item=item)

@app.route("/api/compendio/buscar")
@login_required
def buscar_compendio():
    """Buscar no compêndio por nome/tipo"""
    query = request.args.get("q", "").lower()
    tipo = request.args.get("tipo", "todos")  # criaturas, rituais, itens
    
    resultado = {"criaturas": [], "rituais": [], "itens": []}
    
    if tipo in ["todos", "criaturas"]:
        criaturas = Criatura.query.filter(
            db.or_(
                Criatura.nome.ilike(f"%{query}%"),
                Criatura.tipo.ilike(f"%{query}%"),
                Criatura.elemento.ilike(f"%{query}%")
            )
        ).all()
        resultado["criaturas"] = [{"id": c.id, "nome": c.nome, "tipo": c.tipo, "elemento": c.elemento} for c in criaturas]
    
    if tipo in ["todos", "rituais"]:
        rituais = Ritual.query.filter(
            db.or_(
                Ritual.nome.ilike(f"%{query}%"),
                Ritual.elemento.ilike(f"%{query}%")
            )
        ).all()
        resultado["rituais"] = [{"id": r.id, "nome": r.nome, "circulo": r.circulo, "elemento": r.elemento} for r in rituais]
    
    if tipo in ["todos", "itens"]:
        itens = ItemAmaldicoado.query.filter(
            db.or_(
                ItemAmaldicoado.nome.ilike(f"%{query}%"),
                ItemAmaldicoado.elemento.ilike(f"%{query}%")
            )
        ).all()
        resultado["itens"] = [{"id": i.id, "nome": i.nome, "categoria": i.categoria, "elemento": i.elemento} for i in itens]
    
    return jsonify(resultado)

# -----------------------------
# Rodar app
# -----------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)