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

Python에서 OpenSlide와 DeepZoomGenerator를 통해 부분 이미지를 추출한 파일(Patch)을 생성하는 방법은 아래와 같다.

```python
import openslide
from openslide import OpenSlide
from openslide.deepzoom import DeepZoomGenerator
from io import BytesIO

DEEPZOOM_FORMAT = 'jpeg'

# Given a slide path
openslide_obj = OpenSlide(path)
slide = DeepZoomGenerator(openslide_obj, **self.dz_opts)
mpp_x = openslide_obj.properties[openslide.PROPERTY_NAME_MPP_X]
mpp_y = openslide_obj.properties[openslide.PROPERTY_NAME_MPP_Y]

slide.map = (float(mpp_x) + float(mpp_y)) / 2
dzi = slide.get_dzi(DEEPZOOM_FORMAT)

# Given level, col, row info
tile = slide.get_tile(level, col, row)
buf = BytesIO()
tile.save(buf, "jpeg", quality=DEEPZOOM_TILE_QUALITY)
return buf.getvalue(
```

각 라인에 대한 설명은 아래와 같다.

```python
openslide_obj = OpenSlide(path)
```

- OpenSlide를 사용하여 전체 슬라이드 이미지 열기. 'path'는 WSI 파일 실제 경로를 입력.

```python
slide = DeepZoomGenerator(openslide_obj, **self.dz_opts)
```

- 선언된 슬라이드로 DeepZoomGenerator를 초기화. self.dz_opts는 DeepZoomGenerator에 대한 옵션들이며, 예를 들어, 타일 크기 및 overlap 등이 포함되어야 함.

```python
mpp_x = openslide_obj.properties[openslide.PROPERTY_NAME_MPP_X]
mpp_y = openslide_obj.properties[openslide.PROPERTY_NAME_MPP_Y]
```

- 슬라이드 속성에서 X 및 Y 차원의 Microns Per Pixel(mpp)을 검색. 미크론 단위 픽셀은 픽셀 당 얼마의 micrometer 가 담기느냐를 나타내는 수치 ([링크](https://biology-statistics-programming.tistory.com/215))

```python
slide.map = (float(mpp_x) + float(mpp_y)) / 2
```

- 평균 미크론 단위 픽셀(mpp)을 매핑 요소로 계산

```python
dzi = slide.get_dzi(DEEPZOOM_FORMAT)
```

- 슬라이드에 대한 Deep Zoom Image (DZI) 형식 정보 가져오기. DZI 형식은 DeepZoom이 다양한 줌 레벨에서 이미지가 타일로 어떻게 나뉘어지는지 설명하는 데 사용.

```python
tile = slide.get_tile(level, col, row)
```

- 줌 레벨, 열, 행을 주어 특정 타일 검색

```python
tile.save(buf, "jpeg", quality=DEEPZOOM_TILE_QUALITY)
```

- 타일을 저장하기 위한 메모리 내 바이트 버퍼 준비

```python
tile.save(buf, "jpeg", quality=DEEPZOOM_TILE_QUALITY)
```

- 지정된 품질로 JPEG 형식으로 버퍼에 타일 저장

```python
return buf.getvalue()
```

- 버퍼의 내용, 즉 타일 이미지 데이터 반환

위와 같은 방식으로 WSI 파일에서 지정된 사이즈의 patch로 이미지를 뽑아올 수 있다.
