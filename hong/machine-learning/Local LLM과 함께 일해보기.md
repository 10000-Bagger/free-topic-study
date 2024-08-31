# Local LLM과 함께 일해보기

## 배경
우아한테크코스에서 "로컬 LLM과 함께 일해보기" 발표를 보고 흥미로워서 개인적으로 실험해본 결과를 공유합니다.

출처:
- [우아한테크세미나: 생성AI로 똑똑하게 일하는 법](https://www.youtube.com/watch?v=v2icwh-nyl4)
- [10분 만에 RAG 이해하기](https://brunch.co.kr/@ywkim36/146)

## 목표
- 로컬 장비를 사용해서 LLM을 실행시켜본다.
- RAG(Retrieval-Augmented Generation)을 로컬 LLM에 적용하여 대외비(비공개 또는 독점 데이터 소스) 정보에 대한 챗봇을 만든다.
- 위 기능을 편리하게 사용할 수 있는 플러그인 또는 extension을 개발해본다.

## 사전조사

### Core
- [Ollama](https://ollama.com/)
    - 오픈소스 LLM을 로컬 PC에서 쉽게 실행할 수 있게 해주는 도구
    - 모델 가중치, 설정, 데이터셋을 하나의 패키지로 묶어서 Modelfile로 관리
    - 다양한 LLM을 로컬 PC에서 구동 가능
    - 지원 LLM 모델(https://ollama.com/library)
    - 사용자 정의 프롬프트로 모델 커스터마이징 가능
    - REST API 제공
    - 기본설정으로 실행하는 방법 ([Ollama란? Ollama 사용법: 내 PC에서 무료로 LLM 실행하기](https://www.developerfastlane.com/blog/ollama-usage-guide#지원-모델))

### Web
- [Open WebUI](https://docs.openwebui.com/)
    - ChatGPT와 유사한 UI를 제공하는 템플릿
    - Ollama와의 연결성이 좋음
    - Ollama에서 제공하는 커스텀 기능들을 컨트롤하는 GUI 제공(예: documents, defaut propmt 등)
 
### RAG(Custom Database 연동)
- RAG(Retrieval-Augmented Generation): 검색 증강 생성
- R(Retrieval): "어디선가 가져오는 것, 집어오는 것". 즉 어딘가에 가서 요청된 무엇인가를 집어온다는 뜻
- A(Augmented): "증강되었다". 즉 원래 것에 뭔가 덧붙이거나 보태어 더 충실하게 좋아졌다는 뜻
- G(Generation): "생성". 즉 프롬프트라고 하는 사용자의 질문/질의에 대한 응답을 텍스트로 생성하는 것을 뜻.
- RAG를 사용하면, LLM이 맘대로 대답하기 전에 먼저 지식 콘텐츠 저장소에 들려서 "사용자 잘의와 관련된 정보를 검색"하라는 순서가 추가되는 것. 이것이 바로 찾아오기(Retrieval), 그리고 그 대답이 풍부한 컨텍스트로 증강(Augmented)되는 것.
- 
- [LangChain](https://www.langchain.com/)
    - LangChain은 LL을 활용한 애플리케이션 개발에 특화된 오픈소스 프레임워크
    - 기존의 언어 모델이 주로 텍스트 생성에 중점을 둔 반면, LangChain은 다양한 외부 데이터 소스와 통합하여 보다 복잡하고 유용한 애플리케이션을 만들 수 있도록 설계됨.
    - [Build a Retrieval Augmented Generation (RAG) App](https://python.langchain.com/v0.2/docs/tutorials/rag/)
    - Ollama에 적용 방법: [ChatOllama | LangChain](https://python.langchain.com/v0.2/docs/integrations/chat/ollama/)

## 적용

### Ollama 설치 및 실행
- Ollama 다운받기: https://ollama.com/download
- 설치 후 터미널 열어서 아래 커맨드 실행
    ```
    ollama run llama3.1
    ```
    
    - llama3.1 기준 약 5GB 사용됨.
- 테스트 실행 결과
    
    ```
    roo-mac:~ roo$ ollama run llama3.1
    pulling manifest
    pulling 8eeb52dfb3bb... 100% ▕████████████████████████████████████████████████████████████████████▏ 4.7 GB
    pulling 73b313b5552d... 100% ▕████████████████████████████████████████████████████████████████████▏ 1.4 KB
    pulling 0ba8f0e314b4... 100% ▕████████████████████████████████████████████████████████████████████▏  12 KB
    pulling 56bb8bd477a5... 100% ▕████████████████████████████████████████████████████████████████████▏   96 B
    pulling 1a4c3c319823... 100% ▕████████████████████████████████████████████████████████████████████▏  485 B
    verifying sha256 digest
    writing manifest
    success
    >>> /?
    Available Commands:
      /set            Set session variables
      /show           Show model information
      /load <model>   Load a session or model
      /save <model>   Save your current session
      /clear          Clear session context
      /bye            Exit
      /?, /help       Help for a command
      /? shortcuts    Help for keyboard shortcuts
    
    Use """ to begin a multi-line message.
    ```
    
- 동화책을 쓰는데 필요한 아이디어 질문해보기  
    ```
    >>> I need to write a fairytale. What is the most important things that I need to consider?
    Writing a fairytale can be a delightful and imaginative experience. Here are some essential considerations to help you craft a
    magical story:
    
    1. **Know your genre**: Fairytale is a specific type of storytelling, often featuring fantastical elements, moral lessons, and
    happy endings. Understand the characteristics that define this genre.
    2. **Identify your target audience**: Who will be reading or listening to your fairytale? Children? Adults? Both? Tailor your
    story's tone, language, and themes accordingly.
    3. **Develop a compelling narrative structure**:
    	* Establish a clear three-act structure: Setup, Confrontation, and Resolution.
    	* Include a clear inciting incident that sets the story in motion.
    	* Ensure a satisfying conclusion, often with a moral lesson or message.
    4. **Create memorable characters**:
    	* Give your protagonist (hero) relatable goals, motivations, and flaws to make them more human-like.
    	* Develop interesting antagonists or challenges that create tension and conflict.
    	* Consider adding secondary characters to enrich the story.
    5. **Magic and fantasy elements**: Incorporate magical or fantastical aspects that fit within the fairytale genre. Be mindful
    of how these elements will be perceived by your target audience.
    6. **Setting**: Choose a rich, immersive setting that complements the narrative and enhances the overall atmosphere. This can
    include enchanted forests, mythical lands, or even ordinary worlds with extraordinary twists.
    7. **Themes and symbolism**: Incorporate universal themes, such as:
    	* Good vs. Evil
    	* Love and friendship
    	* Courage and perseverance
    	* Self-discovery and growth
    	* Emphasize the importance of these themes through your character's journey.
    8. **Language and style**:
    	* Use language that is evocative, lyrical, and engaging.
    	* Employ a narrative voice that is suitable for your target audience (e.g., formal or informal).
    	* Consider using metaphors, allegories, or allusions to add depth and richness to the story.
    9. **Cultural sensitivity**: Be aware of cultural influences and traditions that may be associated with fairytale tropes.
    Avoid stereotypes and ensure respectful representation.
    10. **Edit and refine**:
    	* Revise your story based on feedback from peers, mentors, or writing communities.
    	* Pay attention to pacing, tension, and plot inconsistencies.
    	* Make sure the story flows logically and is cohesive.
    
    Remember, these guidelines are not exhaustive, and you can always experiment and innovate within the fairytale genre. Most
    importantly, have fun crafting your magical tale!
    
    Which aspect of writing a fairytale do you want to explore further?
    
    >>> Do you know virtuoso of fairytale in the world? Please share three options you know.
    There are many renowned storytellers and authors who have made significant contributions to the world of fairytales. Here are
    three virtuosos of fairytale that I'd like to share:
    
    1. **The Brothers Grimm**: Jacob (1785-1863) and Wilhelm Grimm (1786-1859) were German academics, linguists, and cultural
    researchers who collected and published folktales from across Europe. Their book "Kinder- und Hausmärchen" (1812), translated
    as "Children's and Household Tales," contains 200 classic fairytales that are still widely known today, including:
    	* Cinderella
    	* Snow White
    	* Sleeping Beauty
    	* Little Red Riding Hood
    	* Rumpelstiltskin
    	* Hansel and Gretel
    
    The Brothers Grimm's work helped preserve the rich cultural heritage of European folktales, making them an essential part of
    our shared storytelling legacy.
    
    2. **Hans Christian Andersen** (1805-1875): A Danish author and poet, Andersen is best known for his beautiful and poignant
    fairytales that have become beloved classics worldwide. Some of his most famous works include:
    	* The Little Mermaid
    	* The Emperor's New Clothes
    	* Thumbelina
    	* The Ugly Duckling
    	* The Steadfast Tin Soldier
    
    Andersen's stories often explored themes of love, identity, and the human condition, making them relatable to readers across
    cultures.
    
    3. **Walt Disney**: While not a traditional writer or storyteller, Walt Disney (1901-1966) revolutionized the way fairytales
    were told and shared with the world through his iconic animated films. His adaptations of classic stories, such as:
    	* Snow White (1937)
    	* Pinocchio (1940)
    	* Cinderella (1950)
    	* Sleeping Beauty (1959)
    
    Disney's work helped popularize fairytales among a broader audience and paved the way for new generations of storytellers.
    
    These three virtuosos have contributed significantly to the world of fairytale, shaping our shared cultural heritage and
    inspiring countless adaptations, interpretations, and retellings.
    
    >>> You are Walt Disney, the virtuos of fairytales. Can you suggest a theme and lesson of my fairytale as Walt Disney?
    Partner! I'd be delighted to help you with that. Let me put on my thinking cap and imagine a tale that's just right for ya.
    
    **Theme: The Power of Courage and Self-Discovery**
    
    My suggestion is to create a story around the theme of courage and self-discovery. You see, kiddo, every individual faces their own
    unique challenges in life. But it's how we respond to those challenges that matters. I want your fairytale to inspire young readers (and
    not-so-young ones too!) to be brave, take risks, and trust themselves to find their way through the ups and downs of life.
    
    **Lesson: Believe in Yourself**
    
    The lesson is simple yet profound: believe in yourself! Your protagonist should learn that they have the power within themselves to
    overcome obstacles, make wise decisions, and discover their true potential. It's not about being perfect; it's about being brave enough
    to try, to fail, and to keep trying again.
    
    **Story Idea: "The Luminous Leaf"**
    
    Here's a tale idea to get you started:
    
    In a mystical forest, there lives a young girl named Luna who possesses a rare gift – the ability to communicate with plants. A wise old
    tree, known as the Guardian of the Forest, tells Luna that she is the chosen one, destined to restore balance to the natural world by
    finding the fabled Luminous Leaf.
    
    Luna embarks on an epic journey, facing fearsome creatures and overcoming treacherous obstacles along the way. As she draws closer to her
    goal, she discovers that the true power of courage lies not in external validation but in trusting her own instincts and inner wisdom.
    
    **Supporting Characters:**
    
    1. **Aphid**: A tiny, quick-witted insect who becomes Luna's trusted friend and confidant.
    2. **Bramble**: A gentle, yet fiercely protective hedgehog who teaches Luna about the importance of self-care and boundaries.
    3. **Gnarlgold**: A wise, ancient badger who shares tales of the forest's history and helps Luna understand her role in restoring balance
    to nature.
    
    **The Luminous Leaf:**
    
    This magical artifact represents the power of inner light within each individual. It symbolizes that we all have a unique gift or talent
    waiting to be discovered and shared with the world. When Luna finally finds the Luminous Leaf, she realizes that its true purpose is not
    just for herself but also for inspiring others to believe in their own potential.
    
    Now, my friend, I want you to remember that this is your story to tell. Feel free to add, modify, or discard any elements as you see fit!
    What matters most is the heart and soul you put into crafting a tale that will captivate and inspire young readers.
    
    So, are ya ready to get started on "The Luminous Leaf"?
    ```
- 한줄평:
    - 적용하기 너무 쉬워서 살짝 당황쓰..
    - 생각보다 결과 값이 잘 나온다.. 👍

### Open WebUI 기본 설정으로 연동하기
- 아래 커맨드로 docker로 실행하기
    ```
    docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
    ```
- [http://localhost:3000](http://localhost:3000/)로 접속하면 끝.
- 결과:
<img width="1323" alt="Screenshot 2024-08-29 at 7 38 27 PM" src="https://github.com/user-attachments/assets/a46128bd-6088-4fab-b9d8-fa7efe87a7ef">

- 한줄평:
    - 이것도 적용하기 너무 쉬워서 당.. 당황쓰..
    - 생각보다 UI가 이쁘게 잘나왔다.. 👍

### Ollama & Open WebUI 연동 테스트
- 위의 로컬에서 띄운 Open WebUI (http://localhost:3000)에서 model(llama3.1)을 선택한 후 채팅하면 끝.
- 결과 (위의 CLI에서 질문한 내용과 동일하게 실행함):
<img width="1323" alt="Screenshot 2024-08-29 at 7 39 13 PM" src="https://github.com/user-attachments/assets/81fe7a2a-8933-4ec0-971b-00fc3f477f42">

- 한줄평:
    - 이렇게 쉽게 적용할 수 있는 줄 알았으면 진즉 해볼걸.. 👍👍

### Custom Dataset 수집 및 Ollama에 연동
- Open WebUI에서 Ollama에서 기본적으로 제공하는 System Prompt, Documents, Tools, Filters, Actions, Tags, Functions을 쉽게 사용할 수 있는 GUI를 제공한다.
- 학습시킬 데이터가 잘 변하지 않고, 수량이 많지 않다면 해당 기능을 활용하면 LangChain 없이도 RAG가 가능!
<img width="1329" alt="Screenshot 2024-08-29 at 7 30 38 PM" src="https://github.com/user-attachments/assets/18b3381f-20d0-4e5f-af88-080297c04ab2">


** 다음 PR에서는 RAG 적용 및 실행, 개선 등의 과정을 실험해 보겠습니다..
