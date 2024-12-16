# Dispather Servlet
요청은 어떻게 컨트롤러까지 도착할까? <br>

우리는 그냥 컨트롤러 클래스에 `@Controller`나 `@RestController`를 붙여준 다음, 메서드에 어노테이션을 통해 HTTP Method와 Endpoint를 넣어주면 "알아서" 수행됐다. <br>

당연히 우리가 보이지 않는 곳에서 요청을 그 컨트롤러의 그 메서드에 매핑해주는 객체가 있을텐데.. 그것이 Dispatcher Servlet이다. <br>

![image](https://github.com/binary-ho/TIL-public/assets/71186266/686ccdaa-08f3-4a19-83f8-d865f1cb71d0)

클라이언트가 요청을 보며내면, 서블릿 컨텍스트의 필터들을 거쳐 Dispatcher Servlet에 도착한다. <br> <br>


그러면 디스패처 서블릿은 클라이언트에게서 HTTP 프로토콜로 오는 모든 요청을 가장 먼저 받아서 해당 요청을 수행할 수 있는 적절한 컨트롤러를 찾아 수행을 위임한다. <br>

내부적으로 `@Controller`랑 `@RestController`가 달린 컨트롤러의 메서드 정보를 가지고 있고, 정보들을 뒤져 매핑해준다. <br>

위 그림에 interceptor가 있는데, 만약 중간에 인터셉터가 있다면 그곳을 거친다. (위 그림은 아마 필터와 인터셉터의 차이를 설명하기 위한 그림일듯?) <br>

Tomcat과 같은 서블릿 컨테이너가 요청을 받으면, Dispatcher Servlet이 컨트롤러 보다 먼저 요청을 받게 되는데, 컨트롤러 보다 먼저 요청을 받는다는 점 때문에 **Front Contoller라고도 불린다.** <br>

<br>

## 동작 과정 

![image](https://github.com/binary-ho/TIL-public/assets/71186266/6d6953fb-18c2-440c-a015-373c4c0ae507)


1. 클라이언트에게서 Dispatcher Servlet에 요청이 온다. 
2. HandlerMapping이 요청을 위임할 컨트롤러를 찾는다.
3. HandlerAdapter에게 Controller에 위임할 것을 명령한다.
4. HandlerAdapter가 Controller에게 요청을 위임한다.
5. 요청 수행
6, 7. 컨트롤러의 반환값을 다시 Dispatcher Servlet에 전달.
8. 요청을 클라이언트에게 반환한다. 

<br>

과정 중 몇 개만 좀 더 자세히 살펴보자

### 2. HandlerMapping이 요청을 위임할 컨트롤러를 찾는다.
HandlerMapping 인터페이스가 구현 방법에 따라 요청을 처리할 대상을 찾는다. 우리는 보통 `@Controller`, `@RestController`를 사용하는 방법을 이용하지만, 여러 구현체가 있고 구현체마다 객체를 찾는 방법이 다르다고 한다. 이는 RequestMappingHandlerMapping이 처리하는데, 컨트롤러 어노테이션이 붙은 클래스를 찾아, 요청 정보에 매핑되는 처리 객체를 HashMap으로 정보를 저장한다. <br>

HandlerMapping이 처리할 대상을 찾았다면 컨트롤러로 요청을 넘기기 전에 처리를 위해 HandlerExecutionChain로 감싸 반환한다.


### 3. HandlerAdapter에게 Controller에 위임할 것을 명령한다.
여기도 HandlerMapping 때처럼 다양한 구현체를 제공하기 위해 HandlerAdapter인터페이스를 통해 컨트롤러에게 명령을 위임한다. 컨트롤러의 구현방식에 상관 없이 요청을 처리할 수 있도록 중간에 인터페이스를 끼워 넣은 것이다.


### 4. HandlerAdapter가 Controller에게 요청을 위임한다.
HandlerAdapter가 Controller에게 요청을 위임하고, 전-후처리를 한다. <br>
예를 들어 실제로 컨트롤러에 닿기 전에 인터셉터나 ArgumentResolver들의  처리가 필요하다. 그리고 응답 이후에도 직렬화 등의 다양한 처리가 필요한데, 이들을 HandlerAdapter에서 처리한 다음 컨트롤러에게 넘긴다.
