import sys
import json
import os
import asyncio
import httpx
from uuid import UUID

BASE_URL = "http://localhost:8000"
MOCK_TOKEN = "mock_token_12345"
HEADERS = {"Authorization": f"Bearer {MOCK_TOKEN}"}

async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run demo/load_golden_family.py <family_name>")
        sys.exit(1)
        
    family_name = sys.argv[1].lower()
    golden_file = os.path.join(os.path.dirname(__file__), f"../../../golden/families/{family_name}.json")
    
    if not os.path.exists(golden_file):
        print(f"Error: Could not find golden data for {family_name} at {golden_file}")
        sys.exit(1)
        
    with open(golden_file, "r") as f:
        data = json.load(f)
        
    print(f"=== Loading Golden Dataset for: {data['name']} ===")
    
    async with httpx.AsyncClient(base_url=BASE_URL, headers=HEADERS) as client:
        # 1. Create Family
        print(f"[*] Creating Family: {data['name']}")
        r = await client.post("/v1/families/", params={"name": data['name'], "primary_member_name": data['primary_member']['name']})
        assert r.status_code == 200, f"Family creation failed: {r.text}"
        family_id = r.json()["id"]
        
        # 2. Upload Reports
        reports_dir = os.path.join(os.path.dirname(__file__), "../../../golden/reports")
        for report in data.get("reports", []):
            pdf_path = os.path.join(reports_dir, report["file"])
            if not os.path.exists(pdf_path):
                print(f"[!] Warning: Missing report {pdf_path}")
                continue
                
            print(f"[*] Uploading Report: {report['file']} for {report['member']}")
            with open(pdf_path, "rb") as pdf_file:
                files = {'file': (report['file'], pdf_file, 'application/pdf')}
                form_data = {'family_id': family_id, 'member_id': family_id, 'document_type': report['type']}
                r = await client.post("/v1/documents/", data=form_data, files=files)
                assert r.status_code == 200, f"Upload failed: {r.text}"
                
        # 3. Trigger baseline conversation
        print("[*] Creating Baseline Conversation")
        r = await client.post("/v1/conversations/", json={"family_id": family_id, "member_id": family_id, "title": "Golden Baseline"})
        assert r.status_code == 200, f"Conversation failed: {r.text}"
        conv_id = r.json()["id"]
        
        print("[*] Initiating Context Sync Chat")
        async with client.stream("POST", f"/v1/conversations/{conv_id}/messages", json={"family_id": family_id, "member_id": family_id, "text": "Syncing baseline medical memory. Please confirm."}) as response:
            assert response.status_code == 200, "Sync failed"
            async for _ in response.aiter_text():
                pass
                
        print(f"\n=== Golden Dataset {family_name} loaded successfully! ===")

if __name__ == "__main__":
    asyncio.run(main())
