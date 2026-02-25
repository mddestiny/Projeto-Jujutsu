#!/usr/bin/env python
"""Script para popular o compêndio com dados do suplemento Jujutsu Kaisen"""

import json
from app import app, db, Criatura, Ritual, ItemAmaldicoado

def populate():
    with app.app_context():
        # ========== CRIATURAS ==========
        
        mahoraga = Criatura(
            nome="Mahoraga",
            tipo="Shikigami - Dez Sombras",
            elemento="Conhecimento",
            vd=320,
            descricao="General Divino Mahoraga é o Shikigami mais forte das Dez Sombras. Possui forma humanoide extremamente musculosa de pele pálida, com dois pares de asas no lugar dos olhos. Seu poder de adaptação é praticamente infinito.",
            habilidades=json.dumps([
                {"nome": "Adaptabilidade", "desc": "Se torna imune a rituais e efeitos após resistir ou passar no teste"},
                {"nome": "Dissipar Ritual", "desc": "Pode dissipar efeitos paranormais com ataque especial"},
                {"nome": "Energia Reversa", "desc": "Cura Acelerada 10"},
                {"nome": "Espada do Extermínio", "desc": "Ataque que causa 4d10+40 dano de Conhecimento"}
            ]),
            imagem=""
        )
        
        sumido = Criatura(
            nome="Sumido",
            tipo="Criatura Paranormal",
            elemento="Sangue",
            vd=60,
            descricao="Criatura minúscula que surge de pessoas desastradas. Amontoado de pés perdidos de meias, dentes de chaves, olhos de adaptadores de tomada e língua de cabos.",
            habilidades=json.dumps([
                {"nome": "Barriga Baú", "desc": "Armazena itens até peso 2, pode guardar itens amaldiçoados"},
                {"nome": "Oculto nas Sombras", "desc": "Pode se movimentar através de objetos quando não visto"},
                {"nome": "Sumiço", "desc": "Desaparece com item do alvo"}
            ]),
            imagem=""
        )
        
        db.session.add(mahoraga)
        db.session.add(sumido)
        
        # ========== RITUAIS ==========
        
        ilimitado = Ritual(
            nome="Ilimitado",
            circulo=1,
            elemento="Energia",
            execucao="Movimento",
            alcance="Pessoal",
            duracao="Sustentado",
            descricao="Ritual que aplica conceitos físicos e abstratos na Realidade, gerando distorções no espaço.",
            efeito="Cria barreira invisível que afasta todas as coisas. +5 Defesa, +2 resistência a dano e testes de resistência. Pode criar esferas Azul (atração), Vermelha (repulsão) ou Roxa (destruição).",
            aprimoramentos="Discente (+2 PE): Azul como teleporte, Vermelho com repulsão maior. Verdadeiro (+9 PE): Infinito (metade de dano), Roxo (destruição massiva)."
        )
        
        dez_sombras = Ritual(
            nome="Dez Sombras",
            circulo=1,
            elemento="Conhecimento",
            execucao="Padrão",
            alcance="Pessoal",
            duracao="Sustentado",
            descricao="Ritual que permite invocar até 10 Shikigamis das Dez Sombras.",
            efeito="Invoca aliados: Cães Divinos (+5 perícias), Fuga do Coelho (+5 Defesa), Gama (sapo), Nue (pássaro voo 9m), Orochi (serpente), Elefante Máximo (água).",
            aprimoramentos="Discente: Nue, Orochi, Elefante. Verdadeiro: Tigre Fúnebre, Touro Perfurante, Cervo Circular, Mahoraga."
        )
        
        dominio_sangue = Ritual(
            nome="Domínio de Sangue",
            circulo=1,
            elemento="Sangue",
            execucao="Reação",
            alcance="Curto",
            duracao="Sustentado",
            descricao="Ritual que converte PV em Pontos de Sangue para usar habilidades blood-based.",
            efeito="Converte PV em Pontos de Sangue (1 PV = 2 Pontos). Pode usar para criar armas, disparar sangue (3d6 dano), criar defesa (3 RD) ou regeneração.",
            aprimoramentos="Sem aprimoramentos formais, mas efeitos escalam com NEX."
        )
        
        db.session.add(ilimitado)
        db.session.add(dez_sombras)
        db.session.add(dominio_sangue)
        
        # ========== ITENS AMALDIÇOADOS ==========
        
        amarra = ItemAmaldicoado(
            nome="Amarra Obscura",
            categoria=4,
            elemento="Conhecimento",
            tipo="Arma/Utensílio",
            descricao="Corda amaldiçoada feita ao longo de gerações com sigilos do Outro Lado. Tem a capacidade de reescrever temporariamente a Realidade, enfraquecendo manifestações Paranormais.",
            habilidades=json.dumps([
                {"nome": "Arma", "desc": "1d8 dano Conhecimento, alcance 4,5m, crítico x2"},
                {"nome": "Neutralização Completa", "desc": "5 cargas: dano e resistências reduzidos pela metade"},
                {"nome": "Amarrar", "desc": "Impossibilita alvo de usar habilidades paranormais, perde 2 cargas/rodada"}
            ]),
            preco="Especial",
            imagem=""
        )
        
        db.session.add(amarra)
        
        db.session.commit()
        print("✓ Compêndio populado com sucesso!")
        print("✓ 2 Criaturas adicionadas (Mahoraga, Sumido)")
        print("✓ 3 Rituais adicionados (Ilimitado, Dez Sombras, Domínio de Sangue)")
        print("✓ 1 Item adicionado (Amarra Obscura)")

if __name__ == "__main__":
    populate()
