import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --- Configuração ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'trabalho-final-flask-ecommerce'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'loja.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- Modelos do Banco de Dados ---

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    # ===== NOVO CAMPO ADICIONADO =====
    imagem_url = db.Column(db.String(500), nullable=True) # URL da imagem

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pendente')
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)
    pagamento = db.relationship('Pagamento', backref='pedido', uselist=False, lazy=True)

class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    produto = db.relationship('Produto', lazy=True)


class Pagamento(db.Model):
    __tablename__ = 'pagamentos'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    tipo = db.Column(db.String(50))
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='aguardando')


# --- Criação do Banco de Dados e Inserção de Dados Iniciais ---
with app.app_context():
    db.create_all()

    if Produto.query.count() == 0:
        print("Banco de dados de produtos vazio. Inserindo produtos de exemplo...")
        
        # ===== PRODUTOS ATUALIZADOS COM IMAGEM E PREÇO =====
        
        p1 = Produto(
            nome="Teclado Fodastico",
            descricao="Uma camiseta de algodão confortável para desenvolvedores Python.",
            preco=79.90,
            estoque=50,
            imagem_url="https://mkt.multilaser.com.br/emkt/mkt/resizer/2022/laminas-html/office/TC213/assets/img/tc225_00.jpg"
        )
        
        p2 = Produto(
            nome="Caneca Python",
            descricao="Caneca de cerâmica preta (300ml) para seu café.",
            preco=39.90,
            estoque=100,
            imagem_url="https://placehold.co/600x400/2ecc71/white?text=Caneca+Python"
        )

        # ===== NOVO PRODUTO ADICIONADO =====
        p3 = Produto(
            nome="Mousepad Coder",
            descricao="Mousepad ergonômico com atalhos de VS Code.",
            preco=55.00,
            estoque=30,
            imagem_url="https://placehold.co/600x400/e74c3c/white?text=Mousepad"
        )

        p4 = Produto(
            nome="Mousepad Coder",
            descricao="Mousepad ergonômico com atalhos de VS Code.",
            preco=55.00,
            estoque=30,
            imagem_url="https://placehold.co/600x400/e74c3c/white?text=Mousepad"
        )

        p5 = Produto(
            nome="Mousepad Coder",

            
            descricao="Mousepad ergonômico com atalhos de VS Code.",
            preco=55.00,
            estoque=30,
            imagem_url="https://placehold.co/600x400/e74c3c/white?text=Mousepad"
        )

        p6 = Produto(
            nome="Mousepad Coder",
            descricao="Mousepad ergonômico com atalhos de VS Code.",
            preco=55.00,
            estoque=30,
            imagem_url="https://placehold.co/600x400/e74c3c/white?text=Mousepad"
        )

        p7 = Produto(
            nome="Mousepad Coder",
            descricao="Mousepad ergonômico com atalhos de VS Code.",
            preco=55.00,
            estoque=30,
            imagem_url="https://placehold.co/600x400/e74c3c/white?text=Mousepad"
        )
        
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.add(p5)
        db.session.add(p6)
        db.session.add(p7)
        db.session.commit()
        print("Produtos de exemplo inseridos com sucesso.")
    else:
        print("Banco de dados de produtos já contém dados.")


# --- Rotas da Aplicação ---
# (Todo o resto do código de rotas permanece o mesmo)

@app.route('/')
def index():
    """Rota Principal: Catálogo de Produtos"""
    produtos = Produto.query.all()
    return render_template('index.html', produtos=produtos)

@app.route('/produto/<int:id>')
def detalhes_produto(id):
    """Rota: Detalhes de um Produto Específico"""
    produto = Produto.query.get_or_404(id)
    # Também vamos atualizar o produto.html para mostrar a imagem
    return render_template('produto.html', produto=produto)

# --- Rotas de Autenticação (Login, Registrar, Logout) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        cliente = Cliente.query.filter_by(email=email).first()
        if cliente and cliente.check_senha(senha):
            session['cliente_id'] = cliente.id
            session['cliente_nome'] = cliente.nome
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        telefone = request.form.get('telefone')
        if Cliente.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
            return redirect(url_for('registrar'))
        novo_cliente = Cliente(nome=nome, email=email, telefone=telefone)
        novo_cliente.set_senha(senha)
        try:
            db.session.add(novo_cliente)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça o login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            return redirect(url_for('registrar'))
    return render_template('registrar.html')

@app.route('/logout')
def logout():
    session.pop('cliente_id', None)
    session.pop('cliente_nome', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))


# --- Rotas do Carrinho e Pedidos ---

@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        quantidade = int(request.form.get('quantidade'))
        produto = Produto.query.get(produto_id)
        if not produto:
            flash('Produto não encontrado.', 'danger')
            return redirect(url_for('index'))
        if 'carrinho' not in session:
            session['carrinho'] = {}
        produto_id_str = str(produto_id)
        if produto_id_str in session['carrinho']:
            session['carrinho'][produto_id_str]['quantidade'] += quantidade
        else:
            session['carrinho'][produto_id_str] = {
                'nome': produto.nome,
                'preco': float(produto.preco),
                'quantidade': quantidade
            }
        session.modified = True 
        flash(f'"{produto.nome}" adicionado ao carrinho!', 'success')
        return redirect(url_for('carrinho'))

    itens_carrinho_session = session.get('carrinho', {})
    total_carrinho = 0
    itens_para_template = []
    if itens_carrinho_session:
        for pid, item in itens_carrinho_session.items():
            subtotal = item['preco'] * item['quantidade']
            item_template = {
                'produto_id': pid,
                'nome_produto': item['nome'],
                'preco_unitario': item['preco'],
                'quantidade': item['quantidade'],
                'subtotal': subtotal
            }
            total_carrinho += subtotal
            itens_para_template.append(item_template)
    return render_template(
        'carrinho.html', 
        itens_carrinho=itens_para_template,
        total_carrinho=total_carrinho
    )


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para finalizar a compra.', 'warning')
        return redirect(url_for('login'))
    carrinho_session = session.get('carrinho', {})
    if not carrinho_session:
        flash('Seu carrinho está vazio.', 'info')
        return redirect(url_for('carrinho'))

    total_carrinho = sum(item['preco'] * item['quantidade'] for item in carrinho_session.values())
    
    if request.method == 'POST':
        tipo_pagamento = request.form.get('tipo_pagamento')
        cliente_id = session['cliente_id']
        try:
            novo_pedido = Pedido(cliente_id=cliente_id, status='processando')
            db.session.add(novo_pedido)
            db.session.flush()
            for produto_id_str, item in carrinho_session.items():
                produto_id = int(produto_id_str)
                produto = Produto.query.get(produto_id)
                if produto.estoque < item['quantidade']:
                    raise Exception(f"Estoque insuficiente para '{produto.nome}'. Temos apenas {produto.estoque} un.")
                produto.estoque -= item['quantidade']
                novo_item_pedido = ItemPedido(
                    pedido_id=novo_pedido.id,
                    produto_id=produto_id,
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco']
                )
                db.session.add(novo_item_pedido)
            novo_pagamento = Pagamento(
                pedido_id=novo_pedido.id,
                tipo=tipo_pagamento,
                valor=total_carrinho,
                status='processando'
            )
            db.session.add(novo_pagamento)
            session.pop('carrinho', None)
            session.modified = True
            db.session.commit()
            flash('Pedido realizado com sucesso!', 'success')
            return redirect(url_for('detalhes_pedido', id=novo_pedido.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao processar o pedido: {str(e)}', 'danger')
            return redirect(url_for('checkout'))

    itens_para_template = []
    for pid, item in carrinho_session.items():
        item_template = {
            'produto_id': pid,
            'nome_produto': item['nome'],
            'preco_unitario': item['preco'],
            'quantidade': item['quantidade']
        }
        itens_para_template.append(item_template)
    return render_template(
        'checkout.html', 
        itens_carrinho=itens_para_template, 
        total_carrinho=total_carrinho
    )


@app.route('/pedido/<int:id>')
def detalhes_pedido(id):
    if 'cliente_id' not in session:
        flash('Faça login para ver seus pedidos.', 'warning')
        return redirect(url_for('login'))
    pedido = Pedido.query.get_or_404(id)
    if pedido.cliente_id != session['cliente_id']:
        flash('Você não tem permissão para ver este pedido.', 'danger')
        return redirect(url_for('index'))
    pagamento = Pagamento.query.filter_by(pedido_id=id).first()
    itens_do_pedido = ItemPedido.query.filter_by(pedido_id=id).all()
    
    # **Lembrete de Correção para 'pedido.html'**:
    # Trocar `{{ item.nome_produto }}` (se existir) por `{{ item.produto.nome }}`
    
    return render_template(
        'pedido.html', 
        pedido=pedido, 
        pagamento=pagamento, 
        itens_do_pedido=itens_do_pedido
    )

# --- Execução da Aplicação ---
if __name__ == '__main__':
    app.run(debug=True)