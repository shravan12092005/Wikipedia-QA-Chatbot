import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api"
SESSION_ID = f"test_runner_{int(time.time())}"

print("==================================================")
print("     Wikipedia QA Chatbot — API Integration Tests")
print("==================================================")

def assert_response(step_name: str, response, expected_intent: str = None):
    print(f"\n[Test Step] {step_name}")
    try:
        response.raise_for_status()
        data = response.json()
        
        # Verify schema
        assert "message" in data, "Response missing 'message'"
        assert "session_state" in data, "Response missing 'session_state'"
        
        msg = data["message"]
        state = data["session_state"]
        
        assert "role" in msg and msg["role"] == "assistant", "Invalid message role"
        assert "content" in msg, "Message missing content"
        assert "meta" in msg, "Message missing meta"
        
        print("  ✅ HTTP Status 200 OK")
        print("  ✅ Schema validated successfully")
        
        if expected_intent:
            actual_intent = state.get("last_intent")
            assert actual_intent == expected_intent, f"Expected intent '{expected_intent}', got '{actual_intent}'"
            print(f"  ✅ Intent matched: {actual_intent} (Confidence: {state.get('last_confidence')}%)")
            
        print("  Preview response:")
        print(f"    {msg['content'].splitlines()[0]}")
        return data
    except AssertionError as ae:
        print(f"  ❌ Assertion failed: {ae}")
        raise ae
    except Exception as e:
        print(f"  ❌ Step failed: {e}")
        raise e

# Step 1: Greeting
req_body = {
    "message": "Hello!",
    "session_id": SESSION_ID
}
res = requests.post(f"{API_URL}/chat", json=req_body)
data1 = assert_response("Greeting Interaction", res, expected_intent="greeting")

# Step 2: Topic Search
req_body = {
    "message": "Tell me about Artificial Intelligence",
    "session_id": SESSION_ID
}
print("\n🔍 Fetching article from Wikipedia (this may take a few seconds)...")
res = requests.post(f"{API_URL}/chat", json=req_body)
data2 = assert_response("Topic Search Retrieval", res, expected_intent="topic_request")

state2 = data2["session_state"]
assert state2["last_article_title"] != "", "Article title should not be empty"
assert state2["articles_fetched"] == 1, "Articles fetched count should be 1"
print(f"  ✅ Verified Wikipedia article loaded: {state2['last_article_title']}")
print(f"  ✅ Wikipedia URL: {state2['last_article_url']}")
print(f"  ✅ Article length: {state2['last_article_word_count']} words")

# Step 3: Question Answering
req_body = {
    "message": "Who coined the term Artificial Intelligence?",
    "session_id": SESSION_ID
}
res = requests.post(f"{API_URL}/chat", json=req_body)
data3 = assert_response("Question Answering (RoBERTa)", res, expected_intent="question_answering")

state3 = data3["session_state"]
assert state3["questions_asked"] == 1, "Questions asked count should be 1"
print(f"  ✅ Stats check: questions asked = {state3['questions_asked']}")

# Step 4: Summarization comparison
req_body = {
    "message": "Summarize it",
    "session_id": SESSION_ID
}
print("\n📝 Generating summaries using BART and T5, calculating ROUGE scores (takes 10-30s)...")
res = requests.post(f"{API_URL}/chat", json=req_body)
data4 = assert_response("Comparative Summarization (BART vs T5)", res, expected_intent="summarization")

state4 = data4["session_state"]
assert state4["summaries_done"] == 1, "Summaries done count should be 1"
assert state4["bart_summary"] != "", "BART summary should not be empty"
assert state4["t5_summary"] != "", "T5 summary should not be empty"
assert "bart" in state4["rouge_scores"] and "t5" in state4["rouge_scores"], "ROUGE scores missing"
print(f"  ✅ Comparative summarization complete")
print(f"  ✅ Winner evaluated: {state4['rouge_winner']}")
print(f"  ✅ ROUGE scores: BART R-1={state4['rouge_scores']['bart']['rouge1']} vs T5 R-1={state4['rouge_scores']['t5']['rouge1']}")

# Step 5: Reset Session
req_body = {
    "session_id": SESSION_ID
}
res = requests.post(f"{API_URL}/clear", json=req_body)
res.raise_for_status()
state5 = res.json()
assert state5["articles_fetched"] == 0, "Cleared articles fetched should be 0"
assert state5["questions_asked"] == 0, "Cleared questions asked should be 0"
assert state5["summaries_done"] == 0, "Cleared summaries done should be 0"
print("\n[Test Step] Reset Session State")
print("  ✅ Session state successfully cleared on the backend")

print("\n==================================================")
print(" 🎉 ALL API INTEGRATION TESTS PASSED SUCCESSFULLY!")
print("==================================================")
