#!/usr/bin/env python3
"""
Test script for the Ollama Gateway client.

This script tests the basic functionality of the Ollama Gateway client.
"""

import asyncio
import sys
from typing import List

from citadel_llm.gateway import OllamaGateway
from citadel_llm.models import LLMManager, Message, GenerationOptions
from citadel_llm.exceptions import CitadelLLMError


async def test_list_models():
    """Test listing models."""
    print("Testing list_models...")
    gateway = OllamaGateway()
    
    try:
        models = await gateway.list_models()
        print(f"Available models: {[model['name'] for model in models]}")
    except CitadelLLMError as e:
        print(f"Error listing models: {e}")
        return False
    
    return True


async def test_generate():
    """Test text generation."""
    print("\nTesting generate...")
    gateway = OllamaGateway()
    
    try:
        response = await gateway.generate(
            prompt="What is the capital of France?",
            model="mistral:latest",
            options={"temperature": 0.7, "top_p": 0.9}
        )
        print(f"Response: {response.get('response', '')}")
        print(f"Model: {response.get('model', '')}")
        print(f"Prompt tokens: {response.get('prompt_eval_count', 0)}")
        print(f"Completion tokens: {response.get('eval_count', 0)}")
    except CitadelLLMError as e:
        print(f"Error generating text: {e}")
        return False
    
    return True


async def test_generate_stream():
    """Test streaming text generation."""
    print("\nTesting generate_stream...")
    gateway = OllamaGateway()
    
    try:
        print("Response: ", end="", flush=True)
        async for chunk in gateway.generate_stream(
            prompt="Explain quantum computing in simple terms.",
            model="mistral:latest",
            options={"temperature": 0.7, "top_p": 0.9}
        ):
            print(chunk, end="", flush=True)
        print()  # Add newline at the end
    except CitadelLLMError as e:
        print(f"Error streaming text: {e}")
        return False
    
    return True


async def test_chat():
    """Test chat completion."""
    print("\nTesting chat...")
    gateway = OllamaGateway()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, who are you?"}
    ]
    
    try:
        response = await gateway.chat(
            messages=messages,
            model="mistral:latest",
            options={"temperature": 0.7, "top_p": 0.9}
        )
        print(f"Response: {response.get('message', {}).get('content', '')}")
    except CitadelLLMError as e:
        print(f"Error in chat: {e}")
        return False
    
    return True


async def test_llm_manager():
    """Test LLMManager."""
    print("\nTesting LLMManager...")
    manager = LLMManager()
    
    try:
        # List supported models
        models = manager.list_models()
        print(f"Supported models: {[model.name for model in models]}")
        
        # Generate text
        result = await manager.generate(
            prompt="What is the meaning of life?",
            model_name="mistral:latest",
            options=GenerationOptions(temperature=0.7, top_p=0.9)
        )
        print(f"Response: {result.text}")
        print(f"Tokens: {result.total_tokens} (prompt: {result.prompt_tokens}, completion: {result.completion_tokens})")
        
        # Chat
        messages = [
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Tell me a joke.")
        ]
        
        result = await manager.chat(
            messages=messages,
            model_name="mistral:latest",
            options=GenerationOptions(temperature=0.7, top_p=0.9)
        )
        print(f"Chat response: {result.text}")
    except CitadelLLMError as e:
        print(f"Error in LLMManager: {e}")
        return False
    
    return True


async def main():
    """Run all tests."""
    tests = [
        test_list_models,
        test_generate,
        test_generate_stream,
        test_chat,
        test_llm_manager
    ]
    
    results = []
    for test in tests:
        results.append(await test())
    
    # Print summary
    print("\n=== Test Summary ===")
    for i, (test, result) in enumerate(zip(tests, results)):
        print(f"{test.__name__}: {'PASS' if result else 'FAIL'}")
    
    # Return success if all tests passed
    return all(results)


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
