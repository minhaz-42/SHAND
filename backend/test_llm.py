"""
Test script for LLM-enhanced analysis endpoints.
Run after setting ANTHROPIC_API_KEY environment variable.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    cd backend
    python3 test_llm.py
"""

import os
import sys
import requests
import json

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = "http://127.0.0.1:8000"

def test_llm_analysis():
    """Test the LLM-enhanced endpoint"""
    print("\n" + "="*60)
    print("TEST 1: LLM-Enhanced Analysis (/analyze-llm/)")
    print("="*60)
    
    sample_text = """
    We believe our new product will capture 30% of the market within 12 months.
    Users will naturally adopt it because it's 10x better than competitors.
    The engineering team can build this with current resources.
    We expect minimal churn once customers start using it.
    The technology is future-proof and won't need major updates for 5 years.
    """
    
    payload = {"text": sample_text}
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-llm/", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Found {len(result['assumptions'])} assumptions")
            print("\nRule-based findings:")
            for a in result['assumptions']:
                if not a.get('llm_enhanced'):
                    status = "✓" if a.get('llm_feedback', {}).get('status') == 'CONFIRMED' else '?'
                    print(f"  {status} {a['text'][:50]}... ({a['type']})")
            
            print("\nLLM-discovered assumptions:")
            for a in result['assumptions']:
                if a.get('llm_enhanced'):
                    print(f"  ✨ {a['text'][:50]}... ({a['type']})")
            
            print(f"\n📋 Executive Summary:\n{result.get('executive_summary', 'N/A')}")
        else:
            print(f"Error: {response.json()}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: ./runserver.sh")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_deepdive_analysis():
    """Test the deep-dive analysis endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Deep-Dive Analysis (/analyze-deepdive/)")
    print("="*60)
    
    sample_text = """
    We expect users will adopt this immediately because it's 10x better.
    The market timing is perfect right now in Q1.
    """
    
    payload = {
        "text": sample_text,
        "assumption_indices": [0]  # Deep dive on first assumption
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze-deepdive/", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            for a in result['assumptions']:
                if a.get('deep_analysis') and not a['deep_analysis'].get('error'):
                    print(f"\n📊 Deep Analysis for: {a['text'][:60]}...")
                    da = a['deep_analysis']
                    print(f"  Likelihood: {da.get('real_world_likelihood')}/10 - {da.get('likelihood_reasoning')}")
                    print(f"  Worst Case: {da.get('worst_case_scenario')[:60]}...")
                    print(f"  Mitigation: {da.get('mitigation_strategy')[:60]}...")
        else:
            print(f"Error: {response.json()}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: ./runserver.sh")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_original_endpoint():
    """Test that original endpoint still works"""
    print("\n" + "="*60)
    print("TEST 3: Original Endpoint (backward compatibility)")
    print("="*60)
    
    sample_text = "We assume the market will grow rapidly because demand is increasing."
    payload = {"text": sample_text}
    
    try:
        response = requests.post(f"{BASE_URL}/analyze/", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {len(result['assumptions'])} assumptions (rule-based)")
            print(f"✅ Original endpoint still works!")
        else:
            print(f"Error: {response.json()}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: ./runserver.sh")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n🧪 LLM Integration Test Suite")
    
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n❌ ANTHROPIC_API_KEY not set!")
        print("\nSet it with:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    print("\n⚠️  Make sure Django server is running!")
    print("   In another terminal: cd /Users/tanvir/Desktop/SHAND && ./runserver.sh")
    print("\nRunning tests in 3 seconds... (Press Ctrl+C to cancel)")
    
    import time
    time.sleep(3)
    
    test_original_endpoint()
    test_llm_analysis()
    test_deepdive_analysis()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
