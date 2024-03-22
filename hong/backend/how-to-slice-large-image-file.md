## 배경

큰 이미지를 분석할 때 작은 크기의 이미지(예: 100x100 사이즈)로 잘라서 부분부분 분석한 다음 결과를 모두 종합하여 최종 결과를 만들어 내는 방식을 백엔드에서 지원해야 한다면 어떻게 할 수 있을까 조사했습니다.

## 문제 분석

### 1. 파일 크기 문제

파일 크기가 일정 사이즈를 초과한다면 일반적으로 잘 알려진 open-source 라이브러리로 처리할 때 최대 사이즈를 초과하는 이미지라는 Exception을 던진다.

예:

- **ImageIO (Java)**

  - ImageIO 라이브러리에서 허용하는 최대 이미지 사이즈는 **2,147,483,647 pixels** 이다. (2GB)
 
![스크린샷 2024-03-17 183337](https://github.com/10000-Bagger/free-topic-study/assets/34956359/d044f4a4-ddac-490e-8ccb-2a4fe1cfb78b)


- **Pillow (Python)**

  - Pillow 라이브러리에서 허용하는 최대 이미지 사이즈는 **178,956,970 pixels** 이다.

![스크린샷 2024-03-17 182407](https://github.com/10000-Bagger/free-topic-study/assets/34956359/5e4631d6-6500-429a-88e3-d6da1c5688a8)


- **OpenCV (Python)**
  - OpenVC 라이브러리에서 허용하는 최대 이미지 사이즈는 **1,073,741,824 pixels** 이다.
 
![스크린샷 2024-03-17 182436](https://github.com/10000-Bagger/free-topic-study/assets/34956359/4d27f703-bbb1-40df-b3e2-68bab647a8c0)


## 문제 해결

큰 파일을 읽어내고 작은 파일로 잘라내거나 바로 접근이 가능하도록 지원하는 라이브러리를 찾아본 결과, **OpenSlide** 라이브러리를 사용하면 큰 이미지 파일을 효율적으로 처리할 수 있다는 것을 알게 되었다.

### OpenSlide

> OpenSlide is a C library that provides a simple interface to read whole-slide images (also known as virtual slides)

OpenSlide은 원래 Whole-slide image (WSI) 라는 유리 슬라이드를 스캔하여 디지털 슬라이드로 만든 파일 형식을 지원하기 위해 개발된 Open source 라이브러리이다. 하지만, 해당 라이브러리를 활용해서 JPEG, JPEG 2000, PNG 등 다양한 이미지 파일을 응용 프로그램으로 컨트롤할 수 있는 기능을 지원한다.

공식 지원하는 언어는 Java와 Python이며, Python이 Java보다 기능 측면에서 더 많은 기능을 지원한다.

예를 들어, Python library는 원본 이미지에서 특정 부분을 뽑아 낼 수 있는 기능인 Deep Zoom generator 기능이 포함되어 있다. 하지만, Java library에는 해당 기능이 빠져 있어 원본 이미지의 파일을 부분으로 잘라서 사용하기 위해서는 Python library를 사용해야 한다.

### OpenSlide 사용 방법
