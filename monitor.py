#!/usr/bin/env python3
"""
HackRx 6.0 API Monitoring Script
Monitors API health, performance, and cache statistics
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class HackRxMonitor:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return {
                "status": "healthy",
                "data": response.json(),
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }
    
    def cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            response = requests.get(f"{self.base_url}/cache/stats", headers=self.headers, timeout=10)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.json(),
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None
            }
    
    def test_api_call(self, document_url: str, questions: list) -> Dict[str, Any]:
        """Test main API endpoint"""
        payload = {
            "documents": document_url,
            "questions": questions
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/hackrx/run",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            end_time = time.time()
            
            data = response.json()
            return {
                "status": "success",
                "response_time": end_time - start_time,
                "processing_time": data.get("metadata", {}).get("processing_time", 0),
                "num_answers": len(data.get("answers", [])),
                "cache_hit": data.get("metadata", {}).get("cache_hit", False)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None
            }
    
    def run_monitoring_cycle(self, test_document: str, test_questions: list) -> Dict[str, Any]:
        """Run a complete monitoring cycle"""
        print(f"🔍 Monitoring HackRx API at {self.base_url}")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("-" * 60)
        
        results = {}
        
        # Health Check
        print("1. Health Check...")
        health_result = self.health_check()
        results["health"] = health_result
        
        if health_result["status"] == "healthy":
            print(f"   ✅ Status: {health_result['data']['status']}")
            print(f"   📊 Version: {health_result['data']['version']}")
            print(f"   💾 Cache Size: {health_result['data']['cache_size']}")
            print(f"   ⚡ Response Time: {health_result['response_time']:.3f}s")
        else:
            print(f"   ❌ Health Check Failed: {health_result['error']}")
            return results
        
        # Cache Stats
        print("\n2. Cache Statistics...")
        cache_result = self.cache_stats()
        results["cache"] = cache_result
        
        if cache_result["status"] == "success":
            print(f"   ✅ Cache Size: {cache_result['data']['cache_size']}")
            print(f"   ⏱️  Cache TTL: {cache_result['data']['cache_ttl']}s")
            print(f"   📏 Max Document Size: {cache_result['data']['max_document_size']} bytes")
            print(f"   ❓ Max Questions: {cache_result['data']['max_questions']}")
        else:
            print(f"   ❌ Cache Stats Failed: {cache_result['error']}")
        
        # API Test
        print("\n3. API Functionality Test...")
        api_result = self.test_api_call(test_document, test_questions)
        results["api_test"] = api_result
        
        if api_result["status"] == "success":
            print(f"   ✅ API Test Passed")
            print(f"   ⚡ Total Response Time: {api_result['response_time']:.3f}s")
            print(f"   🔄 Processing Time: {api_result['processing_time']:.3f}s")
            print(f"   📝 Number of Answers: {api_result['num_answers']}")
            print(f"   💾 Cache Hit: {api_result['cache_hit']}")
        else:
            print(f"   ❌ API Test Failed: {api_result['error']}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 MONITORING SUMMARY")
        print("=" * 60)
        
        all_healthy = all([
            health_result["status"] == "healthy",
            cache_result["status"] == "success",
            api_result["status"] == "success"
        ])
        
        if all_healthy:
            print("🎉 All systems operational!")
        else:
            print("⚠️  Some issues detected:")
            if health_result["status"] != "healthy":
                print("   - Health check failed")
            if cache_result["status"] != "success":
                print("   - Cache stats unavailable")
            if api_result["status"] != "success":
                print("   - API functionality test failed")
        
        return results

def main():
    """Main monitoring function"""
    # Configuration
    BASE_URL = "https://ironwill-hackrx.vercel.app"
    API_TOKEN = "hackrx_secret_token_2024"
    
    # Official HackRx 6.0 Test Document
    TEST_DOCUMENT = "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D"
    TEST_QUESTIONS = [
        "What are the main policies covered in this Arogya Sanjeevani Policy?",
        "What is the definition of Cashless Facility in this policy?",
        "What are the exclusions mentioned in this policy?"
    ]
    
    # Create monitor instance
    monitor = HackRxMonitor(BASE_URL, API_TOKEN)
    
    # Run monitoring cycle
    results = monitor.run_monitoring_cycle(TEST_DOCUMENT, TEST_QUESTIONS)
    
    # Save results to file (optional)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"monitoring_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "test_document": TEST_DOCUMENT,
            "test_questions": TEST_QUESTIONS,
            "results": results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {filename}")
    
    # Exit with appropriate code
    all_healthy = all([
        results.get("health", {}).get("status") == "healthy",
        results.get("cache", {}).get("status") == "success",
        results.get("api_test", {}).get("status") == "success"
    ])
    
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main() 