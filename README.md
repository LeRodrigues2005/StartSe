# Site de Investimentos
## Descrição
Este projeto é um site de investimentos onde os usuários podem cadastrar suas empresas, lançar propostas de investimentos para outras empresas e aceitar ou negar propostas de investimentos recebidas. 

## Tecnologias Utilizadas
Este projeto foi desenvolvido utilizando **Python** com o framework **Django**. Também houve um trabalho significativo com HTML, CSS e JavaScript para estruturar as páginas, mas a principal linguagem utilizada é Python.

## Recomendações 
- Ter o <a href="https://code.visualstudio.com">Visual Studio Code</a> instalado.  
- Utilizar a extensão *SQLite Viewer* para melhor visualização do banco de dados.
- Rodar o código dentro do ambiente virtual.

## Executando o Projeto
Para rodar o projeto, é recomendável usar um **ambiente virtual**. Siga estes passos:

Ative o ambiente virtual com o comando: `.\venv\Scripts\Activate`
Execute o servidor com o comando: `python manage.py runserver`

Clique no link que aparecerá no terminal para abrir a página no localhost:

<p align="center">
<img src="https://github.com/user-attachments/assets/5d8439aa-e409-4fcb-8664-279a2797f0d9" alt="" width="600">
</p>

## Banco de Dados
O projeto utiliza o banco de dados **db.sqlite3**. Alguns nomes de usuários e senhas foram pré-criados para fins de teste e estão salvos no banco de dados.

## Funcionalidades e Detalhes
Abaixo estão os passos e funcionalidades da plataforma, cada um acompanhado por imagens para melhor compreensão:

### 1. **Iniciando a Aplicação:**
Após rodar o servidor e clicar no link no terminal, a página será aberta no localhost, iniciando com a seguinte interface:
<p align="center">
<img src="https://github.com/user-attachments/assets/ac835055-8e92-40bd-b4cc-351b002b080f" alt="" width="900">
</p>

### 2. **Cadastro de Usuário:**
Crie um novo nome de usuário e senha para se registrar.

*Obs: Se o nome de usuário já estiver registrado, você será redirecionado para a página de login.*

<p align="center">
<img src="https://github.com/user-attachments/assets/ac835055-8e92-40bd-b4cc-351b002b080f" alt="" width="500">
</p>

### 3. **Segurança das Senhas:**
As senhas são armazenadas no banco de dados e protegidas usando PBKDF2 (Password-Based Key Derivation Function 2) com o algoritmo de hash SHA-256.

<p align="center">
<img src="https://github.com/LeRodrigues2005/StudyAsync/assets/97632543/d44a1c56-f527-4647-91e0-0c28f32590e3" alt="" width="400">
</p>

