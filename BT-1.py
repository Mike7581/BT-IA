import json
import requests
from deep_translator import GoogleTranslator

print("BT: Eu estou em fase de desenvolvimento, então sou meio burro, pega leve.")
print(" ")
print("Qual é seu nome?")

# Lista de variações de saudações
saudacoes = ["oi", "oie", "olá", "oiie", "oiee", "ola"]

# Carrega a memória do assistente
def carregar_memoria():
    try:
        with open("memoria.json", "r") as arquivo:
            conteudo = arquivo.read().strip()
            return json.loads(conteudo) if conteudo else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Salva a memória do assistente
def salvar_memoria(memoria):
    with open("memoria.json", "w") as arquivo:
        json.dump(memoria, arquivo, indent=4)

# Função para resetar a memória
def memory_reset():
    with open("memoria.json", "w") as arquivo:
        json.dump({}, arquivo, indent=4)
    return "Reset concluído"

# Responde as saudações de maneira mais flexível
def tratar_saudacao(pergunta):
    for saudacao in saudacoes:
        if saudacao in pergunta.lower():
            return "Olá! Como posso ajudar?"
    return None

# Busca informações na Wikipedia
def buscar_em_wikipedia(pergunta):
    url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{pergunta.replace(' ', '_')}"
    try:
        resposta = requests.get(url).json()
        if resposta.get("lang") == "pt":  # Garante que a resposta está em português
            return resposta.get("extract")
        return None
    except requests.RequestException:
        return None

# Busca informações no DuckDuckGo
def buscar_em_duckduckgo(pergunta):
    url = f"https://api.duckduckgo.com/?q={requests.utils.quote(pergunta)}&format=json&no_html=1&skip_disambig=1"
    try:
        resposta = requests.get(url).json()
        return resposta.get("AbstractText")
    except requests.RequestException:
        return None

# Obtém a data e a hora
def buscar_data_e_hora():
    url = "http://worldtimeapi.org/api/timezone/America/Sao_Paulo"
    try:
        resposta = requests.get(url).json()
        data = resposta["datetime"].split("T")[0]
        hora = resposta["datetime"].split("T")[1][:8]
        return f"Hoje é {data} e agora são {hora}."
    except requests.RequestException:
        return "Erro ao acessar o serviço de hora."

# Obtém a resposta do assistente, tentando aprender sozinho
def obter_resposta(pergunta, memoria):
    # Verifica se a pergunta é uma saudação
    resposta_saudacao = tratar_saudacao(pergunta)
    if resposta_saudacao:
        return resposta_saudacao

    if pergunta in memoria:
        return memoria[pergunta]
    
    # Se não souber, tenta aprender automaticamente
    resposta = buscar_em_wikipedia(pergunta)
    if not resposta:
        resposta = buscar_em_duckduckgo(pergunta)

    if resposta:
        # Traduz para PT-BR se necessário
        resposta = GoogleTranslator(source="auto", target="pt").translate(resposta)
        
        memoria[pergunta] = resposta  # Salva no JSON
        salvar_memoria(memoria)
        return f"Aprendi algo novo! {resposta}"
    
    return "Não encontrei uma resposta para isso."

# Processa os comandos do usuário
def processar_comando(comando, memoria):
    comandos = {
        "meu nome é": lambda c: c.split("meu nome é ")[-1].strip(),
        "eu sou o": lambda c: c.split("eu sou o")[-1].strip(),
        "quem sou eu": lambda _: f"Você é {memoria.get('nome', 'alguém que ainda não me disse o nome')}!",
        "que dia é hoje": lambda _: buscar_data_e_hora(),
        "que horas são": lambda _: buscar_data_e_hora(),
        "o que é": lambda c: obter_resposta(c.replace("o que é ", "").strip(), memoria),
        "quem foi": lambda c: obter_resposta(c.replace("quem foi ", "").strip(), memoria),
        "quem é": lambda c: obter_resposta(c.replace("quem é ", "").strip(), memoria),
        "reset": lambda _: memory_reset()  # Corrigido para chamar a função memory_reset()
    }

    comando = comando.lower()
    
    for chave, acao in comandos.items():
        if chave in comando:
            if chave == "meu nome é":
                memoria["nome"] = acao(comando)
                salvar_memoria(memoria)
                return f"Entendido, vou te chamar de {memoria['nome']}!"
            else:
                return acao(comando) if callable(acao) else acao()
    
    return obter_resposta(comando, memoria)

# Executa o assistente
def executar_comandos():
    memoria = carregar_memoria()

    while True:
        comando = input("Você: ").strip()
        
        if comando in ["sair", "tchau", "adeus"]:
            print("BT: Até mais!")
            break
        
        resposta = processar_comando(comando, memoria)
        
        if resposta:
            print(f"BT: {resposta}")
        else:
            print("BT: Desculpe, não entendi sua pergunta.")

if __name__ == "__main__":
    executar_comandos()
