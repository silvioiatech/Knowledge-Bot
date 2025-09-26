"""Claude content enrichment service via OpenRouter."""

from typing import Dict, Any

try:
    import httpx
    from loguru import logger
except ImportError:
    httpx = None
    logger = None

from config import Config


class ClaudeEnrichmentError(Exception):
    """Custom exception for Claude enrichment failures."""
    pass


class ClaudeService:
    """Service for enriching content with Claude API via OpenRouter."""
    
    def __init__(self):
        if not httpx:
            raise ClaudeEnrichmentError("httpx not installed")
        
        if not Config.OPENROUTER_API_KEY:
            raise ClaudeEnrichmentError("OPENROUTER_API_KEY not configured")
            
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.OPENROUTER_MODEL
        self.base_url = Config.OPENROUTER_BASE_URL
        self.timeout = Config.CLAUDE_ENRICHMENT_TIMEOUT
    
    async def enrich_content(self, analysis: Dict[str, Any]) -> str:
        """Transform Gemini analysis into educational Markdown content."""
        try:
            if logger:
                logger.info("Starting Claude content enrichment via OpenRouter")
            
            prompt = self._build_enrichment_prompt(analysis)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/silvioiatech/Knowledge-Bot",
                "X-Title": "Knowledge Bot"
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": Config.OPENROUTER_MAX_TOKENS,
                "temperature": 0.1
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                enriched_content = result["choices"][0]["message"]["content"].strip()
            
            if logger:
                logger.success("Claude enrichment completed via OpenRouter")
            
            return enriched_content
            
        except Exception as e:
            if logger:
                logger.error(f"Claude enrichment error: {e}")
            raise ClaudeEnrichmentError(f"Enrichment failed: {e}")
    
    def _build_enrichment_prompt(self, analysis: Dict[str, Any]) -> str:
        """Build aggressive prompt forcing complete content generation."""
        title = analysis.get('title', 'Technical Guide')
        subject = analysis.get('subject', 'Technology')
        key_points = analysis.get('key_points', [])
        tools = analysis.get('tools', [])
        
        points_text = '; '.join(key_points[:6]) if key_points else 'General concepts'
        tools_text = ', '.join(tools[:4]) if tools else 'Various tools'

        return f"""Generate a COMPLETE comprehensive technical guide. Write the ENTIRE content now - no partial responses.

TOPIC: {title}
SUBJECT: {subject}
CONCEPTS: {points_text}
TOOLS: {tools_text}

Write a complete guide with these sections:

# {title}

## Executive Summary
Write 4-5 detailed paragraphs (800+ words) explaining what this technology is, its business importance, current professional applications, specific problems it solves, and future industry trends.

## Learning Objectives  
List 15+ specific, measurable learning outcomes covering:
- Theoretical foundations and core principles
- Practical implementation from basic to advanced
- Performance optimization and troubleshooting
- Security and production deployment
- Integration and architectural patterns

## Prerequisites & Environment Setup
Detail exactly what's needed:
- Required background knowledge with examples
- Software versions and installation procedures  
- Development environment configuration
- Hardware requirements and cloud setup
- Security and compliance considerations

## Core Concepts & Theory
Write comprehensive explanation (1000+ words):
- Historical development and evolution
- Fundamental principles from first principles
- Key terminology and definitions
- Mathematical or algorithmic foundations
- Relationships to other technologies
- Industry standards and best practices

## Technical Implementation

### Basic Implementation
```python
# Complete working example (50+ lines)
import logging
import asyncio
from typing import Dict, List, Any

class BasicImplementation:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    async def process(self, data: Any) -> Dict[str, Any]:
        \"\"\"Main processing logic with error handling.\"\"\"
        try:
            validated_data = self._validate_input(data)
            result = await self._execute_logic(validated_data)
            return {{'status': 'success', 'result': result}}
        except Exception as e:
            self.logger.error(f"Processing failed: {{e}}")
            return {{'status': 'error', 'message': str(e)}}
    
    def _validate_input(self, data: Any) -> Any:
        \"\"\"Input validation logic.\"\"\"
        if not data:
            raise ValueError("Input data cannot be empty")
        return data
    
    async def _execute_logic(self, data: Any) -> Any:
        \"\"\"Core business logic implementation.\"\"\"
        # Add your specific implementation here
        await asyncio.sleep(0.1)  # Simulate processing
        return f"Processed: {{data}}"

# Usage example
async def main():
    config = {{'timeout': 30, 'retries': 3}}
    processor = BasicImplementation(config)
    result = await processor.process("sample data")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Production Implementation
```python
# Enterprise-ready implementation (100+ lines)
import os
import json
import logging
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

@dataclass
class ProductionConfig:
    api_key: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    log_level: str = "INFO"
    
class ProductionService:
    def __init__(self, config: ProductionConfig):
        self.config = config
        self._setup_logging()
        self.metrics = {{
            'requests_total': 0,
            'requests_success': 0, 
            'requests_failed': 0
        }}
    
    def _setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def process_with_retry(self, data: Any) -> Dict[str, Any]:
        \"\"\"Process with retry logic and metrics.\"\"\"
        self.metrics['requests_total'] += 1
        
        for attempt in range(self.config.max_retries):
            try:
                result = await self._process_single(data)
                self.metrics['requests_success'] += 1
                return result
            except Exception as e:
                self.logger.warning(f"Attempt {{attempt + 1}} failed: {{e}}")
                if attempt == self.config.max_retries - 1:
                    self.metrics['requests_failed'] += 1
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _process_single(self, data: Any) -> Dict[str, Any]:
        \"\"\"Single processing attempt.\"\"\"
        # Validation
        if not self._validate_data(data):
            raise ValueError("Invalid input data")
        
        # Processing
        result = await self._execute_processing(data)
        
        # Post-processing
        return self._format_result(result)
    
    def _validate_data(self, data: Any) -> bool:
        \"\"\"Comprehensive data validation.\"\"\"
        return data is not None and isinstance(data, (dict, str, list))
    
    async def _execute_processing(self, data: Any) -> Any:
        \"\"\"Core processing logic.\"\"\"
        # Simulate actual processing
        await asyncio.sleep(0.1)
        return f"Processed: {{data}}"
    
    def _format_result(self, result: Any) -> Dict[str, Any]:
        \"\"\"Format result for API response.\"\"\"
        return {{
            'status': 'success',
            'data': result,
            'timestamp': asyncio.get_event_loop().time(),
            'metrics': self.metrics.copy()
        }}
```

## Performance & Optimization
Comprehensive performance analysis:
- Computational complexity with Big O notation
- Memory usage patterns and optimization strategies
- Concurrency and parallelization techniques
- Caching strategies at multiple levels
- Database optimization and query performance
- Load balancing and scaling considerations

## Security Implementation
Security best practices:
- Input validation and sanitization
- Authentication and authorization patterns
- Data encryption at rest and in transit
- Security monitoring and audit logging
- Compliance requirements (GDPR, HIPAA, SOC2)
- Vulnerability assessment and penetration testing

## Production Deployment
Production readiness:
- CI/CD pipeline setup and automation
- Environment configuration management
- Container orchestration and scaling
- Monitoring and observability implementation
- Disaster recovery and backup strategies
- Performance monitoring and alerting

## Troubleshooting Guide
Systematic debugging approach:
- Common issues and their solutions
- Performance profiling and optimization
- Log analysis and error pattern recognition
- Root cause analysis methodologies
- Incident response and escalation procedures
- Preventive measures and monitoring

## Testing Strategy
Comprehensive testing approach:
```python
# Test suite example (75+ lines)
import unittest
import pytest
from unittest.mock import Mock, patch

class TestImplementation(unittest.TestCase):
    def setUp(self):
        self.config = ProductionConfig(
            api_key="test_key",
            base_url="https://test.example.com"
        )
        self.service = ProductionService(self.config)
    
    @pytest.mark.asyncio
    async def test_successful_processing(self):
        test_data = {{'key': 'value'}}
        result = await self.service.process_with_retry(test_data)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('data', result)
        self.assertIn('timestamp', result)
    
    @pytest.mark.asyncio
    async def test_retry_logic(self):
        with patch.object(self.service, '_process_single', 
                         side_effect=[Exception("Error"), {{'status': 'success'}}]):
            result = await self.service.process_with_retry({{'test': 'data'}})
            self.assertEqual(result['status'], 'success')
    
    def test_data_validation(self):
        self.assertTrue(self.service._validate_data({{'valid': 'data'}}))
        self.assertFalse(self.service._validate_data(None))
        self.assertFalse(self.service._validate_data(""))
```

## Tool Comparison & Alternatives
Detailed technology comparison:
- Feature comparison matrix
- Performance benchmarking results
- Cost analysis and licensing considerations
- Learning curve and adoption factors
- Community support and ecosystem
- Long-term viability and roadmap

## Advanced Topics
Advanced concepts and patterns:
- Enterprise integration strategies
- Microservices architecture patterns
- Cloud-native deployment approaches
- Advanced monitoring and observability
- Machine learning integration
- Future technology directions

## Learning Resources
Comprehensive resource list:
- Official documentation and tutorials
- Industry books and publications
- Online courses and certification programs
- Hands-on labs and practice projects
- Community forums and support channels
- Professional development paths

## Assessment & Projects
Knowledge validation:
- Self-assessment questions
- Practical implementation projects
- Performance optimization challenges
- Security implementation exercises
- Production deployment scenarios
- Career development guidance

Generate the COMPLETE guide with substantial content in ALL sections. Write 12,000+ words of comprehensive, detailed technical content."""


async def enrich_analysis(analysis: Dict[str, Any]) -> str:
    """Enrich Gemini analysis with Claude."""
    service = ClaudeService()
    return await service.enrich_content(analysis)