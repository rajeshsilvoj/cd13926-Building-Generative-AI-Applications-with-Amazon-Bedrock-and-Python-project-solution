#!/usr/bin/env python3
"""
Test script for demonstrating Bedrock Knowledge Base functionality
"""
from bedrock_utils import query_knowledge_base, generate_response, valid_prompt
import json

# Configuration
KB_ID = "VN8TJ0RVNU"
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

print("=" * 80)
print("BEDROCK KNOWLEDGE BASE TEST")
print("=" * 80)

# Test 1: Valid Prompt Function
print("\n1. Testing valid_prompt function")
print("-" * 80)

test_prompts = [
    ("What are the specifications of the excavator?", "Valid - about heavy machinery"),
    ("How does your AI model work?", "Invalid - asking about model architecture"),
    ("Tell me about cooking recipes", "Invalid - not about heavy machinery")
]

for prompt, expected in test_prompts:
    print(f"\nPrompt: {prompt}")
    print(f"Expected: {expected}")
    is_valid = valid_prompt(prompt, MODEL_ID)
    print(f"Result: {'VALID' if is_valid else 'INVALID'}")

# Test 2: Query Knowledge Base Function
print("\n\n2. Testing query_knowledge_base function")
print("-" * 80)

query = "What are the specifications of the excavator X950?"
print(f"\nQuery: {query}")
print("\nRetrieving from Knowledge Base...")

kb_results = query_knowledge_base(query, KB_ID)
print(f"\nFound {len(kb_results)} results")

if kb_results:
    for i, result in enumerate(kb_results[:2], 1):
        print(f"\n--- Result {i} ---")
        content = result['content']['text']
        print(f"Content preview: {content[:200]}...")
        print(f"Score: {result.get('score', 'N/A')}")
        
        # Display source location if available
        if 'location' in result:
            location = result['location']
            if 's3Location' in location:
                print(f"Source: s3://{location['s3Location']['uri']}")

# Test 3: Generate Response Function
print("\n\n3. Testing generate_response function")
print("-" * 80)

# Prepare context from KB results
if kb_results:
    context = "\n".join([result['content']['text'][:500] for result in kb_results[:2]])
    
    full_prompt = f"""Based on the following information about heavy machinery, answer the user's question.

Context:
{context}

User Question: {query}

Please provide a concise answer based only on the information provided."""

    print("\nGenerating response with:")
    print(f"  Temperature: 0.7")
    print(f"  Top P: 0.9")
    
    response = generate_response(full_prompt, MODEL_ID, temperature=0.7, top_p=0.9)
    
    print("\n--- Generated Response ---")
    print(response)

# Test 4: Different Temperature and Top P values
print("\n\n4. Testing different temperature/top_p values")
print("-" * 80)

simple_prompt = "Describe the bulldozer in one sentence."

configs = [
    {"temp": 0.0, "top_p": 0.1, "desc": "Low temperature, low top_p (deterministic)"},
    {"temp": 1.0, "top_p": 1.0, "desc": "High temperature, high top_p (creative)"}
]

for config in configs:
    print(f"\n{config['desc']}")
    print(f"Temperature: {config['temp']}, Top P: {config['top_p']}")
    response = generate_response(simple_prompt, MODEL_ID, config['temp'], config['top_p'])
    print(f"Response: {response[:150]}...")

print("\n" + "=" * 80)
print("TESTS COMPLETE")
print("=" * 80)
