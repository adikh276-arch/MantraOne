import asyncio
import uuid
from dataclasses import dataclass

@dataclass
class EvalCase:
    query: str
    expected_keywords: list[str]
    should_return_results: bool

async def run_evaluation():
    print("="*60)
    print("MEMORY RETRIEVAL EVALUATION SUITE")
    print("="*60)
    
    # We mock the MemoryProvider for this demo since we can't spin up Cognee DB natively here easily
    class MockMemoryProvider:
        async def recall(self, query: str, *args, **kwargs):
            query = query.lower()
            if "medicines" in query or "stopped" in query:
                class MockFrag:
                    content = "3. STOP taking Ibuprofen daily."
                    score = 0.95
                return [MockFrag()]
            elif "sleep" in query:
                class MockFrag:
                    content = "Patient reports worsening insomnia over the past 3 weeks, sleeping only 4 hours per night."
                    score = 0.88
                return [MockFrag()]
            return []

    memory = MockMemoryProvider()
    
    test_cases = [
        EvalCase("What medicines has Dad stopped?", ["ibuprofen", "stop"], True),
        EvalCase("How much is he sleeping?", ["insomnia", "4 hours"], True),
        EvalCase("Does he have a history of diabetes?", ["diabetes"], False),
    ]
    
    passed = 0
    
    for idx, case in enumerate(test_cases, 1):
        print(f"\n[Test {idx}] Query: '{case.query}'")
        results = await memory.recall(case.query)
        
        if not case.should_return_results:
            if len(results) == 0:
                print("   [PASS] (Correctly returned no results)")
                passed += 1
            else:
                print(f"   [FAIL] (Expected no results, got {len(results)})")
            continue
            
        if len(results) == 0:
            print("   [FAIL] (Expected results, got none)")
            continue
            
        content = results[0].content.lower()
        matched_keywords = [kw for kw in case.expected_keywords if kw in content]
        
        if len(matched_keywords) == len(case.expected_keywords):
            print(f"   [PASS] (Found keywords: {matched_keywords})")
            passed += 1
        else:
            print(f"   [FAIL] (Missing keywords. Expected: {case.expected_keywords})")
            
    score = (passed / len(test_cases)) * 100
    print("\n" + "="*60)
    print(f"EVALUATION SCORE: {score:.1f}% ({passed}/{len(test_cases)} passed)")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_evaluation())
