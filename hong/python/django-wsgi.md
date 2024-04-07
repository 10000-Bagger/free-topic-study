# Django의 WAS 운영 방식: WSGI와 Gunicorn

```python
# /django/core/servers/basehttp.py
"""
HTTP server that implements the Python WSGI protocol (PEP 333, rev 1.21).

Based on wsgiref.simple_server which is part of the standard library since 2.5.

This is a simple server for use in testing or debugging Django apps. It hasn't
been reviewed for security issues. DON'T USE IT FOR PRODUCTION USE!
"""
```

### 배경:

- Django로 만든 API 서버를 GCP에서 NGINX로 서빙하는 과정을 수행하면서 Gunicorn이라는 키워드를 얻게 되어 공부했습니다.

![스크린샷 2024-04-05 105302](https://github.com/10000-Bagger/free-topic-study/assets/34956359/13ee305d-e7e0-4206-a814-d8b99cebd457)
*Django의 WSGI는 Spring Boot에 내장된 Tomcat과 다르게, 웹 서버가 안에 내장되어 있지 않음.*

Django의 WSGI는 Spring Boot에 내장된 Tomcat과 다르게, 웹 서버가 안에 내장되어 있지 않음. 

즉, Python 진영은 WSGI 기반의 WAS, Java 진영은 Servlet 기반의 WAS 운용.

### CGI 

- Common Gateway Interface
- 2003년까지 Python Web Framework는 주로 CGI와 같은 방식으로 Web Server와 통신.
- CGI 동작 방식:
    - Web Server가 Client로부터 HTTP request를 받는다.
    - Web Server는 Request에 대한 정보 (Mathod, URL, Parameters, …)를 Env variable과 Standard Input을 통해 전달하면서 Script를 실행함.
    - Script는 비즈니스 로직을 수행하고 Standard Output으로 결과를 Web Server에게 전달.
    - Web Server는 이를 다시 Client에게 전달.
- 문제는 매번 다시 스크립트를 실행하여 메모리에 적재하는 과정에서 발생하는 추가적인 시간 소요 등임.
- 이 때 2003년에 Python 표준(PEP333)인 WSGI가 등장하게 됨.

### WSGI

- Web Server Gateway Interface
- Web Server와 Web Application을 Interchangable하게 사용하기 위해서는 잘 정의된 인터페이스가 필수.
- Python application이 웹 서버와 통신하기 위한 인터페이스로 웹 서버의 요청을 해석해서 Python application에게 전달함.
    - WSGI는 Callable Object를 통해 Web Server가 요청에 대한 정보를 Application에 전달함.
    - 대표적으로 gunicorn과 uWSGI가 있음.
- Callable Object는 Function이나 Object의 형태가 될 수 있으며, Web Server는 Callable Object를 통해 2가지 정보를 전달.
    - HTTP Request에 대한 정보 (Method, URL, Data, …)
    - Callback 함수

### Gunicorn (Green Unicorn)

- Python Web Server Gateway Interface (WSGI) HTTP 서버이다.
- Python 웹 어플리케이션의 높은 트래픽을 쉽게 처리할 수 있는 가볍고 안정적인 서버.
- Django나 Flask의 개발환경의 웹 서버는 보안적으로나, 성능적으로 검증되지 않아서 배포환경에서는 적합하지 않음.
- 그래서 Python Script, application들은 gunicorn으로 실행하고 이것을 웹 서버와 연결하는 방식으로 배포를 많이함.
- 또한 worker를 통해 multi-threads (IO bound), multi-processes (CPU bound)를 구현할 수 있어서 Request 요청이 많아지더라도 효율적으로 처리할 수 있음.
- 정리
    1. 가볍고 성능, 보안적으로 우수함.
    2. Worker를 설정함으로써 멀티 쓰레드를 구현, Request를 효율적으로 처리
    3. gunicorn이 uWSGI보다 조금 더 좋고 가벼워서 더 많이 사용됨.
    

### Gunicorn으로 Django 실행 방법

일반적으로 Django application을 실행할 때는 `python manage.py runserver` 커맨드로 실행한다. Gunicorn을 사용하는 방식도 이와 비슷하게 간단하다.

1. Gunicorn 설치

```python
pip install gunicorn
```

2. 필요하다면 설정 변경 수행
- 유요한 설정을 설명해준 블로그: [gunicorn 설정의 A to Z – 화해 블로그 | 기술 블로그](https://blog.hwahae.co.kr/all/tech/5567)

3. Gunicorn을 통해 Django application binding

```python
gunicorn --bind 0:8000 rmadmin.wsgi:application
```

이렇게 간단하게 실행이 가능하다.
