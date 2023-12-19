# Rules System

## Visão geral

O RulesSystem é uma API baseada em [Chalice](https://aws.github.io/chalice/index.html) que é capaz de orquestrar diferentes ações de acordo com regras de condicionamento dinâmicas. Por exemplo, a API é capaz de disparar um E-mail quando um venda de determinado valor acontece.

As ações que a API pode tomar são:
* Execução de um script customizável Python
* Disparo de email
* Chamada à um Webhook externo

E as condições de acionamento de ações são:
* `is`
* `is_not`
* `is_empty`
* `is_not_empty`
* `contains`
* `does_not_contain`
* `starts_with`
* `ends_with`

Atualmente a API suporta eventos para:
* Novos pedidos
* Novos pagamentos

Em outras palavras, com todas essas integrações acima, é possivel criar regras para as mais variadas necessidades, por exemplo:

* Disparar um Email para a diretoria quando uma ordem de pedido for internacional
* Acionar um Webhook externo quando um cliente comprar 20 produto em uma só compra
* Dar baixa no banco de dados quando um pagamento acontecer
* etc...

![image](https://github.com/alissonpelizaro/rules-system/.assets/infra.png)
![image](https://github.com/alissonpelizaro/rules-system/.assets/Diagram.drawio.png)

As definições de todas as rotas podem ser acessadas [aqui](https://documenter.getpostman.com/view/28677630/2s9Ykoe2N8).

## Requerimentos
* Python ^3.11.1
* Docker e Docker Compose (necessário para subir os serviços de dependências: Redis e PostgreSQL)

## Recomendações
* [asdf](https://asdf-vm.com/#/core-manage-asdf?id=install) - para instalar e gerenciar diferentes versões do Python
* [direnv](https://github.com/asdf-community/asdf-direnv) - para gerenciar ambientes virtuais

## Como executar

### Dependências
Após clonar e acessar o projeto, e com seu ambiente virtual Python devidamente ativado (saiba como ativar [aqui](https://www.infoworld.com/article/3239675/virtualenv-and-venv-python-virtual-environments-explained.html)), execute o seguinte comando para instalar as dependências do projeto:

```sh
$ pip install -r requirement.txt
```

### Migração do Banco de dados
Para faciliar a execução local, há um `Makefile` com os comandos prontos. Se seu SO for compatível com comandos `make`, execute o seguinte comando para criar e executar a migração do banco de dados:

```sh
$ make migrate
```

Caso seu SO não seja compatível com comandos `make`, execute:
```sh
$ docker compose up -d postgres
$ alembic upgrade head
```

### Iniciando os serviços
 Se seu SO for compatível com comandos `make`, execute o seguinte comando para subir a aplicação:

```sh
$ make up
```

Caso seu SO não seja compatível com comandos `make`, execute:
```sh
$ docker compose up -d
$ chalice local
```

## Conhecendo as API
A API possui CRUD para todas as entidades existentes. São elas:

### /rule_actions
São as ações que uma regra pode acionar. A mesma ação pode ser acionada por diferentes regras.
* GET `/rule_actions/{ID}`: Obtém uma ação pelo ID
* POST `/rule_actions`: Cria uma ação
* PUT `/rule_actions/{ID}`: Atualiza uma ação pelo ID
* DELETE `/rule_actions/{ID}`: Deleta uma ação pelo ID

O payload de uma ação para as rotas POST e PUT é:

Exemplo pro tipo Webhook
```json
{
    "name": "Minha ação que chama um Webhook",
    "action": "webhook",
    "data": "https://webhook.site/4000aa7e-519f-451e-ad8c-e4c9f5a35df0"
}
```

Exemplo pro tipo Email
```json
{
    "name": "Minha ação que manda um email",
    "action": "email",
    "data": "seu.email@github.com"
}
```

Exemplo pro tipo Fulfillment
```json
{
    "name": "Minha ação que executa Python!",
    "action": "fulfillment",
    "data": "print('Sou um script Pyhton!')"
}
```


### /rules
São as regras que contém condições dinâmicas de acordo com um evento.

* GET `/rules/{ID}`: Obtém uma regra pelo ID
* POST `/rules`: Cria uma regra
* PUT `/rules/{ID}`: Atualiza uma regra pelo ID
* DELETE `/rules/{ID}`: Deleta uma regra pelo ID

O payload de uma ação para as rotas POST e PUT é:
```json
{
    "name": "Minha regra",
    "entity": "payment",
    "enabled": true,
    "filters": [
        {
            "key": "country",
            "operation": "is_not",
            "value" : "Brazil"
        }
    ],
    "actions": [
        "{ID DA AÇÃO}",
        "{ID DE OUTRA AÇÃO}"
    ]
}
```
> Nessa regra, a condição é: Quando um pagamento não for do Brasil, executa as ações definidas em `actions`

Uma regra pode ter multiplos filtros. As operações suportadas são:
* `is`
* `is_not`
* `is_empty`
* `is_not_empty`
* `contains`
* `does_not_contain`
* `starts_with`
* `ends_with`


### /orders e /payments
São os eventos que a API suporta atualmente. O conteudo/payload desses eventos são prerrogativa do cliente/usuário.
* GET `/orders/{ID}` ou `/payments/{ID}`: Obtém um evento pelo ID
* POST `/orders` ou `/payments`: Cria um evento
* PUT `/orders/{ID}` ou `/payments/{ID}`: Atualiza um evento pelo ID
* DELETE `/orders/{ID}` ou `/payments/{ID}`: Deleta um evento pelo ID

O payload dessas entidades são dinamicos, fazendo com que seja possível criar diferentes regras para diferentes tipos de conteúdo. Se quisermos acionar a regra criada anteriormente nesse README, devemos POSTAR um evento do tipo pagamento assim:

POST: `/payments`
```json
{
    "client": "Steve Jobs",
    "order": 123456, 
    "value": 155.02,
    "method": "PIX",
    "status": "completed",
    "country": "France"
}
```
> NOTA: Esse evento de pagamento acionará a regra criada anteriormente, pois o "country" não é "Brazil"

IMPORTANTE: As entidade de evento (`orders` e `payloads`) não possuem uma estrutura de dados definidas, elas são flexiveis. Isso significa que a definição de como é um pedido ou pagamento é feita pelo cliente que esta mandando essas ações.
Ex: se o cliente quiser postar um pedido apenas com essa informação abaixo, ele pode.
```json
{
  "value": 155.02,
}
```

## Testes
A API está com uma ótima cobertura de testes. Possui testes de integração em todos os endpoints e testes unitários em todas as regras de negócio. Para rodar os testes, basta executar:

```sh
pytest
```