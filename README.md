# pdc-backend

## Instruções para instalação de dependências

**Obs:** é necessário ter o pip (instalador de pacotes python) instalado em sua máquina.

Para instalar o Flask, execute:
```
pip install Flask
```

Para instalar o psycopg2, execute:
```
pip install psycopg2-binary
```

## Ferramenta para testes
```
pip install -U pytest
```

Se durante a instalação, ocorrer o seguinte erro:
```
Failed building wheel for scandir
```

Instale o scandir
```
pip install scandir
```

Atualize o pip
```
pip install --upgrade pip
```

Para executar os testes, execute:
```
pytest
```

## Variáveis de ambiente

É necessário instalar o módulo jproperties para poder carregar o arquivo .properties com as credenciais de acesso ao banco de dados.

```
pip install jproperties
```

## Dependências de desenvolvimento

Para instalar o livereload, para reinicio autómatico do servidor após atualizações, execute:
```
pip install livereload
```

## Documentação da API

Para instalar a biblioteca que gerencia a documentação da API, digite:
```
pip install flask_swagger_ui
```
Para visualizar a documentação da API, basta acessar a rota **/api/swagger**

## Execução da aplicação

Após instalar todas as dependências, para executar a aplicação basta executar o seguinte comando na raiz do projeto
```
python run.py
```
