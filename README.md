# pdc-backend

## Instruções para instalação do psycopg2 e Flask

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

## Execução

Antes de executar é necessário exportar uma variável de ambiente para o Flask poder trabalhar, usando o seguinte comando dentro da pasta **/controllers**:
```
export FLASK_APP=statistics_controller.py
```

Então, para executar o servidor, utilize:
```
flask run
```
