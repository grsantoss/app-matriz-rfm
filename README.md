# Matriz RFM

Uma aplicação completa para análise RFM (Recency, Frequency, Monetary) de clientes, com integração OpenAI para geração de insights estratégicos.

## Visão Geral

Matriz RFM é uma aplicação SaaS que permite às empresas analisar o comportamento de seus clientes utilizando a metodologia RFM:

- **Recency**: Quão recentemente um cliente realizou uma compra
- **Frequency**: Com que frequência o cliente compra
- **Monetary**: Quanto dinheiro o cliente gasta

A aplicação segmenta os clientes em diferentes categorias e gera insights estratégicos utilizando a API OpenAI para ajudar empresas a tomar decisões de marketing mais eficazes.

## Características

- **Análise RFM completa**: Upload de dados, processamento e segmentação de clientes
- **Integração com OpenAI**: Geração automatizada de insights de marketing estratégicos
- **Previsão de Churn**: Identificação de clientes com risco de abandono
- **Otimização de LTV**: Sugestões para melhorar o valor vitalício do cliente
- **Autenticação JWT**: Sistema de login seguro com JWT
- **Recuperação de Senha**: Processo de recuperação de senha usando Amazon SES
- **Arquitetura Microserviços**: Serviços separados para autenticação, backend e frontend
- **Totalmente Dockerizado**: Fácil de configurar e executar em qualquer ambiente

## Tecnologias

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: FastAPI (Python), SQLAlchemy
- **Autenticação**: Node.js, Express, JWT
- **Banco de Dados**: PostgreSQL
- **Análise de Dados**: Pandas, NumPy, scikit-learn
- **IA**: Integração com OpenAI API
- **Infraestrutura**: Docker, Docker Compose, Traefik

## Requisitos

- Docker e Docker Compose
- Conta OpenAI (para a API)
- Conta Amazon SES (para emails de recuperação de senha)

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/matriz-rfm.git
cd matriz-rfm
```

2. Copie o arquivo de exemplo de configuração:

```bash
cp .env.example .env
```

3. Edite o arquivo `.env` com suas configurações (API keys, credenciais de banco de dados, etc.)

4. Inicie os serviços com Docker Compose:

```bash
docker-compose up -d
```

5. Acesse a aplicação em:

```
http://localhost:3000
```

Ou, se você configurou os domínios locais, acesse:

```
http://matrizrfm.local
```

## Estrutura do Projeto

```
matriz-rfm/
├── frontend/          # HTML, CSS, JavaScript
├── backend/           # API FastAPI (Python)
│   ├── main.py        # Entrypoint
│   ├── routes/        # Endpoints da API
│   ├── models/        # Modelos da base de dados
│   ├── rfm_service.py # Serviço de análise RFM
│   └── tests/         # Testes unitários
├── auth/              # Serviço de autenticação (Node.js)
│   ├── models/        # Modelos de usuário e tokens
│   ├── controllers/   # Controladores de autenticação
│   └── routes/        # Rotas de autenticação
├── database/          # Scripts SQL e configurações
├── config/            # Configurações compartilhadas
├── docker-compose.yml # Configuração Docker
└── traefik/           # Configuração do proxy reverso
```

## Uso da Aplicação

### 1. Criar uma Conta

- Acesse a página de cadastro
- Preencha seus dados e crie uma conta
- Faça login com suas credenciais

### 2. Upload de Dados para Análise RFM

- Prepare seu arquivo CSV ou Excel com os seguintes campos:
  - customer_id: ID único do cliente
  - transaction_id: ID único da transação
  - transaction_date: Data da transação
  - transaction_amount: Valor da transação
- Navegue até a página de análise e faça o upload do arquivo
- Aguarde o processamento da análise

### 3. Visualização dos Resultados

- Explore os segmentos de clientes identificados
- Visualize métricas e distribuições de clientes
- Leia os insights estratégicos gerados pela IA
- Exporte os resultados ou compartilhe com sua equipe

## Desenvolvimento

### Executar Testes

```bash
# Testes do backend
cd backend
pytest

# Testes da autenticação
cd auth
npm test
```

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um pull request.

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

## Contato

Para qualquer dúvida ou sugestão, por favor, entre em contato. #
