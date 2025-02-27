import sqlite3
import requests
import re
import math
from decimal import Decimal, InvalidOperation
from deep_translator import GoogleTranslator
from contextlib import contextmanager
import spacy
from datetime import datetime

# ========== BLOCO 1 - CONFIGURAÇÃO INICIAL ==========
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    print("ERRO: Execute no terminal -> python -m spacy download pt_core_news_sm")
    exit()

# ========== BLOCO 2 - BANCO DE DADOS ==========
@contextmanager
def get_db():
    conn = sqlite3.connect('memoria.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS conhecimentos (
                pergunta TEXT PRIMARY KEY,
                resposta TEXT,
                confianca INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                contexto TEXT
            );
        ''')
        conn.commit()

# ========== BLOCO 3 - FUNÇÕES PRINCIPAIS ==========
def buscar_resposta(pergunta: str) -> str | None:
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT resposta FROM conhecimentos WHERE LOWER(pergunta) = LOWER(?)",
            (pergunta.strip(),)
        )
        resultado = cursor.fetchone()
        return resultado["resposta"] if resultado else None

def salvar_resposta(pergunta: str, resposta: str, confianca: int = 1):
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO conhecimentos VALUES (?, ?, ?)",
            (pergunta.strip(), resposta, confianca)
        )
        conn.commit()

def buscar_nome_usuario() -> str:
    with get_db() as conn:
        cursor = conn.execute("SELECT nome FROM usuario WHERE id = 1")
        resultado = cursor.fetchone()
        return resultado["nome"] if resultado else "alguém que ainda não me disse o nome"

def buscar_data_e_hora() -> str:
    agora = datetime.now()
    return f"Hoje é {agora.strftime('%d/%m/%Y')} e são {agora.strftime('%H:%M:%S')}."

# ========== BLOCO 4 - MATEMÁTICA AVANÇADA ==========
def resolver_expressao(expressao: str) -> str:
    try:
        # Remove caracteres indesejados, mas permite letras para funções
        expressao_limpa = re.sub(r'[^a-zA-Z\d\.\+\-\*\/\^\(\) ]', '', expressao)
        
        # Substitui o símbolo '^' por '**'
        expressao_limpa = expressao_limpa.replace('^', '**')
        
        # Verifica caracteres permitidos (letras e dígitos inclusos)
        if not re.match(r'^[a-zA-Z\d\.\+\-\*\/\(\) ]+$', expressao_limpa):
            return "Expressão inválida"
            
        # Cálculo preciso com Decimal e funções matemáticas
        result = eval(expressao_limpa, {'__builtins__': None}, {
            'Decimal': Decimal,
            'sqrt': math.sqrt,
            'sen': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'pi': math.pi,
            'abs': abs,
            'exp': math.exp,
            'fact': math.factorial,
            'log10': math.log10
        })
        
        # Se o resultado for um float inteiro, converte para int
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        
        return f"Resultado: {round(result, 6)}"
        
    except (SyntaxError, ZeroDivisionError, InvalidOperation, TypeError):
        return "Não consegui resolver essa expressão"
    except Exception as e:
        return f"Erro na expressão: {str(e)}"


# ========== BLOCO 5 - APRENDIZADO E CONTEXTO ==========
def processar_aprendizado(pergunta: str) -> str:
    # Verifica se é uma pergunta matemática
    if re.match(r'(quanto é|calcule|resolva)', pergunta, re.IGNORECASE):
        expressao = re.sub(r'(quanto é|calcule|resolva)', '', pergunta, flags=re.IGNORECASE)
        return resolver_expressao(expressao)
    
    # Processamento de contexto
    doc = nlp(pergunta)
    entidades = [ent.text for ent in doc.ents]
    
    if entidades:
        with get_db() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO usuario (id, contexto) VALUES (1, ?)",
                (entidades[0],)
            )
            conn.commit()
    
    # Busca em fontes externas
    resposta = buscar_em_wikipedia(pergunta) or buscar_em_duckduckgo(pergunta)
    
    if resposta:
        try:
            resposta_traduzida = GoogleTranslator(source="auto", target="pt").translate(resposta)
            salvar_resposta(pergunta, resposta_traduzida)
            return f"Aprendi: {resposta_traduzida}"
        except:
            return "Não consegui traduzir a resposta"
    
    return "Não sei responder isso. Pode me explicar?"

# ========== BLOCO 6 - FUNÇÕES DE BUSCA ==========
def buscar_em_wikipedia(pergunta: str) -> str | None:
    try:
        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{pergunta.replace(' ', '_')}"
        resposta = requests.get(url, timeout=5).json()
        return resposta.get("extract") if resposta.get("lang") == "pt" else None
    except Exception:
        return None

def buscar_em_duckduckgo(pergunta: str) -> str | None:
    try:
        url = f"https://api.duckduckgo.com/?q={requests.utils.quote(pergunta)}&format=json&no_html=1"
        resposta = requests.get(url, timeout=5).json()
        return resposta.get("AbstractText")
    except Exception:
        return None

# ========== BLOCO 7 - PROCESSAMENTO DE COMANDOS ==========
def processar_comando(comando: str) -> str:
    RESPOSTAS_PADRAO = {
        "oi": "Olá! Como posso ajudar? 😊",
        "olá": "Oi! Tudo bem com você?",
        "bom dia": "Bom dia! Que posso fazer por você hoje?",
        "boa tarde": "Boa tarde! Como posso ajudar?",
        "boa noite": "Boa noite! Precisa de ajuda com algo?",
        "quem é você": "Sou a BT, sua assistente inteligente!",
        "você é uma ia": "Sim! Fui programada para aprender e ajudar.",
        "que dia é hoje": buscar_data_e_hora,
        "que horas são": buscar_data_e_hora,
        "quem sou eu": lambda: f"Você é {buscar_nome_usuario()}!",  # Adicionado vírgula para manter o código válido
        "Quem desenvolveu você?": "Meu desenvolvedor é o Mike, e esta é a pagina do github dele!",
        # Novas opções para perguntas sobre o desenvolvedor
        "quem desenvolveu você": "Meu desenvolvedor é o Mike, confere o GitHub dele: https://github.com/Mike7581",
        "quem criou você": "Fui criada pelo Mike! Espia o GitHub dele: https://github.com/Mike7581",
        "quem te programou": "Fui programada pelo Mike! Dá uma olhada no GitHub dele: https://github.com/Mike7581",
        "quem é seu desenvolvedor": "Meu criador é o Mike! Confere o GitHub dele: https://github.com/Mike7581"
    }
    
    comando_limpo = comando.strip().lower()
    
    # Comandos especiais
    if "meu nome é" in comando_limpo:
        nome = comando.split("meu nome é")[-1].strip()
        with get_db() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO usuario (id, nome) VALUES (1, ?)",
                (nome,)
            )
            conn.commit()
        return f"Prazer em conhecê-lo, {nome}! Como posso ajudar?"
    
    # Respostas pré-definidas
    for padrao, resposta in RESPOSTAS_PADRAO.items():
        if padrao in comando_limpo:
            return resposta() if callable(resposta) else resposta
    
    # Processamento avançado
    return processar_aprendizado(comando)


# ========== BLOCO 8 - EXECUÇÃO PRINCIPAL ==========
def executar_assistente():
    init_db()
    print("BT: Olá! Sou a BT. Como posso ajudar?")
    
    while True:
        try:
            entrada = input("Você: ").strip()
            
            if not entrada:
                continue
                
            if entrada.lower() in ["sair", "exit", "adeus"]:
                print("BT: Até mais! Foi um prazer ajudar.")
                break
                
            resposta = processar_comando(entrada)
            print(f"BT: {resposta}")
            
        except KeyboardInterrupt:
            print("\nBT: Até mais!")
            break
        except Exception as e:
            print(f"BT: Ocorreu um erro inesperado: {str(e)}")

if __name__ == "__main__":
    executar_assistente()