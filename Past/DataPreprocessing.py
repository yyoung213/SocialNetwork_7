import pandas as pd
import re
from collections import Counter, defaultdict
from typing import List, Dict, Set
import openpyxl

def load_data(file_path: str) -> pd.DataFrame:
    """엑셀 파일에서 데이터 로드"""
    df = pd.read_excel(file_path)
    return df

def extract_text_from_dataframe(df: pd.DataFrame) -> List[str]:
    """데이터프레임에서 주요업무, 자격요건, 우대사항 텍스트 추출"""
    text_list = []
    columns = ['주요업무', '자격요건', '우대사항']
    
    for col in columns:
        if col in df.columns:
            for text in df[col].dropna():
                if isinstance(text, str) and text.strip():
                    text_list.append(text.strip())
    
    return text_list

def normalize_text(text: str) -> str:
    """텍스트 정규화"""
    # 공백 정리
    text = re.sub(r'\s+', ' ', text)
    # 특수문자 제거 (일부는 유지)
    text = re.sub(r'[^\w\s가-힣•·.,()/-]', '', text)
    return text.strip()

def extract_technical_terms_from_text(text: str) -> Set[str]:
    """텍스트에서 기술 용어 및 키워드 추출 (데이터 기반)"""
    keywords = set()
    text_normalized = normalize_text(text)
    
    # 불용어 확장 (의미 없는 단어 필터링)
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 
        'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 
        'did', 'let', 'put', 'say', 'she', 'too', 'use', 'with', 'from', 'this', 'that', 'have', 'been', 'will',
        'more', 'than', 'what', 'when', 'where', 'which', 'while', 'would', 'could', 'should', 'might', 'must'
    }
    
    # 1. 영문 기술 용어 추출 (대문자로 시작하는 단어, 또는 알려진 기술 스택)
    # 프로그래밍 언어, 프레임워크, 라이브러리 패턴
    tech_patterns = [
        r'\b[A-Z][a-z]{2,}(?:\.[a-z]+)?\b',  # Python, Node.js, React.js 등 (최소 3자)
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text_normalized)
        for match in matches:
            # 불용어 필터링 및 최소 길이 체크
            if len(match) >= 3 and match.lower() not in stop_words:
                # 일반적인 영어 단어가 아닌 기술 용어로 보이는 것만 추가
                if not match.lower() in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'let', 'put', 'say', 'she', 'too', 'use', 'with', 'from', 'this', 'that', 'have', 'been', 'will', 'more', 'than', 'what', 'when', 'where', 'which', 'while', 'would', 'could', 'should', 'might', 'must']:
                    keywords.add(match)
    
    # 2. 한글 기술 용어 추출 (명사 패턴) - 더 엄격한 필터링
    # 기술 관련 접미사가 붙은 2-4자 한글 조합만 추출
    korean_tech_suffixes = ['분석', '개발', '설계', '구축', '운영', '관리', '시스템', '플랫폼', '서비스', '기술', '도구', 
                           '프레임워크', '라이브러리', '언어', '프로그램', '소프트웨어', '하드웨어', '네트워크', 
                           '데이터베이스', '알고리즘', '모델', '인프라', '클라우드', '보안', '테스트', '디버깅', 
                           '최적화', '자동화', '모니터링', '로깅', '배포', '아키텍처', '마이크로서비스', '컨테이너', 
                           '오케스트레이션', '스케일링', '로드밸런싱', '캐싱', '큐잉', '메시징', '스트리밍']
    
    korean_tech_pattern = r'[가-힣]{2,4}(?:' + '|'.join(korean_tech_suffixes) + r')'
    matches = re.findall(korean_tech_pattern, text_normalized)
    for match in matches:
        if len(match) >= 3:  # 최소 3자 이상
            keywords.add(match)
    
    # 3. 기술 스택 조합 추출 (예: "Python 개발", "React Native", "Spring Boot") - 제한적
    # 알려진 기술 스택만 추출하도록 제한
    known_tech_stacks = ['React Native', 'Spring Boot', 'Node.js', 'Ruby on Rails', 'ASP.NET', 'Machine Learning', 
                        'Deep Learning', 'Data Analysis', 'Data Science', 'Big Data', 'Power BI', 'Natural Language']
    for tech_stack in known_tech_stacks:
        if tech_stack.lower() in text_normalized.lower():
            keywords.add(tech_stack)
    
    return keywords

def extract_keywords_from_text(text: str) -> Set[str]:
    """텍스트에서 키워드 추출 (기존 패턴 + 데이터 기반 추출)"""
    keywords = set()
    
    # 기존 패턴 기반 추출
    # 불용어 목록 확장
    stop_words = {
        '및', '또는', '등', '을', '를', '이', '가', '의', '에', '에서', '로', '으로', '와', '과',
        '분', '자', '경험', '보유', '능력', '가진', '있는', '수', '할', '있는', '할 수',
    }
    
    # 구체적인 기술 키워드 사전 (정확한 매칭을 위해) - 확장된 버전
    keyword_patterns = {
        # 프로그래밍 언어
        'Python': [r'\bPython\b', r'\b파이썬\b', r'\bPYTHON\b'],
        'SQL': [r'\bSQL\b', r'\bsql\b', r'\b에스큐엘\b'],
        'R': [r'\bR\b(?:\s+언어)?', r'\bR언어\b'],
        'Java': [r'\bJava\b', r'\b자바\b', r'\bJAVA\b'],
        'JavaScript': [r'\bJavaScript\b', r'\b자바스크립트\b', r'\bJS\b', r'\bJavascript\b'],
        'TypeScript': [r'\bTypeScript\b', r'\b타입스크립트\b', r'\bTS\b'],
        'C++': [r'\bC\+\+\b', r'\bCpp\b', r'\bcpp\b'],
        'C': [r'\bC\b(?:\s+언어)?', r'\bC언어\b'],
        'C#': [r'\bC#\b', r'\bCSharp\b', r'\bC샵\b'],
        'Go': [r'\bGo\b', r'\bGolang\b', r'\b고\b'],
        'Rust': [r'\bRust\b', r'\b러스트\b'],
        'Swift': [r'\bSwift\b', r'\b스위프트\b'],
        'Kotlin': [r'\bKotlin\b', r'\b코틀린\b'],
        'PHP': [r'\bPHP\b', r'\bphp\b'],
        'Ruby': [r'\bRuby\b', r'\b루비\b', r'\bRuby on Rails\b', r'\b루비온레일즈\b'],
        'Scala': [r'\bScala\b', r'\b스칼라\b'],
        'Perl': [r'\bPerl\b', r'\b펄\b'],
        'Objective-C': [r'\bObjective-C\b', r'\bObjectiveC\b'],
        'Dart': [r'\bDart\b', r'\b다트\b'],
        
        # 데이터 분석 도구
        'Tableau': [r'\bTableau\b', r'\b태블로\b', r'\bTABLEAU\b'],
        'Power BI': [r'\bPower\s+BI\b', r'\b파워비아이\b', r'\bPowerBI\b'],
        'Excel': [r'\bExcel\b', r'\b엑셀\b', r'\bEXCEL\b'],
        'QlikView': [r'\bQlikView\b', r'\b퀵뷰\b'],
        'SAS': [r'\bSAS\b', r'\b에스에이에스\b'],
        'SPSS': [r'\bSPSS\b', r'\b에스피에스에스\b'],
        'Looker': [r'\bLooker\b', r'\b루커\b'],
        'Metabase': [r'\bMetabase\b', r'\b메타베이스\b'],
        
        # 머신러닝/딥러닝
        'Machine Learning': [r'\bMachine\s+Learning\b', r'\b머신러닝\b', r'\bML\b', r'\b기계학습\b'],
        'Deep Learning': [r'\bDeep\s+Learning\b', r'\b딥러닝\b', r'\bDL\b'],
        'AI': [r'\bAI\b', r'\b인공지능\b', r'\bArtificial\s+Intelligence\b'],
        
        # 데이터 과학
        'Data Analysis': [r'\bData\s+Analysis\b', r'\b데이터\s+분석\b', r'\b데이터분석\b', r'\bData\s+Analytics\b'],
        'Data Science': [r'\bData\s+Science\b', r'\b데이터\s+사이언스\b', r'\b데이터사이언스\b'],
        'Statistics': [r'\bStatistics\b', r'\b통계\b', r'\b통계학\b', r'\bStatistical\s+Analysis\b'],
        
        # 빅데이터 기술
        'Big Data': [r'\bBig\s+Data\b', r'\b빅데이터\b', r'\b빅\s+데이터\b'],
        'Hadoop': [r'\bHadoop\b', r'\b하둡\b', r'\bHADOOP\b'],
        'Spark': [r'\bSpark\b', r'\b스파크\b', r'\bApache\s+Spark\b', r'\bSPARK\b'],
        'Kafka': [r'\bKafka\b', r'\b카프카\b', r'\bApache\s+Kafka\b'],
        'Flink': [r'\bFlink\b', r'\b플링크\b', r'\bApache\s+Flink\b'],
        'Storm': [r'\bStorm\b', r'\b스톰\b', r'\bApache\s+Storm\b'],
        
        # 딥러닝 프레임워크
        'TensorFlow': [r'\bTensorFlow\b', r'\b텐서플로우\b', r'\b텐서플로\b'],
        'PyTorch': [r'\bPyTorch\b', r'\b파이토치\b'],
        'Keras': [r'\bKeras\b', r'\b케라스\b'],
        'MXNet': [r'\bMXNet\b', r'\b엠엑스넷\b'],
        'Caffe': [r'\bCaffe\b', r'\b카페\b'],
        
        # 데이터 처리 라이브러리
        'Pandas': [r'\bPandas\b', r'\b판다스\b', r'\bpandas\b'],
        'NumPy': [r'\bNumPy\b', r'\b넘파이\b', r'\bnumpy\b', r'\bNumPy\b'],
        'Scikit-learn': [r'\bScikit-learn\b', r'\b사이킷런\b', r'\bsklearn\b', r'\bscikit-learn\b'],
        'Matplotlib': [r'\bMatplotlib\b', r'\b맷플롯립\b', r'\bmatplotlib\b'],
        'Seaborn': [r'\bSeaborn\b', r'\b시본\b', r'\bseaborn\b'],
        'Plotly': [r'\bPlotly\b', r'\b플롯리\b'],
        'Bokeh': [r'\bBokeh\b', r'\b보케\b'],
        
        # 개발 도구
        'Jupyter': [r'\bJupyter\b', r'\b주피터\b', r'\bJupyter\s+Notebook\b'],
        'Git': [r'\bGit\b', r'\b깃\b', r'\bGIT\b', r'\bGitHub\b', r'\b깃허브\b', r'\bGitLab\b', r'\b깃랩\b'],
        'SVN': [r'\bSVN\b', r'\b서브버전\b'],
        'Mercurial': [r'\bMercurial\b', r'\b머큐리얼\b'],
        
        # 클라우드/인프라
        'AWS': [r'\bAWS\b', r'\b아마존\b', r'\bAmazon\s+Web\s+Services\b'],
        'GCP': [r'\bGCP\b', r'\b구글\s+클라우드\b', r'\bGoogle\s+Cloud\s+Platform\b'],
        'Azure': [r'\bAzure\b', r'\b애저\b', r'\b마이크로소프트\s+애저\b'],
        'Docker': [r'\bDocker\b', r'\b도커\b', r'\bDOCKER\b'],
        'Kubernetes': [r'\bKubernetes\b', r'\b쿠버네티스\b', r'\bK8s\b', r'\bk8s\b'],
        'Terraform': [r'\bTerraform\b', r'\b테라폼\b'],
        'Ansible': [r'\bAnsible\b', r'\b앤서블\b'],
        'Chef': [r'\bChef\b', r'\b셰프\b'],
        'Puppet': [r'\bPuppet\b', r'\b퍼핏\b'],
        'Jenkins': [r'\bJenkins\b', r'\b젠킨스\b'],
        'GitLab CI': [r'\bGitLab\s+CI\b', r'\bGitLabCI\b'],
        'CircleCI': [r'\bCircleCI\b', r'\b서클CI\b'],
        'Travis CI': [r'\bTravis\s+CI\b', r'\bTravisCI\b'],
        
        # 데이터베이스
        'MySQL': [r'\bMySQL\b', r'\b마이에스큐엘\b', r'\bmysql\b'],
        'PostgreSQL': [r'\bPostgreSQL\b', r'\b포스트그레스큐엘\b', r'\bPostgres\b', r'\bpostgres\b'],
        'MongoDB': [r'\bMongoDB\b', r'\b몽고디비\b', r'\bmongo\b'],
        'Redis': [r'\bRedis\b', r'\b레디스\b', r'\bREDIS\b'],
        'Oracle': [r'\bOracle\b', r'\b오라클\b'],
        'MariaDB': [r'\bMariaDB\b', r'\b마리아디비\b'],
        'Cassandra': [r'\bCassandra\b', r'\b카산드라\b'],
        'Elasticsearch': [r'\bElasticsearch\b', r'\b엘라스틱서치\b'],
        'Neo4j': [r'\bNeo4j\b', r'\b네오포제이\b'],
        'DynamoDB': [r'\bDynamoDB\b', r'\b다이나모디비\b'],
        'SQLite': [r'\bSQLite\b', r'\b에스큐엘라이트\b'],
        'CouchDB': [r'\bCouchDB\b', r'\b카우치디비\b'],
        
        # 데이터 엔지니어링
        'ETL': [r'\bETL\b', r'\b이티엘\b', r'\bExtract\s+Transform\s+Load\b'],
        'ELT': [r'\bELT\b', r'\b이엘티\b'],
        'Data Pipeline': [r'\bData\s+Pipeline\b', r'\b데이터\s+파이프라인\b', r'\b데이터파이프라인\b'],
        'Data Warehouse': [r'\bData\s+Warehouse\b', r'\b데이터\s+웨어하우스\b', r'\bDW\b', r'\b데이터웨어하우스\b'],
        'Data Lake': [r'\bData\s+Lake\b', r'\b데이터\s+레이크\b', r'\b데이터레이크\b'],
        'Airflow': [r'\bAirflow\b', r'\b에어플로우\b', r'\bApache\s+Airflow\b'],
        'Luigi': [r'\bLuigi\b', r'\b루이지\b'],
        'Prefect': [r'\bPrefect\b', r'\b프리펙트\b'],
        
        # 비즈니스 인텔리전스
        'BI': [r'\bBI\b', r'\b비즈니스\s+인텔리전스\b', r'\bBusiness\s+Intelligence\b', r'\b비즈니스인텔리전스\b'],
        'Dashboard': [r'\bDashboard\b', r'\b대시보드\b', r'\b대시\s+보드\b'],
        
        # 분석 기법
        'A/B Testing': [r'\bA/B\s+Testing\b', r'\bAB\s+테스트\b', r'\b에이비\s+테스팅\b', r'\bA/B\s+Test\b'],
        'Regression': [r'\bRegression\b', r'\b회귀분석\b', r'\b회귀\b', r'\b회귀\s+분석\b'],
        'Classification': [r'\bClassification\b', r'\b분류\b', r'\b분류\s+분석\b'],
        'Clustering': [r'\bClustering\b', r'\b클러스터링\b', r'\b군집화\b', r'\b군집\s+분석\b'],
        'NLP': [r'\bNLP\b', r'\b자연어\s+처리\b', r'\bNatural\s+Language\s+Processing\b', r'\b자연어처리\b'],
        'Computer Vision': [r'\bComputer\s+Vision\b', r'\b컴퓨터\s+비전\b', r'\bCV\b'],
        'Time Series': [r'\bTime\s+Series\b', r'\b시계열\b', r'\b시계열\s+분석\b', r'\b시계열데이터\b'],
        'Recommendation System': [r'\bRecommendation\s+System\b', r'\b추천\s+시스템\b', r'\b추천\s+알고리즘\b'],
        
        # 웹 개발 프레임워크
        'React': [r'\bReact\b', r'\b리액트\b', r'\bReact.js\b', r'\bReactJS\b'],
        'Vue': [r'\bVue\b', r'\b뷰\b', r'\bVue.js\b', r'\bVuejs\b', r'\bVueJS\b'],
        'Angular': [r'\bAngular\b', r'\b앵귤러\b', r'\bAngularJS\b'],
        'Node.js': [r'\bNode.js\b', r'\bNodejs\b', r'\b노드\b', r'\bNode\b'],
        'Django': [r'\bDjango\b', r'\b장고\b'],
        'Flask': [r'\bFlask\b', r'\b플라스크\b'],
        'Spring': [r'\bSpring\b', r'\b스프링\b', r'\bSpring\s+Boot\b', r'\b스프링부트\b'],
        'Express': [r'\bExpress\b', r'\b익스프레스\b', r'\bExpress.js\b'],
        'FastAPI': [r'\bFastAPI\b', r'\b패스트API\b'],
        'Laravel': [r'\bLaravel\b', r'\b라라벨\b'],
        'Ruby on Rails': [r'\bRuby\s+on\s+Rails\b', r'\bRails\b', r'\b루비온레일즈\b'],
        'ASP.NET': [r'\bASP\.NET\b', r'\bASP.NET\b'],
        
        # 모바일 개발
        'iOS': [r'\biOS\b', r'\b아이오에스\b', r'\bIOS\b'],
        'Android': [r'\bAndroid\b', r'\b안드로이드\b'],
        'React Native': [r'\bReact\s+Native\b', r'\b리액트\s+네이티브\b'],
        'Flutter': [r'\bFlutter\b', r'\b플러터\b'],
        'Xamarin': [r'\bXamarin\b', r'\b자마린\b'],
        'Ionic': [r'\bIonic\b', r'\b아이오닉\b'],
        
        # 소프트 스킬
        'Communication': [r'\bCommunication\b', r'\b커뮤니케이션\b', r'\b소통\b', r'\b의사소통\b'],
        'Problem Solving': [r'\bProblem\s+Solving\b', r'\b문제\s+해결\b', r'\b문제해결\b'],
        'Teamwork': [r'\bTeamwork\b', r'\b팀워크\b', r'\b협업\b', r'\b협력\b'],
        'Leadership': [r'\bLeadership\b', r'\b리더십\b', r'\b리더\b', r'\b리더쉽\b'],
        'Project Management': [r'\bProject\s+Management\b', r'\b프로젝트\s+관리\b', r'\bPM\b'],
        'Presentation': [r'\bPresentation\b', r'\b프레젠테이션\b', r'\b발표\b'],
        'Documentation': [r'\bDocumentation\b', r'\b문서화\b', r'\b문서\s+작성\b'],
        'Analytical Thinking': [r'\bAnalytical\s+Thinking\b', r'\b분석적\s+사고\b', r'\b분석적\s+사고력\b'],
        'Business Acumen': [r'\bBusiness\s+Acumen\b', r'\b비즈니스\s+감각\b', r'\b비즈니스\s+이해\b'],
        'Agile': [r'\bAgile\b', r'\b애자일\b', r'\bAgile\s+Methodology\b'],
        'Scrum': [r'\bScrum\b', r'\b스크럼\b'],
        'Kanban': [r'\bKanban\b', r'\b칸반\b'],
        
        # 도메인 지식
        'E-commerce': [r'\bE-commerce\b', r'\b이커머스\b', r'\b전자상거래\b', r'\bE커머스\b'],
        'Finance': [r'\bFinance\b', r'\b금융\b', r'\b핀테크\b', r'\bFinTech\b', r'\b금융권\b'],
        'Marketing': [r'\bMarketing\b', r'\b마케팅\b', r'\b디지털\s+마케팅\b'],
        'Platform': [r'\bPlatform\b', r'\b플랫폼\b', r'\b플랫폼\s+서비스\b'],
        'Blockchain': [r'\bBlockchain\b', r'\b블록체인\b'],
        'Game': [r'\bGame\b', r'\b게임\b', r'\b게임\s+개발\b'],
        'Healthcare': [r'\bHealthcare\b', r'\b헬스케어\b', r'\b의료\b'],
    }
    
    # 텍스트 정규화
    text_normalized = normalize_text(text)
    
    # 패턴 매칭으로 키워드 추출
    for keyword, patterns in keyword_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_normalized, re.IGNORECASE):
                keywords.add(keyword)
                break
    
    # 유효한 약어만 추출 (2-5자 대문자, 의미 있는 약어만)
    valid_acronyms = {'AI', 'ML', 'DL', 'BI', 'ETL', 'ELT', 'DW', 'NLP', 'CV', 'PM', 'AWS', 'GCP', 'SQL', 'R', 'JS', 'TS', 'API', 'REST', 'SOAP', 'gRPC', 'CI', 'CD', 'IoT', 'VR', 'AR', 'UI', 'UX', 'QA', 'TDD', 'BDD', 'OOP', 'FP', 'MVC', 'MVP', 'ORM', 'JWT', 'OAuth', 'SSO', 'LDAP', 'DNS', 'HTTP', 'HTTPS', 'TCP', 'UDP', 'IP', 'VPN', 'SSL', 'TLS', 'JSON', 'XML', 'YAML', 'CSV', 'PDF', 'HTML', 'CSS', 'SASS', 'SCSS', 'LESS', 'BEM', 'SEO', 'SEM', 'CMS', 'ERP', 'CRM', 'SCM', 'HRM', 'PLM', 'MES', 'WMS', 'TMS', 'POS', 'OSS', 'BSS', 'OSS', 'BSS', 'OSS', 'BSS'}
    acronyms = re.findall(r'\b([A-Z]{2,5})\b', text)
    for acr in acronyms:
        if acr in valid_acronyms:
            keywords.add(acr)
    
    # 데이터 기반 기술 용어 추출 추가
    technical_terms = extract_technical_terms_from_text(text)
    keywords.update(technical_terms)
    
    return keywords

def group_similar_expressions(keyword_counts: Dict[str, int], min_frequency: int = 1) -> Dict[str, List[str]]:
    """유사한 표현들을 그룹화"""
    
    # 최소 빈도수 필터링
    filtered_keywords = {k: v for k, v in keyword_counts.items() if v >= min_frequency}
    
    # 키워드 그룹화 사전 (실제 추출된 키워드와 매칭)
    keyword_groups = {
        # 프로그래밍 언어
        'Python': ['Python', '파이썬'],
        'SQL': ['SQL'],
        'R': ['R'],
        'Java': ['Java', '자바'],
        'JavaScript': ['JavaScript', '자바스크립트', 'JS'],
        
        # 데이터 분석 도구
        'Tableau': ['Tableau', '태블로'],
        'Power BI': ['Power BI'],
        'Excel': ['Excel', '엑셀'],
        
        # 머신러닝/딥러닝
        'Machine Learning': ['Machine Learning', '머신러닝', 'ML'],
        'Deep Learning': ['Deep Learning', '딥러닝', 'DL'],
        'AI': ['AI', '인공지능'],
        
        # 데이터 과학
        'Data Analysis': ['Data Analysis', '데이터 분석', '데이터분석'],
        'Data Science': ['Data Science', '데이터 사이언스', '데이터사이언스'],
        'Statistics': ['Statistics', '통계', '통계학'],
        
        # 빅데이터 기술
        'Big Data': ['Big Data', '빅데이터'],
        'Hadoop': ['Hadoop', '하둡'],
        'Spark': ['Spark', '스파크'],
        
        # 딥러닝 프레임워크
        'TensorFlow': ['TensorFlow', '텐서플로우', '텐서플로'],
        'PyTorch': ['PyTorch', '파이토치'],
        
        # 데이터 처리 라이브러리
        'Pandas': ['Pandas', '판다스'],
        'NumPy': ['NumPy', '넘파이'],
        'Scikit-learn': ['Scikit-learn', '사이킷런'],
        'Matplotlib': ['Matplotlib', '맷플롯립'],
        'Seaborn': ['Seaborn', '시본'],
        
        # 개발 도구
        'Jupyter': ['Jupyter', '주피터'],
        'Git': ['Git', '깃', 'GitHub', '깃허브'],
        
        # 클라우드/인프라
        'AWS': ['AWS', '아마존'],
        'GCP': ['GCP', '구글 클라우드'],
        'Azure': ['Azure', '애저'],
        'Docker': ['Docker', '도커'],
        'Kubernetes': ['Kubernetes', '쿠버네티스'],
        
        # 데이터베이스
        'MySQL': ['MySQL', '마이에스큐엘'],
        'PostgreSQL': ['PostgreSQL', '포스트그레스큐엘'],
        'MongoDB': ['MongoDB', '몽고디비'],
        'Redis': ['Redis', '레디스'],
        
        # 데이터 엔지니어링
        'ETL': ['ETL', '이티엘'],
        'Data Pipeline': ['Data Pipeline', '데이터 파이프라인', '데이터파이프라인'],
        'Data Warehouse': ['Data Warehouse', '데이터 웨어하우스', 'DW'],
        'Data Lake': ['Data Lake', '데이터 레이크', '데이터레이크'],
        
        # 비즈니스 인텔리전스
        'BI': ['BI', '비즈니스 인텔리전스'],
        'Dashboard': ['Dashboard', '대시보드', '대시 보드'],
        
        # 분석 기법
        'A/B Testing': ['A/B Testing', 'AB 테스트', '에이비 테스팅'],
        'Regression': ['Regression', '회귀분석', '회귀'],
        'Classification': ['Classification', '분류'],
        'Clustering': ['Clustering', '클러스터링', '군집화'],
        'NLP': ['NLP', '자연어 처리', '자연어처리'],
        'Time Series': ['Time Series', '시계열', '시계열 분석'],
        
        # 소프트 스킬
        'Communication': ['Communication', '커뮤니케이션', '소통', '의사소통'],
        'Problem Solving': ['Problem Solving', '문제 해결', '문제해결'],
        'Teamwork': ['Teamwork', '팀워크', '협업', '협력'],
        'Leadership': ['Leadership', '리더십', '리더'],
        'Project Management': ['Project Management', '프로젝트 관리', 'PM'],
        'Presentation': ['Presentation', '프레젠테이션', '발표'],
        'Documentation': ['Documentation', '문서화', '문서 작성'],
        'Analytical Thinking': ['Analytical Thinking', '분석적 사고', '분석적 사고력'],
        'Business Acumen': ['Business Acumen', '비즈니스 감각', '비즈니스 이해'],
        
        # 도메인 지식
        'E-commerce': ['E-commerce', '이커머스', '전자상거래'],
        'Finance': ['Finance', '금융', '핀테크', 'FinTech'],
        'Marketing': ['Marketing', '마케팅', '디지털 마케팅'],
        'Platform': ['Platform', '플랫폼', '플랫폼 서비스'],
    }
    
    # 역방향 매핑 생성 (표현 -> 키워드)
    expression_to_keyword = {}
    for keyword, expressions in keyword_groups.items():
        for expr in expressions:
            expr_normalized = expr.strip().lower()
            if expr_normalized not in expression_to_keyword:
                expression_to_keyword[expr_normalized] = keyword
    
    # 키워드 그룹화 결과
    grouped = defaultdict(list)
    used_expressions = set()
    
    # 먼저 정의된 그룹에 속하는 키워드 처리
    for expr, count in filtered_keywords.items():
        expr_normalized = expr.strip().lower()
        if expr_normalized in expression_to_keyword:
            keyword = expression_to_keyword[expr_normalized]
            if expr not in used_expressions:
                grouped[keyword].append(expr)
                used_expressions.add(expr)
        elif expr in expression_to_keyword:
            keyword = expression_to_keyword[expr]
            if expr not in used_expressions:
                grouped[keyword].append(expr)
                used_expressions.add(expr)
    
    # 그룹에 속하지 않는 키워드는 그대로 유지 (최소 빈도수 이상인 것만)
    for expr, count in filtered_keywords.items():
        if expr not in used_expressions:
            # 유사도 기반 그룹화 시도 (부분 문자열 매칭)
            found_group = False
            expr_lower = expr.lower()
            for keyword, expressions in grouped.items():
                for existing_expr in expressions:
                    existing_lower = existing_expr.lower()
                    # 한쪽이 다른 쪽에 포함되거나, 매우 유사한 경우
                    if (expr_lower in existing_lower or existing_lower in expr_lower) and \
                       len(expr_lower) >= 3 and len(existing_lower) >= 3:
                        grouped[keyword].append(expr)
                        found_group = True
                        break
                if found_group:
                    break
            
            if not found_group:
                # 새로운 그룹 생성
                grouped[expr] = [expr]
    
    return dict(grouped)

def create_keyword_dictionary(df: pd.DataFrame) -> pd.DataFrame:
    """키워드 사전 생성"""
    
    # 텍스트 추출
    all_texts = extract_text_from_dataframe(df)
    
    # 모든 텍스트에서 키워드 추출
    all_keywords = set()
    for text in all_texts:
        keywords = extract_keywords_from_text(text)
        all_keywords.update(keywords)
    
    # 키워드 빈도 계산
    keyword_counts = Counter()
    for text in all_texts:
        keywords = extract_keywords_from_text(text)
        for kw in keywords:
            keyword_counts[kw] += 1
    
    # 유사 표현 그룹화 (최소 빈도수 1회 이상)
    grouped_keywords = group_similar_expressions(dict(keyword_counts), min_frequency=1)
    
    # 키워드 그룹 사전 (사전에 정의된 모든 표현 포함) - 확장된 버전
    keyword_groups_full = {
        'Python': ['Python', '파이썬'],
        'SQL': ['SQL'],
        'R': ['R'],
        'Java': ['Java', '자바'],
        'JavaScript': ['JavaScript', '자바스크립트', 'JS'],
        'TypeScript': ['TypeScript', '타입스크립트', 'TS'],
        'C++': ['C++', 'Cpp'],
        'C': ['C', 'C언어'],
        'C#': ['C#', 'CSharp', 'C샵'],
        'Go': ['Go', 'Golang', '고'],
        'Rust': ['Rust', '러스트'],
        'Swift': ['Swift', '스위프트'],
        'Kotlin': ['Kotlin', '코틀린'],
        'PHP': ['PHP', 'php'],
        'Ruby': ['Ruby', '루비', 'Ruby on Rails', '루비온레일즈'],
        'Scala': ['Scala', '스칼라'],
        'Tableau': ['Tableau', '태블로'],
        'Power BI': ['Power BI', '파워비아이', 'PowerBI'],
        'Excel': ['Excel', '엑셀'],
        'Machine Learning': ['Machine Learning', '머신러닝', 'ML', '기계학습'],
        'Deep Learning': ['Deep Learning', '딥러닝', 'DL'],
        'AI': ['AI', '인공지능', 'Artificial Intelligence'],
        'Data Analysis': ['Data Analysis', '데이터 분석', '데이터분석', 'Data Analytics'],
        'Data Science': ['Data Science', '데이터 사이언스', '데이터사이언스'],
        'Statistics': ['Statistics', '통계', '통계학', 'Statistical Analysis'],
        'Big Data': ['Big Data', '빅데이터', '빅 데이터'],
        'Hadoop': ['Hadoop', '하둡'],
        'Spark': ['Spark', '스파크', 'Apache Spark'],
        'TensorFlow': ['TensorFlow', '텐서플로우', '텐서플로'],
        'PyTorch': ['PyTorch', '파이토치'],
        'Pandas': ['Pandas', '판다스'],
        'NumPy': ['NumPy', '넘파이', 'numpy'],
        'Scikit-learn': ['Scikit-learn', '사이킷런', 'sklearn'],
        'Matplotlib': ['Matplotlib', '맷플롯립'],
        'Seaborn': ['Seaborn', '시본'],
        'Jupyter': ['Jupyter', '주피터', 'Jupyter Notebook'],
        'Git': ['Git', '깃', 'GitHub', '깃허브'],
        'AWS': ['AWS', '아마존', 'Amazon Web Services'],
        'GCP': ['GCP', '구글 클라우드', 'Google Cloud Platform'],
        'Azure': ['Azure', '애저'],
        'Docker': ['Docker', '도커'],
        'Kubernetes': ['Kubernetes', '쿠버네티스', 'K8s'],
        'MySQL': ['MySQL', '마이에스큐엘'],
        'PostgreSQL': ['PostgreSQL', '포스트그레스큐엘', 'Postgres'],
        'MongoDB': ['MongoDB', '몽고디비'],
        'Redis': ['Redis', '레디스'],
        'ETL': ['ETL', '이티엘'],
        'Data Pipeline': ['Data Pipeline', '데이터 파이프라인', '데이터파이프라인'],
        'Data Warehouse': ['Data Warehouse', '데이터 웨어하우스', 'DW'],
        'Data Lake': ['Data Lake', '데이터 레이크', '데이터레이크'],
        'BI': ['BI', '비즈니스 인텔리전스', 'Business Intelligence'],
        'Dashboard': ['Dashboard', '대시보드', '대시 보드'],
        'A/B Testing': ['A/B Testing', 'AB 테스트', '에이비 테스팅', 'A/B Test'],
        'Regression': ['Regression', '회귀분석', '회귀'],
        'Classification': ['Classification', '분류'],
        'Clustering': ['Clustering', '클러스터링', '군집화'],
        'NLP': ['NLP', '자연어 처리', '자연어처리', 'Natural Language Processing'],
        'Time Series': ['Time Series', '시계열', '시계열 분석'],
        'Communication': ['Communication', '커뮤니케이션', '소통', '의사소통'],
        'Problem Solving': ['Problem Solving', '문제 해결', '문제해결'],
        'Teamwork': ['Teamwork', '팀워크', '협업', '협력'],
        'Leadership': ['Leadership', '리더십', '리더'],
        'Project Management': ['Project Management', '프로젝트 관리', 'PM'],
        'Presentation': ['Presentation', '프레젠테이션', '발표'],
        'Documentation': ['Documentation', '문서화', '문서 작성'],
        'Analytical Thinking': ['Analytical Thinking', '분석적 사고', '분석적 사고력'],
        'Business Acumen': ['Business Acumen', '비즈니스 감각', '비즈니스 이해'],
        'E-commerce': ['E-commerce', '이커머스', '전자상거래'],
        'Finance': ['Finance', '금융', '핀테크', 'FinTech'],
        'Marketing': ['Marketing', '마케팅', '디지털 마케팅'],
        'Platform': ['Platform', '플랫폼', '플랫폼 서비스'],
    }
    
    # 결과 데이터프레임 생성
    result_data = []
    for keyword, extracted_expressions in sorted(grouped_keywords.items()):
        # 사전에 정의된 표현들 가져오기
        if keyword in keyword_groups_full:
            all_expressions = keyword_groups_full[keyword]
        else:
            # 사전에 없는 키워드는 추출된 표현만 사용
            all_expressions = extracted_expressions
        
        # 추출된 표현과 사전 표현 합치기 (중복 제거)
        combined_expressions = list(set(all_expressions + extracted_expressions))
        
        # 정렬 (영문 먼저, 그 다음 한글)
        def sort_key(expr):
            if any(ord(c) >= 0xAC00 and ord(c) <= 0xD7A3 for c in expr):
                return (1, expr)  # 한글
            else:
                return (0, expr)  # 영문/기타
        
        unique_expressions = sorted(combined_expressions, key=sort_key)
        expressions_str = ', '.join(unique_expressions)
        
        result_data.append({
            'Keyword': keyword,
            'Expressions': expressions_str
        })
    
    result_df = pd.DataFrame(result_data)
    return result_df

def main():
    """메인 함수"""
    print("데이터 분석가.xlsx 파일 로딩 중...")
    df = load_data('데이터 분석가.xlsx')
    print(f"로드된 데이터: {df.shape[0]}개 행, {df.shape[1]}개 컬럼")
    
    print("\n키워드 추출 및 그룹화 중...")
    keyword_dict = create_keyword_dictionary(df)
    
    print(f"\n추출된 키워드 수: {len(keyword_dict)}")
    print("\n샘플 결과:")
    print(keyword_dict.head(20).to_string())
    
    # 엑셀 파일로 저장
    output_file = '필수역량_키워드_사전.xlsx'
    keyword_dict.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n✓ 키워드 사전이 '{output_file}'에 저장되었습니다.")
    
    return keyword_dict

if __name__ == "__main__":
    result = main()
