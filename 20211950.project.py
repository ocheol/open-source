# requests: HTTP 요청을 보내기 위한 라이브러리로, 서버에서 데이터를 가져오거나 보내는 데 사용합니다.
import requests

# datetime이란 현재 날짜와 시간을 가져오거나 조작하는 데 사용되는 표준 라이브러리입니다.
from datetime import datetime

# xmltodict이란 XML 형식의 데이터를 Python 딕셔너리(사전)로 변환하는 데 사용하는 라이브러리입니다.
import xmltodict

# 현재 날짜를 'yyyymmdd' 형식으로 반환하는 함수입니다. 현재 날짜를 가져와서 yyyymmdd 형식의 문자열로 반환합니다.
# API 요청 시 기준 날짜를 전달하기 위해 사용됩니다. 예시로는 현재 날짜가 2024년 12월 14일이라면, 함수는 '20241214'을 반환합니다.
# 사용 이유로는 기상청 API는 날짜를 반드시 yyyymmdd 형식으로 요구하기 때문입니다.
def get_current_date():
    # 현재 시스템 날짜를 가져옵니다.
    current_date = datetime.now().date()  
    # '20241214' 같은 형식의 문자열로 변환합니다.
    return current_date.strftime("%Y%m%d")  

# 현재 시간을 'hhmm' 형식으로 반환하는 함수입니다.
# 기상청 API의 'base_time'은 30분 간격으로 요청해야 합니다.
# 예를 들어, 10:00, 10:30, 11:00 등 형식으로 요청해야 유효한 응답을 받을 수 있습니다.
# 현재 시간을 'hhmm' 형식으로 반환하되, 기상청 API가 요구하는 30분 단위로 조정
def get_valid_base_time():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    if minute < 40:
        # 40분 이전에는 이전 시간의 데이터를 요청
        base_time = f"{hour - 1:02d}30" if hour > 0 else "2330"
    else:
        # 40분 이후에는 현재 시간 데이터를 요청
        base_time = f"{hour:02d}30"
    return base_time
    
    # 시간과 분을 'hhmm' 형식으로 반환
    return adjusted_time.strftime("%H%M")

# 강수 형태를 나타내는 숫자 코드를 사람이 읽을 수 있는 텍스트로 변환하기 위한 딕셔너리입니다.
int_to_weather = {
    "0": "맑음",        # 강수 없음
    "1": "비",         # 비가 오는 상태
    "2": "비/눈",      # 비와 눈이 섞여서 내리는 상태
    "3": "눈",         # 눈이 오는 상태
    "5": "빗방울",      # 가볍게 빗방울이 떨어지는 상태
    "6": "빗방울눈날림", # 빗방울과 눈이 흩날리는 상태
    "7": "눈날림"       # 눈이 흩날리는 상태
}


# 초단기 실황 데이터를 요청하고 결과를 처리하는 함수입니다.

#   기상청 초단기 실황 데이터를 가져오는 함수입니다.
#   입력된 API 파라미터를 이용해 서버에서 데이터를 요청한 후, 결과를 처리하여 온도와 날씨 상태를 반환합니다.
#   매개변수 params는 dict로 API 호출에 필요한 요청 파라미터를 포함하는 딕셔너리
#   반환값은 tuple(현재 온도, 날씨 상태) 예를 들어 ('15', '맑음')과 같은 형식으로 반환됩니다.
#   처리 과정
#   1. 기상청 API URL로 HTTP GET 요청을 보냅니다.
#   2. XML 형식의 응답 데이터를 가져옵니다.
#   3. XML 데이터를 Python 딕셔너리로 변환합니다.
#   4. 필요한 데이터('T1H'와 'PTY')를 추출합니다.
#   5. 'PTY' 코드를 텍스트로 변환하여 결과를 반환합니다.
def forecast(params):
    # 기상청 초단기 실황 API의 URL(공식 문서에서 제공된 API URL) 입니다.
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'

    # requests 라이브러리를 사용하여 HTTP GET 요청을 보냅니다.
    # params는 API 호출에 필요한 모든 파라미터를 포함합니다.
    res = requests.get(url, params)

    # API 호출이 성공했는지 확인하기 위해 상태 코드를 점검합니다.
    # 성공적인 요청은 상태 코드 200을 반환합니다.
    if res.status_code != 200:
        # 상태 코드가 200이 아니면 오류 메시지를 출력합니다.
        print(f"API 호출 실패. HTTP 상태 코드: {res.status_code}")
        print(f"응답 내용: {res.text}")
        # 오류가 발생한 경우 None 값을 반환하여 이후의 코드 실행을 방지합니다.
        return None, None

    # API 서버로부터 받은 응답 데이터를 XML 형식의 텍스트로 저장합니다.
    xml_data = res.text
    
    # XML 데이터를 Python 딕셔너리로 변환합니다.
    # xmltodict를 사용하면 XML 노드가 딕셔너리의 키-값 형태로 변환되어 편리하게 데이터 접근 가능합니다.
    dict_data = xmltodict.parse(xml_data)

    # API 응답에 'response'와 'body' 키가 있는지 확인합니다.
    # 이 두 키가 없으면 올바른 데이터가 반환되지 않았다는 의미입니다.
    if 'response' not in dict_data or 'body' not in dict_data['response']:
        # 필요한 키가 없을 경우, 에러 메시지를 출력하고 데이터를 출력하여 문제를 진단합니다.
        print("API 응답에 'response' 또는 'body'가 없습니다.")
        print(f"응답 데이터: {dict_data}")
        # 오류가 발생한 경우 None 값을 반환하여 이후의 코드 실행을 방지합니다.
        return None, None

    # 온도와 강수 상태를 저장할 변수를 초기화합니다.
    temp = None
    sky = None

    # try-except 블록을 사용하여 데이터 처리 중 발생할 수 있는 오류를 잡아냅니다.
    try:
        # 응답 데이터에서 'items' 항목의 'item' 리스트를 순회하며 필요한 데이터를 추출합니다.
        for item in dict_data['response']['body']['items']['item']:
            # 'category'가 'T1H'인 경우 현재 온도를 나타냅니다.
            if item['category'] == 'T1H':
                # 온도 값을 추출하여 temp 변수에 저장합니다.
                temp = item['obsrValue']  
            # 'category'가 'PTY'인 경우 강수 형태를 나타냅니다.
            if item['category'] == 'PTY':
                # 강수 형태 값을 추출하여 sky 변수에 저장합니다.
                sky = item['obsrValue']  

        # 강수 형태 코드(sky)를 사람이 읽을 수 있는 텍스트로 변환합니다.
        # int_to_weather 딕셔너리를 사용하여 숫자 코드를 의미 있는 문자열로 매핑합니다.
        sky = int_to_weather[sky]
        
        # 최종적으로 온도와 날씨 상태를 튜플 형태로 반환합니다.
        return temp, sky

    except KeyError as e:
        # 데이터 처리 중 KeyError가 발생하면 오류 메시지와 함께 디버깅을 위한 응답 데이터를 출력합니다.
        print(f"데이터 처리 중 오류 발생: {e}")
        print(f"응답 데이터: {dict_data}")
        # 오류가 발생한 경우 None 값을 반환하여 이후의 코드 실행을 방지합니다.
        return None, None


# 위도와 경도를 사용자로부터 직접 입력받기 위해 print와 input을 활용합니다.
# 사용자가 특정 위치의 날씨 데이터를 쉽게 조회할 수 있도록 하기 위해 변경하였습니다.
print("날씨를 조회할 지역의 위도와 경도를 입력하세요.")  
# 위도를 입력받아 latitude 변수에 저장
latitude = input("위도: ")  
# 경도를 입력받아 longitude 변수에 저장
longitude = input("경도: ")  
# 기존 코드에서는 위도와 경도를 미리 설정해두었지만, 이 방식은 특정 위치(예: 서울)만 조회가 가능하다는 한계가 있습니다.
# 따라서 사용자가 원하는 지역의 날씨를 동적으로 조회할 수 있도록 위도와 경도를 입력받는 방식으로 변경하였습니다.
# 위도와 경도를 `input()`으로 입력받아 사용자가 다양한 지역을 직접 조회할 수 있게 확장성을 높였습니다.


# 기상청 API 호출 시 필요한 인증 키 (기상청에서 발급) 입니다.
keys = '%2FLqgJiy2ddbDwCCO5BbKA1Rq%2FYUounM0%2B%2FTw2%2F94WPbRQGjxODuySL46A8V10U%2F2XHIjlVFdefSCvysQ8WON7w%3D%3D'

# API 호출에 필요한 모든 요청 파라미터를 딕셔너리 형태로 구성합니다.
params = {
    # 기상청에서 발급받은 API 인증 키입니다.
    'serviceKey': keys,          
    # 조회할 페이지 번호, 기본적으로 첫 페이지를 요청합니다.
    'pageNo': '1',               
    # 조회할 데이터의 개수입니다. 
    'numOfRows': '10',            
    # 응답 데이터의 형식(XML 또는 JSON 중 선택) 입니다.
    'dataType': 'XML',            
    # 기준 날짜 (yyyymmdd 형식)입니다.
    'base_date': get_current_date(),  
    # 기준 시간 (hhmm 형식, 30분 단위로 제공됨) 입니다.
    'base_time': get_valid_base_time(),  
    # 조회할 지역의 격자 X 좌표 (위도) 입니다.
    'nx': latitude,                   
    # 조회할 지역의 격자 Y 좌표 (경도) 입니다.
    'ny': longitude                   
}

# 위에서 정의한 forecast 함수를 호출하여 온도와 날씨 데이터를 가져옵니다.
# API 응답으로부터 데이터를 받아 처리합니다.
forecast_data = forecast(params)  

# 현재 날짜와 시간을 보기 좋게 포맷팅하여 출력하였습니다.
# 날짜와 시간을 사람이 읽기 쉬운 형식으로 출력하기 위해 `strftime`을 사용하였습니다.
# 이 형식은 사용자가 날씨 데이터가 어느 시점의 데이터인지 명확히 이해할 수 있도록 도와줍니다.
current_date = datetime.now().strftime("%Y 년 %m 월 %d 일")
current_hour = datetime.now().strftime("%H%M 시")

# 출력 형식 변경하였습니다.
print(f"{current_date} {current_hour}의 날씨 데이터입니다:")
print(f"기온은 {forecast_data[0]}도 입니다.")

# 강수 상태에 따른 메시지를 if-elif-else 문으로 출력하였습니다.
# 강수 형태에 따라 날씨 메시지를 세분화하여 출력하였습니다.
# 사용자 경험을 개선하기 위해 날씨 조건에 따른 조언을 추가하였습니다.
# 예시로는 비가 올 경우 "우산을 챙기세요!", 눈이 올 경우 "따뜻하게 입으세요!" 등 입니다.

if forecast_data[1] == "비":
    print("비가 와요. 우산을 챙겨주세요!")
elif forecast_data[1] == "비/눈":
    print("비 또는 눈이 와요. 따뜻하게 입고 우산을 챙기세요!")
elif forecast_data[1] == "눈":
    print("눈이 와요. 장갑을 꼭 챙기세요!")
elif forecast_data[1] == "빗방울":
    print("빗방울이 떨어져요. 우산을 챙겨주세요!")
elif forecast_data[1] == "빗방울눈날림":
    print("빗방울과 눈이 흩날려요. 우산과 따뜻한 옷을 준비하세요!")
elif forecast_data[1] == "눈날림":
    print("눈이 흩날려요. 따뜻하게 입으세요!")
else:
    print("날씨가 좋네요!")


