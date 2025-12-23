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
    print("\n📥 INPUT:")
    print(json.dumps(batch_input, indent=2, ensure_ascii=False))
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: API not running at {API_BASE_URL}")
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
            print(f"🌐 Sending POST request to {API_TICKET_ENDPOINT}")
            api_response = requests.post(
                API_TICKET_ENDPOINT,
                json=ticket_data,
                timeout=30
            )
            
            # Check response status
            if api_response.status_code == 200:
                response_data = api_response.json()
                print(f"\n✅ Response received (Status {api_response.status_code}):")
                print(f"   Answer: {response_data['response']}")
                print(f"   Escalated: {response_data['escalated']}")
                
                # Format answer for batch output
                answers.append({
                    "id": q_id,
                    "answer": response_data['response']
                })
            else:
                print(f"\n⚠️  Unexpected status code: {api_response.status_code}")
                print(f"Response: {api_response.text}")
                answers.append({
                    "id": q_id,
                    "answer": f"Error: API returned {api_response.status_code}"
                })
            
        except requests.exceptions.Timeout:
            print(f"\n⏱️  Timeout: API request took too long")
            answers.append({
                "id": q_id,
                "answer": "Error: Request timeout"
            })
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Connection error: Cannot reach API")
            answers.append({
                "id": q_id,
                "answer": "Error: Cannot connect to API"
            })
        except Exception as e:
            print(f"\n❌ Error processing {q_id}: {e}")
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
    print("📤 OUTPUT:")
    print("="*70)
    print(json.dumps(batch_output, indent=2, ensure_ascii=False))
    
    return batch_output


def test_single_question_via_api(q_id: str, query: str) -> dict:
    """Test single question via API"""
    
    print("\n" + "="*70)
    print("TESTING SINGLE QUESTION VIA API")
    print("="*70)
    
    print(f"\n📥 INPUT:")
    print(f"   ID: {q_id}")
    print(f"   Query: {query}")
    
    try:
        # Create ticket input from question
        ticket_data = {
            "ticket_id": q_id,
            "content": query
        }
        
        # Send to API
        print(f"\n🌐 Sending POST request to {API_TICKET_ENDPOINT}")
        api_response = requests.post(
            API_TICKET_ENDPOINT,
            json=ticket_data,
            timeout=30
        )
        
        if api_response.status_code == 200:
            response_data = api_response.json()
            print(f"\n📤 OUTPUT (Status {api_response.status_code}):")
            print(f"   ID: {q_id}")
            print(f"   Answer: {response_data['response']}")
            print(f"   Escalated: {response_data['escalated']}")
            
            if response_data.get('escalated'):
                print(f"   Reason: {response_data.get('reason')}")
            
            return response_data
        else:
            print(f"\n⚠️  Unexpected status code: {api_response.status_code}")
            print(f"Response: {api_response.text}")
            raise Exception(f"API returned status {api_response.status_code}")
        
    except requests.exceptions.Timeout:
        print(f"\n⏱️  Timeout: API request took too long")
        raise
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error: Cannot reach API at {API_BASE_URL}")
        print("Make sure the API is running: python -m uvicorn app.main:app --reload")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Sample batch input
    batch_input = {
        "Questions": [
            {
                "id": "Q001",
                "query": "ici il y'aura une question 1"
            },
            {
                "id": "Q002",
                "query": "ici il y'aura une question 2"
            },
            {
                "id": "Q003",
                "query": "ici il y'aura une question 3"
            },
            {
                "id": "Q004",
                "query": "ici il y'aura une question 4"
            }
        ]
    }
    
    # Test Option 1: Batch questions via API (default)
    batch_output = test_batch_questions_via_api(batch_input)
    
    # Test Option 2: Single question via API (uncomment to use)
    # test_single_question_via_api("Q001", "ici il y'aura une question 1")
