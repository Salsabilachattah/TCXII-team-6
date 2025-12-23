"""
API Testing with Multiple Questions
Tests the agent via API with batch input/output format matching the expected structure:
Input: Questions with ids and queries
Output: Team name and Answers with ids and answers
"""

import sys
import json
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas import TicketInput, FinalResponse

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_TICKET_ENDPOINT = f"{API_BASE_URL}/ticket"


def test_batch_questions_via_api(batch_input: dict) -> dict:
    """Test agent via API with batch questions input"""
    
    print("\n" + "="*70)
    print("TESTING AGENT VIA API - BATCH MODE")
    print("="*70)
    print("\n INPUT:")
    print(json.dumps(batch_input, indent=2, ensure_ascii=False))
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n ERROR: API not running at {API_BASE_URL}")
        print("Make sure the API is running: python -m uvicorn app.main:app --reload")
        return None
    
    # Process each question
    answers = []
    
    for question in batch_input["Questions"]:
        q_id = question["id"]
        q_query = question["query"]
        
        print(f"\n\n{'='*70}")
        print(f"Processing: {q_id}")
        print(f"Query: {q_query}")
        print(f"{'='*70}")
        
        try:
            # Create ticket input from question
            ticket_data = {
                "ticket_id": q_id,
                "content": q_query
            }
            
            # Send to API
            print(f" Sending POST request to {API_TICKET_ENDPOINT}")
            api_response = requests.post(
                API_TICKET_ENDPOINT,
                json=ticket_data,
                timeout=30
            )
            
            # Check response status
            if api_response.status_code == 200:
                response_data = api_response.json()
                print(f"\n Response received (Status {api_response.status_code}):")
                print(f"   Answer: {response_data['response']}")
                print(f"   Escalated: {response_data['escalated']}")
                
                # Format answer for batch output
                answers.append({
                    "id": q_id,
                    "answer": response_data['response']
                })
            else:
                print(f"\n  Unexpected status code: {api_response.status_code}")
                print(f"Response: {api_response.text}")
                answers.append({
                    "id": q_id,
                    "answer": f"Error: API returned {api_response.status_code}"
                })
            
        except requests.exceptions.Timeout:
            print(f"\n  Timeout: API request took too long")
            answers.append({
                "id": q_id,
                "answer": "Error: Request timeout"
            })
        except requests.exceptions.ConnectionError:
            print(f"\n Connection error: Cannot reach API")
            answers.append({
                "id": q_id,
                "answer": "Error: Cannot connect to API"
            })
        except Exception as e:
            print(f"\n Error processing {q_id}: {e}")
            import traceback
            traceback.print_exc()
            answers.append({
                "id": q_id,
                "answer": f"Error: {str(e)}"
            })
    
    # Format output according to expected format
    batch_output = {
        "Team": "TEAM 6",
        "Answers": answers
    }
    
    print("\n\n" + "="*70)
    print(" OUTPUT:")
    print("="*70)
    print(json.dumps(batch_output, indent=2, ensure_ascii=False))
    
    return batch_output


def test_single_question_via_api(q_id: str, query: str) -> dict:
    """Test single question via API"""
    
    print("\n" + "="*70)
    print("TESTING SINGLE QUESTION VIA API")
    print("="*70)
    
    print(f"\n INPUT:")
    print(f"   ID: {q_id}")
    print(f"   Query: {query}")
    
    try:
        # Create ticket input from question
        ticket_data = {
            "ticket_id": q_id,
            "content": query
        }
        
        # Send to API
        print(f"\n Sending POST request to {API_TICKET_ENDPOINT}")
        api_response = requests.post(
            API_TICKET_ENDPOINT,
            json=ticket_data,
            timeout=30
        )
        
        if api_response.status_code == 200:
            response_data = api_response.json()
            print(f"\n OUTPUT (Status {api_response.status_code}):")
            print(f"   ID: {q_id}")
            print(f"   Answer: {response_data['response']}")
            print(f"   Escalated: {response_data['escalated']}")
            
            if response_data.get('escalated'):
                print(f"   Reason: {response_data.get('reason')}")
            
            return response_data
        else:
            print(f"\n Unexpected status code: {api_response.status_code}")
            print(f"Response: {api_response.text}")
            raise Exception(f"API returned status {api_response.status_code}")
        
    except requests.exceptions.Timeout:
        print(f"\n  Timeout: API request took too long")
        raise
    except requests.exceptions.ConnectionError:
        print(f"\n Connection error: Cannot reach API at {API_BASE_URL}")
        print("Make sure the API is running: python -m uvicorn app.main:app --reload")
        raise
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Sample batch input
    batch_input = {
    "Questions": [
      {
        "id": "Q001",
        "query": "ما هي منصة دوكسا (Doxa)؟"
      },
      {
        "id": "Q002",
        "query": "ما هو سعر الخطة الاحترافية (Plan Pro)؟"
      },
      {
        "id": "Q003",
        "query": "ماذا أفعل إذا ظهرت لي رسالة الخطأ 'البريد الإلكتروني غير معروف'؟"
      },
      {
        "id": "Q004",
        "query": "كيف يمكنني إنشاء مشروعي الأول؟"
      },
      {
        "id": "Q005",
        "query": "ما هي الاختلافات الرئيسية بين الخطة البسيطة (Simple) والخطة الاحترافية (Pro)؟"
      },
      {
        "id": "Q006",
        "query": "هل تتوافق دوكسا مع القانون 25-11 في الجزائر؟"
      },
      {
        "id": "Q007",
        "query": "كيف يمكنني إضافة عضو؟"
      },
      {
        "id": "Q008",
        "query": "هل النظام آمن؟"
      },
      {
        "id": "Q009",
        "query": "كيف يمكنني دمج برنامج المحاسبة المخصص الخاص بي؟"
      },
      {
        "id": "Q010",
        "query": "هل يمكنني استخدام دوكسا لإجراء مكالمات فيديو؟"
      },
      {
        "id": "Q011",
        "query": "من فاز ببطولة كأس العالم الأخيرة؟"
      },
      {
        "id": "Q012",
        "query": "كيف هي حالة الطقس في الجزائر العاصمة اليوم؟"
      },
      {
        "id": "Q013",
        "query": "كيف يدير النظام 'السبرنتات' (Sprints)؟"
      },
      {
        "id": "Q014",
        "query": "ما هي المهلة الزمنية لإخطار السلطة الوطنية (ANPDP) بحادث أمني؟"
      },
      {
        "id": "Q015",
        "query": "هل يمكنني تخزين أرقام البطاقات البنكية داخل المهام؟"
      },
      {
        "id": "Q016",
        "query": "ماذا يحدث بعد انتهاء الفترة التجريبية المجانية لمدة 14 يوماً؟"
      },
      {
        "id": "Q017",
        "query": "كيف يمكنني حذف بياناتي بشكل نهائي؟"
      },
      {
        "id": "Q018",
        "query": "ما هي حدود واجهة برمجة التطبيقات (API) للخطة الاحترافية؟"
      },
      {
        "id": "Q019",
        "query": "تطبيق الهاتف المحمول لا يتزامن، ماذا يجب أن أفعل؟"
      },
      {
        "id": "Q020",
        "query": "ما هي الأدوار المتاحة وما هي صلاحيات كل منها؟"
      },
      {
        "id": "Q021",
        "query": "كيف يمكنني تصدير تقاريري بصيغة PDF؟"
      },
      {
        "id": "Q022",
        "query": "هل يمكنني استخدام دوكسا للتعامل مع البيانات الطبية؟"
      },
      {
        "id": "Q023",
        "query": "كيف يمكنني أتمتة عملية أرشفة المهام المكتملة؟"
      },
      {
        "id": "Q024",
        "query": "هل التشفير المستخدم هو تشفير من طرف إلى طرف (End-to-end)؟"
      },
      {
        "id": "Q025",
        "query": "كم تبلغ تكلفة خطة الشركات (Enterprise)؟"
      },
      {
        "id": "Q026",
        "query": "ماذا أفعل إذا تم رفض رمز المصادقة الثنائية (2FA) الخاص بي؟"
      },
      {
        "id": "Q027",
        "query": "هل تدعم دوكسا اللغة الأمازيغية؟"
      },
      {
        "id": "Q028",
        "query": "كيف يمكنني ربط 'طلب سحب' (Pull Request) من GitHub بمهمة معينة؟"
      },
      {
        "id": "Q029",
        "query": "هل يمكنني استرداد أموالي إذا لم أكن راضياً عن الخدمة؟"
      },
      {
        "id": "Q030",
        "query": "من المسؤول في حالة حدوث خرق للبيانات؟"
      },
      {
        "id": "Q031",
        "query": "كيف يمكنني الاطلاع على سجل النشاط لمهمة محددة؟"
      },
      {
        "id": "Q032",
        "query": "كيف يمكنني دعوة 50 شخصاً في وقت واحد؟"
      },
      {
        "id": "Q033",
        "query": "هل تعمل منصة دوكسا بدون اتصال بالإنترنت؟"
      },
      {
        "id": "Q034",
        "query": "ما هي الشهادات التي تمتلكها مراكز البيانات؟"
      },
      {
        "id": "Q035",
        "query": "هل يمكنني إنشاء حقول مخصصة من نوع 'صورة'؟"
      },
      {
        "id": "Q036",
        "query": "كيف يمكنني إعداد إشعارات Slack لمشروع ما؟"
      },
      {
        "id": "Q037",
        "query": "ما هو الحجم الأقصى للمرفقات؟"
      },
      {
        "id": "Q038",
        "query": "كيف يمكنني تقليل بطء واجهة المستخدم؟"
      },
      {
        "id": "Q039",
        "query": "هل يمكنني الدفع عبر الحساب البريدي الجاري (CCP)؟"
      },
      {
        "id": "Q040",
        "query": "هل تعيين مندوب حماية البيانات (DPD) إلزامي لمنظمتي؟"
      },
      {
        "id": "Q041",
        "query": "كيف يمكنني نسخ مشروع بالكامل؟"
      },
      {
        "id": "Q042",
        "query": "ما الفرق بين 'الأرشفة' و'الحذف'؟"
      },
      {
        "id": "Q043",
        "query": "كيف يمكنني الحصول على فاتورة بصيغة PDF؟"
      },
      {
        "id": "Q044",
        "query": "هل يمكنني نقل بياناتي خارج الجزائر؟"
      },
      {
        "id": "Q045",
        "query": "كيف يمكنني الإشارة (@mention) لفريق تطوير كامل؟"
      },
      {
        "id": "Q046",
        "query": "شركتي تستخدم Okta، هل يمكنني استخدامه للولوج؟"
      },
      {
        "id": "Q047",
        "query": "ما هي نسبة وقت التشغيل (Uptime) المضمونة في الخطة الاحترافية؟"
      },
      {
        "id": "Q048",
        "query": "كيف يمكنني استعادة مهمة حُذفت عن طريق الخطأ؟"
      },
      {
        "id": "Q049",
        "query": "هل يمكنك إعطائي وصفة تحضير الكسكسي الجزائري؟"
      },
      {
        "id": "Q050",
        "query": "لخص لي فوائد دوكسا لفرق تكنولوجيا المعلومات (IT)."
      }
    ]
}
    
    # Test Option 1: Batch questions via API (default)
    batch_output = test_batch_questions_via_api(batch_input)
    
    # Test Option 2: Single question via API (uncomment to use)
    # test_single_question_via_api("Q001", "ici il y'aura une question 1")
