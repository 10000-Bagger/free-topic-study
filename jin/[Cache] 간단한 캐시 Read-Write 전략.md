# 캐시 Read-Write 전략
    
## 1. 읽기 전략
### 1. Look Aside Pattern
![Pasted image 20230925203350](https://github.com/10000-Bagger/free-topic-study/assets/71186266/60e95e71-ba80-42e5-b9e2-d91c11e31a75)
    
캐시를 우선 확인하고 없으면, DB를 조회하는 전략이다. <br>
`Look Aside`란 "옆을 보다"라는 의미가 있는데, DB를 확인하기 전에 옆 (캐시)을 먼저 확인하는 패턴이라고 해서 Look Aside Pattern이다. <br> <br>

장애시에도 DB에서 데이터를 가져오므로 문제 없이 운영 가능하다. <br>
But 캐시가 워낙 인기가 많아, connection이 잔뜩 쌓여있는 와중 갑자기 캐시가 만료된다거나 실패하게 되는 경우, DB로 요청이 한번에 몰릴 수도 있다. -> 이것이 그 유명한 [Thundering Herd 문제이다.](https://en.wikipedia.org/wiki/Thundering_herd_problem) <br>
반복적인 읽기가 많은 호출에 적합한 방법이다. 다만, 캐시만 확인하고, DB 데이터는 확인하지 않으므로, 쓰기 정책에 따라 일관성에 주의해야 한다.
	
### 2. Read Through Pattern
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/fe1a4ec9-3edb-477e-bd19-39830882f0a9)

	
캐시에서만 데이터를 읽는 전략이다. <br>
캐시를 "통해" 읽는 것과 같아 `Read Through Pattern`이다. <br>
캐시에서만 데이터를 읽는 만큼, 읽는 속도가 엄청 빠를 수 밖에 없다. <br>
하지만, **cache miss가 많은 경우** look aside 전략보다도 느릴 수가 있다. Miss가 발생할 때마다 DB에서 데이터를 조회해야 하고, 캐싱한 다음 그 값을 읽어야 하기 때문에, 절차가 복잡하다. <br> 
또한 캐시에서만 데이터를 읽기 때문에 장애에 매우 취약하다. 캐시 서버가 죽는 경우 데이터를 읽기 어려워지기 때문에, 서버의 HA가 요구된다. <br> 레디스의 경우 센티넬이나 클러스터링을 고려해야 할 것이다.
	  
# 2. 캐시 쓰기 전략
	  
## 2.1 Write Back Pattern
      
![Pasted image 20230925203654](https://github.com/10000-Bagger/free-topic-study/assets/71186266/084eb363-78e7-4ee3-af54-3655dca13801)

데이터를 DB에 바로 저장하지 않고 캐시에 모아두었다가 DB에 저장하는 방식이다. <br>
나중에 쓴다는 의미의 "Write Back"이다. 문제는 이 때도 캐시 스토어의 중요성이 너무나도 높아져 버린다. 만약 캐시 스토어가 죽는다면 데이터가 영구 손실될 수 있다. <br>
레디스의 경우 앞서 언급한 HA를 위한 기능 말고도, 여기서는 복제 기능이나, 서버에 직접 저장하는 기능이 유용할 수 있겠다.
      
## 2.2 Write Through Pattern
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/2f9ce133-b820-4eeb-8d8b-545a0ec0e37f)

데이터를 캐시를 "통해" DB에 저장하는 패턴이라 `Write Through Pattern`이다. 저장 시점이 DB에 "함께" 저장되는 것이나 마찬가지이기 때문에, 두 데이터는 대게 일치한다. <br> 
따라서 일관성 유지에도 좋고, 매번 DB에 잘 저장하기 때문에 데이터의 유실 가능성이 적다. <br>
하지만, Write 비용이 높아진다. 왜냐하면 매번 두 군데에 데이터를 저장하는 것이나 마찬가지이기 때문이다. 서비스에 생성이나 수정 쿼리가 빈번한 경우 성능 이슈가 발생할 수 있다.
		  
## 2.4 Write Around Pattern
![image](https://github.com/10000-Bagger/free-topic-study/assets/71186266/916ff1e3-43d6-48a6-a799-6dea52416aae)

그냥 모든 데이터를 DB에만 바로 저장하는 전략이다. 딱히 쓸 때 캐시를 갱신한다기 보다는 필요에 따라 갱신한다. <br>
캐시 Miss나 Prefetching 상황에서 캐싱이 될 것이다. 따라서 캐시와 DB의 데이터 불일치 가능성이 있다고 보는게 맞다. <br>
그래서 Cache의 Expire나 데이터 갱신, 캐시 무효화를 아주 잘 설정해야 할 것이다. <br>
덕분에 다른 Write 전략들 보다는 평상시 저장 시간이 덜 걸린다는게 장점이라면 장점일 수 있다.


# 3. 전략 조합



# Reference
- [Inpa Blog](https://inpa.tistory.com/entry/REDIS-%F0%9F%93%9A-%EC%BA%90%EC%8B%9CCache-%EC%84%A4%EA%B3%84-%EC%A0%84%EB%9E%B5-%EC%A7%80%EC%B9%A8-%EC%B4%9D%EC%A0%95%EB%A6%AC)
