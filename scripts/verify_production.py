import asyncio
import httpx
import uuid
import time
import os
import json

BASE_URL = "http://localhost:8000"
MOCK_TOKEN = "mock_token_12345"

HEADERS = {
    "Authorization": f"Bearer {MOCK_TOKEN}",
}

async def verify():
    print("=== MANTRAONE BACKEND PRODUCTION VERIFICATION ===")
    
    async with httpx.AsyncClient(base_url=BASE_URL, headers=HEADERS) as client:
        # 1. Health Check
        print("\n[*] 1. Health Check")
        start = time.time()
        r = await client.get("/health")
        print(f"  Latency: {(time.time() - start)*1000:.2f}ms")
        assert r.status_code == 200, f"Health check failed: {r.text}"
        
        # 2. Family Creation
        print("\n[*] 2. Family Creation")
        r = await client.post("/v1/families/", params={"name": "Doe Family", "primary_member_name": "John Doe"})
        assert r.status_code == 200, f"Family creation failed: {r.text}"
        family_id = r.json()["id"]
        print(f"  Created Family ID: {family_id}")
        
        # 3. Create Conversation
        print("\n[*] 3. Create Conversation")
        r = await client.post("/v1/conversations/", json={"family_id": family_id, "member_id": family_id, "title": "Initial Chat"})
        assert r.status_code == 200, f"Conversation creation failed: {r.text}"
        conv_id = r.json()["id"]
        print(f"  Created Conversation ID: {conv_id}")
        
        # 4. Stream Message
        print("\n[*] 4. Stream Message (Initial Chat)")
        start = time.time()
        async with client.stream("POST", f"/v1/conversations/{conv_id}/messages", json={"family_id": family_id, "member_id": family_id, "text": "Hi, I am John. I sleep 4 hours a night."}) as response:
            assert response.status_code == 200, f"Message streaming failed"
            first_token = True
            print("  Response: ", end="")
            async for chunk in response.aiter_text():
                if first_token:
                    print(f"\n  TTFT: {(time.time() - start)*1000:.2f}ms")
                    first_token = False
                print(chunk, end="", flush=True)
            print(f"\n  Total Latency: {(time.time() - start)*1000:.2f}ms")
        
        # 5. Document Upload
        print("\n[*] 5. Document Upload (Ingestion)")
        start = time.time()
        files = {'file': ('test.pdf', b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n', 'application/pdf')}
        data = {'family_id': family_id, 'member_id': family_id, 'document_type': 'medical_history'}
        r = await client.post("/v1/documents/", data=data, files=files)
        print(f"  Upload Latency: {(time.time() - start)*1000:.2f}ms")
        assert r.status_code == 200, f"Document upload failed: {r.text}"
        
        # 6. Stream Message (With Recall)
        print("\n[*] 6. Stream Message (Recall test)")
        start = time.time()
        async with client.stream("POST", f"/v1/conversations/{conv_id}/messages", json={"family_id": family_id, "member_id": family_id, "text": "What do you know about my sleep?"}) as response:
            assert response.status_code == 200, f"Message streaming failed"
            first_token = True
            print("  Response: ", end="")
            async for chunk in response.aiter_text():
                if first_token:
                    print(f"\n  TTFT: {(time.time() - start)*1000:.2f}ms")
                    first_token = False
                print(chunk, end="", flush=True)
            print(f"\n  Total Latency: {(time.time() - start)*1000:.2f}ms")
            
        print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(verify())
