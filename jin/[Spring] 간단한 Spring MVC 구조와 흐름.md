# Spring MVC 전체 구조
스프링 MVC는 DispatcherServlet이라는 객체를 활용한 프론트 컨트롤러 패턴으로 구현되어 있다. <br>
스프링 부트는 내장 톰캣을 띄우면서 DispatcherServlet을 띄운다. 그 과정에서 모든 url 경로에 대해 매핑한다. 

## 1. DispatcherServlet 요청 흐름
DispatcherServlet 요청 흐름을 내부 동작을 간단히 살펴보며 알아보자. <Br>
복잡한 내부 구조를 모두 파악하기엔 어렵고, 핵심 동작 방식만 알아보자. 그래야 나중에 내부 요소들을 확장하면서 문제를 해결할 수 있다. <Br>

1. 요청이 들어온다.
2. HttpServlet의 `service()`를 Override한 DispatcherServlet의 `service()`를 호출한다. 이는 부모 클래스 FramworkServlet에서 Override했다. <br> 다양한 요청 Method에 따라 처리할 메서드를 호출하는 것을 알 수 있다.

```java
  protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
      String method = req.getMethod();
      long lastModified;
      if (method.equals("GET")) {
          lastModified = this.getLastModified(req);
          if (lastModified == -1L) {
              this.doGet(req, resp);
          }

          ...생략

      } else if (method.equals("HEAD")) {
          lastModified = this.getLastModified(req);
          this.maybeSetLastModified(resp, lastModified);
          this.doHead(req, resp);
      } else if (method.equals("POST")) {
          this.doPost(req, resp);
      } else if (method.equals("PUT")) {
          this.doPut(req, resp);
      } else if (method.equals("DELETE")) {
          this.doDelete(req, resp);
      } else if (method.equals("OPTIONS")) {
          this.doOptions(req, resp);
      } else if (method.equals("TRACE")) {
          this.doTrace(req, resp);
      } else {
          String errMsg = lStrings.getString("http.method_not_implemented");
          Object[] errArgs = new Object[]{method};
          errMsg = MessageFormat.format(errMsg, errArgs);
          resp.sendError(501, errMsg);
      }

  }
```



3. 최종적으로 DispatcherServlet에 있는 `doDispatch()`가 호출된다.
핸들러를 찾아서 매핑하는 역할

<br>

## 1.1 `doDispatch()` 열어보기

아래의 매핑 과정들이 `doDispatch()`에서 일어난다.

![image](https://github.com/depromeet/amazing3-be/assets/71186266/b6968a7c-b6f9-4145-8c9c-a27eab750f62)

<br> <br>

```java
  // 매핑되는 핸들러가 있는지 확인한다.
  mappedHandler = this.getHandler(processedRequest);
  // 없으면 핸들러가 없음을 알린다.
  if (mappedHandler == null) {
      this.noHandlerFound(processedRequest, response);
      return;
  }
```

### 핸들러 찾는 getHandler()
HandlerMapping들을 순회하면서, 요청을 위임할 컨트롤러를 찾아줄 Handler를 찾는다.
```java
  @Nullable
  protected HandlerExecutionChain getHandler(HttpServletRequest request) throws Exception {
      if (this.handlerMappings != null) {
          Iterator var2 = this.handlerMappings.iterator();

          while(var2.hasNext()) {
              HandlerMapping mapping = (HandlerMapping)var2.next();
              HandlerExecutionChain handler = mapping.getHandler(request);
              if (handler != null) {
                  return handler;
              }
          }
      }

      return null;
  }
```

### 매핑할 핸들러 없을 때 noHandlerFound()
설정에 따라 로깅하던지, 예외를 던지던지, 404 반환한다.
```java
  protected void noHandlerFound(HttpServletRequest request, HttpServletResponse response) throws Exception {
      if (pageNotFoundLogger.isWarnEnabled()) {
          pageNotFoundLogger.warn("No mapping for " + request.getMethod() + " " + getRequestUri(request));
      }

      if (this.throwExceptionIfNoHandlerFound) {
          throw new NoHandlerFoundException(request.getMethod(), getRequestUri(request), (new ServletServerHttpRequest(request)).getHeaders());
      } else {
          response.sendError(404);
      }
  }
```

### Handler 찾은 이후 다시 doDispatch로 돌아와서
이제 핸들러가 컨트롤러한테 요청 위임 해야 하는데, 위임 작업을 해줄 HandlerAdapter를 찾는다. <br>
그리고 Get이나 Head인 경우 Resource 변경을 확인해서, 변경되지 않았으면 얼리 리턴 해준다.

```java
  // 핸들러 어뎁터 찾기 - 
  // 찾는 과정은 또 handlerAdapters를 iterator로 단순 순회하므로 생략
  // 없으면 ServletException 던진다.
  HandlerAdapter ha = this.getHandlerAdapter(mappedHandler.getHandler());

  String method = request.getMethod();
  boolean isGet = HttpMethod.GET.matches(method);
  // method를 가져오는데, GET이나 HEAD일 때만 바뀌었는지 확인한다.
  // LastModified를 통해 확인했는데, 안 변했으면 그냥 얼리 리턴
  if (isGet || HttpMethod.HEAD.matches(method)) {
      long lastModified = ha.getLastModified(request, mappedHandler.getHandler());
      if ((new ServletWebRequest(request, response)).checkNotModified(lastModified) && isGet) {
          return;
      }
  }
```

### 최종 처리
```java
  // 인터셉터 처리
  if (!mappedHandler.applyPreHandle(processedRequest, response)) {
      return;
  }

  // 핸들러 어뎁터에게 handle()을 요청하고,
  // 모델엔 뷰를 가져온다 (mv)
  mv = ha.handle(processedRequest, response, mappedHandler.getHandler());
  if (asyncManager.isConcurrentHandlingStarted()) {
      return;
  }

  // 모델엔 뷰 적용
  this.applyDefaultViewName(processedRequest, mv);
  mappedHandler.applyPostHandle(processedRequest, response, mv);

  ...

  // 최종 render를 진행하는 processDispatchResult()!
  this.processDispatchResult(processedRequest, response, mappedHandler, mv, (Exception)dispatchException);
```

### processDispathResult()
```java
  private void processDispatchResult(HttpServletRequest request, HttpServletResponse response, @Nullable HandlerExecutionChain mappedHandler, @Nullable ModelAndView mv, @Nullable Exception exception) throws Exception {

      ...생략

      // [핵심]
      // 모델엔 뷰가 비어있지 않고, not cleared라면
      // 드디어 랜더링
      if (mv != null && !mv.wasCleared()) {
          // 랜더링
          this.render(mv, request, response);
          if (errorView) {
              WebUtils.clearErrorRequestAttributes(request);
          }
      } else if (this.logger.isTraceEnabled()) {
          this.logger.trace("No view rendering, null ModelAndView returned.");
      }

      ...생략

  }

```

### 랜더링
```java
  protected void render(ModelAndView mv, HttpServletRequest request, HttpServletResponse response) throws Exception {

      // 뷰 리졸버 통해서 View에 대한 정보를 가져온다.
      Locale locale = this.localeResolver != null ? this.localeResolver.resolveLocale(request) : request.getLocale();
      response.setLocale(locale);
      String viewName = mv.getViewName();
      View view;
      if (viewName != null) {
          view = this.resolveViewName(viewName, mv.getModelInternal(), locale, request);
          if (view == null) {
              throw new ServletException("Could not resolve view with name '" + mv.getViewName() + "' in servlet with name '" + this.getServletName() + "'");
          }
      } else {
          view = mv.getView();
          if (view == null) {
              throw new ServletException("ModelAndView [" + mv + "] neither contains a view name nor a View object in servlet with name '" + this.getServletName() + "'");
          }
      }

      ... 생략

        // 상태 설정ㄴ
        if (mv.getStatus() != null) {
            request.setAttribute(View.RESPONSE_STATUS_ATTRIBUTE, mv.getStatus());
            response.setStatus(mv.getStatus().value());
        }

        // 최종 랜더링
        view.render(mv.getModelInternal(), request, response);
      
      ... 생략
  }
```


```java
  protected void doDispatch(HttpServletRequest request, HttpServletResponse response) throws Exception {
      HttpServletRequest processedRequest = request;
      HandlerExecutionChain mappedHandler = null;
      boolean multipartRequestParsed = false;
      WebAsyncManager asyncManager = WebAsyncUtils.getAsyncManager(request);

      try {
          try {
              ModelAndView mv = null;
              Exception dispatchException = null;

              try {
                  processedRequest = this.checkMultipart(request);
                  multipartRequestParsed = processedRequest != request;
                  mappedHandler = this.getHandler(processedRequest);
                  if (mappedHandler == null) {
                      this.noHandlerFound(processedRequest, response);
                      return;
                  }

                  HandlerAdapter ha = this.getHandlerAdapter(mappedHandler.getHandler());
                  String method = request.getMethod();
                  boolean isGet = HttpMethod.GET.matches(method);
                  if (isGet || HttpMethod.HEAD.matches(method)) {
                      long lastModified = ha.getLastModified(request, mappedHandler.getHandler());
                      if ((new ServletWebRequest(request, response)).checkNotModified(lastModified) && isGet) {
                          return;
                      }
                  }

                  if (!mappedHandler.applyPreHandle(processedRequest, response)) {
                      return;
                  }

                  mv = ha.handle(processedRequest, response, mappedHandler.getHandler());
                  if (asyncManager.isConcurrentHandlingStarted()) {
                      return;
                  }

                  this.applyDefaultViewName(processedRequest, mv);
                  mappedHandler.applyPostHandle(processedRequest, response, mv);
              } catch (Exception var20) {
                  dispatchException = var20;
              } catch (Throwable var21) {
                  dispatchException = new NestedServletException("Handler dispatch failed", var21);
              }

              this.processDispatchResult(processedRequest, response, mappedHandler, mv, (Exception)dispatchException);
          } catch (Exception var22) {
              this.triggerAfterCompletion(processedRequest, response, mappedHandler, var22);
          } catch (Throwable var23) {
              this.triggerAfterCompletion(processedRequest, response, mappedHandler, new NestedServletException("Handler processing failed", var23));
          }

      } finally {
          if (asyncManager.isConcurrentHandlingStarted()) {
              if (mappedHandler != null) {
                  mappedHandler.applyAfterConcurrentHandlingStarted(processedRequest, response);
              }
          } else if (multipartRequestParsed) {
              this.cleanupMultipart(processedRequest);
          }

      }
  }
```


## 2. 스프링 부트가 자동 등록하는 HandlerMapping, HandlerAdapter 구현체

위에서 부터 사용하는 우선순위가 높다. (얘네가 전부인건 아님) <br>
위에서 부터 필터처럼 적용된다.


1. HandlerMapping : 컨트롤러를 찾는다.
   - `RequestMappingHanderMapping` : Annotation 기반 컨트롤러인 `@RequestMapping`에서 사용한다.
   - `BeanNameUrlHandlerMapping` : 스프링 빈 이름으로 핸들러를 찾는다. (요청 Url과 똑같은 이름을 가진 빈을 찾는다.)
2. HandlerAdapter : HandlerMapping을 통해 컨트롤러를 실행한다.
   - `RequestMappingHandlerAdapter` : Annotation 기반 `RequestMapping`에서 사용
   - `HttpRequestHanderAdapter` : HttpRequestHander 처리
   - `SimpleControllerHandlerAdapter` : Controller 인터페이스를 처리한다. `@Controller`와는 다른 것이므로 헷갈리면 안 됨


<br> 




## 3. MappingJackson2JsonView (ViewResolver)


1. ViewResolver들이 순차적으로 호출된다.
2. View 정보 반환
3. 반환된 View 정보는 `forward()`를 호출해 처리할 수 있는 경우에 사용
4. `view.render()`가 호출된다.

<br> <br>


스프링 부트는 다양한 View를 자동으로 등록한다. 스프링 부트 프로젝트를 할 때, 보통은 화면 대신 Json으로 된 API를 제공해주는데, 이 또한 View의 일종으로 `MappingJackson2JsonView`를 사용하면 된다. 스프링 3.X에서 기본으로 사용한다. <br>

Jackson Library는 Java Object를 JSON으로 변화시키거나, JSON을 Java Object로 변화시킬 때 사용하는 라이브러리이다.

### Render Code
Render를 하는 부분. `MappingJackson2JsonView`의 상위 클래스인 `AbstractJackson2View`가 가지고 있다. <br>

```java
	@Override
	protected void renderMergedOutputModel(Map<String, Object> model, HttpServletRequest request,
			HttpServletResponse response) throws Exception {

		ByteArrayOutputStream temporaryStream = null;
		OutputStream stream;

		if (this.updateContentLength) {
			temporaryStream = createTemporaryOutputStream();
			stream = temporaryStream;
		}
		else {
			stream = response.getOutputStream();
		}

		Object value = filterAndWrapModel(model, request);

    // 여기가 넣어주는 곳
		writeContent(stream, value);

		if (temporaryStream != null) {
			writeToResponse(response, temporaryStream);
		}
	}
```

### writeContent

```java
	/**
	 * Write the actual JSON content to the stream.
	 * @param stream the output stream to use
	 * @param object the value to be rendered, as returned from {@link #filterModel}
	 * @throws IOException if writing failed
	 */
	protected void writeContent(OutputStream stream, Object object) throws IOException {
		try (JsonGenerator generator = this.objectMapper.getFactory().createGenerator(stream, this.encoding)) {
			writePrefix(generator, object);

			Object value = object;
			Class<?> serializationView = null;
			FilterProvider filters = null;

			if (value instanceof MappingJacksonValue) {
				MappingJacksonValue container = (MappingJacksonValue) value;
				value = container.getValue();
				serializationView = container.getSerializationView();
				filters = container.getFilters();
			}

			ObjectWriter objectWriter = (serializationView != null ?
					this.objectMapper.writerWithView(serializationView) : this.objectMapper.writer());
			if (filters != null) {
				objectWriter = objectWriter.with(filters);
			}

      // Output Stream을 가진 Generator와 Write할 Value를 Writer에 넣어준다.
			objectWriter.writeValue(generator, value);

			writeSuffix(generator, object);
			generator.flush();
		}
	}
```


### WriteToResponse
WriteToResponse에서 값을 Response에 적어준다.

```java
	/**
	 * Write the given temporary OutputStream to the HTTP response.
	 * @param response current HTTP response
	 * @param baos the temporary OutputStream to write
	 * @throws IOException if writing/flushing failed
	 */
	protected void writeToResponse(HttpServletResponse response, ByteArrayOutputStream baos) throws IOException {
		// Write content type and also length (determined via byte array).
		response.setContentType(getContentType());
		response.setContentLength(baos.size());

		// Flush byte array to servlet output stream.
		ServletOutputStream out = response.getOutputStream();
		baos.writeTo(out);
		out.flush();
	}
```
