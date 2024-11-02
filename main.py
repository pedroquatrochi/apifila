from fastapi import FastAPI, HTTPException, status
from datetime import datetime

app = FastAPI()

fila = []
id_counter = 0  # Inicia o contador de IDs a partir de 0

# Modelo de cliente
class Cliente:
    def __init__(self, id: int, nome: str, tipo_atendimento: str, posicao: int):
        self.id = id
        self.nome = nome
        self.tipo_atendimento = tipo_atendimento
        self.data_chegada = datetime.now()
        self.posicao = posicao
        self.atendido = False

@app.get("/")
def home():
    return {"mensagem": "Prova API e Microsserviços"}

# Endpoint para listar a fila
@app.get("/fila/")
def listar_fila():
    fila_ativa = [
        {"id": cliente.id, "posicao": cliente.posicao, "nome": cliente.nome, "data_chegada": cliente.data_chegada}
        for cliente in fila if not cliente.atendido
    ]
    
    if not fila_ativa:
        return {"mensagem": "A fila está vazia"}
    
    return fila_ativa

# Endpoint para obter um cliente específico pelo ID
@app.get("/fila/{id}")
def obter_cliente(id: int):
    cliente = next((cliente for cliente in fila if cliente.id == id), None)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    
    return {
        "id": cliente.id,
        "posicao": cliente.posicao,
        "nome": cliente.nome,
        "data_chegada": cliente.data_chegada,
        "atendido": cliente.atendido
    }

# Endpoint para adicionar cliente
@app.post("/fila")
def adicionar_cliente(nome: str, tipo_atendimento: str):
    global id_counter
    if len(nome) > 20 or tipo_atendimento not in ['N', 'P']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados inválidos")
    
    posicao = len(fila)
    cliente = Cliente(id=id_counter, nome=nome, tipo_atendimento=tipo_atendimento, posicao=posicao)
    fila.append(cliente)
    id_counter += 1  # Incrementa o ID após a criação do cliente
    return {"mensagem": "Cliente adicionado com sucesso", "id": cliente.id, "posicao": posicao}

# Endpoint para avançar o próximo cliente na fila
@app.put("/fila")
def atualizar_fila():
    proximo_cliente = next((cliente for cliente in fila if not cliente.atendido), None)
    if not proximo_cliente:
        return {"mensagem": "Nenhum cliente na fila para ser atendido"}
    
    proximo_cliente.atendido = True
    
    for i, cliente in enumerate([c for c in fila if not c.atendido]):
        cliente.posicao = i

    return {"mensagem": "Próximo cliente atendido e fila atualizada"}

# Endpoint para remover cliente por ID
@app.delete("/fila/{id}")
def remover_cliente(id: int):
    cliente = next((cliente for cliente in fila if cliente.id == id), None)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    
    fila.remove(cliente)
    
    for i, cliente in enumerate([c for c in fila if not c.atendido]):
        cliente.posicao = i

    return {"mensagem": "Cliente removido com sucesso"}