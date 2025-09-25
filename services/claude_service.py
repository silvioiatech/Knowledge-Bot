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
        """
        Transform Gemini analysis into educational Markdown content.
        
        Args:
            analysis: Structured analysis from Gemini
            
        Returns:
            Enriched Markdown content
            
        Raises:
            ClaudeEnrichmentError: If enrichment fails
        """
        try:
            if logger:
                logger.info("Starting Claude content enrichment via OpenRouter")
            
            # Build enrichment prompt
            prompt = self._build_enrichment_prompt(analysis)
            
            # Call OpenRouter API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/silvioiatech/Knowledge-Bot",
                "X-Title": "Knowledge Bot"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": Config.OPENROUTER_MAX_TOKENS,  # Increased to 4000 for comprehensive content
                "temperature": 0.7  # Increased for more creative technical writing
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
        """Build comprehensive textbook-quality enrichment prompt for Claude."""
        title = analysis.get('title', 'Video Analysis')
        subject = analysis.get('subject', 'General')
        category_confidence = analysis.get('category_confidence', 0.0)
        key_points = analysis.get('key_points', [])
        tools = analysis.get('tools', [])
        code_snippets = analysis.get('code_snippets', [])
        error_resolutions = analysis.get('error_resolutions', [])
        performance_notes = analysis.get('performance_notes', [])
        security_considerations = analysis.get('security_considerations', [])
        visual_concepts = analysis.get('visual_concepts', [])
        prerequisites = analysis.get('prerequisites', [])
        problem_context = analysis.get('problem_context', '')
        visible_text = analysis.get('visible_text', [])
        resources = analysis.get('resources', [])
        production_ready = analysis.get('production_ready', False)
        platform_specific = analysis.get('platform_specific', [])
        
        prompt = f"""Transform this comprehensive video analysis into TEXTBOOK-QUALITY technical reference material suitable for professional publication and ebook creation.

**ANALYSIS DATA:**
Title: {title}
Subject: {subject}  
Category Confidence: {category_confidence:.2f}
Production Ready: {production_ready}
Platform Specific: {', '.join(platform_specific) if platform_specific else 'Universal'}

**COMPREHENSIVE KEY POINTS:**
{chr(10).join(f"• {point}" for point in key_points) if key_points else 'No key points provided'}

**TOOLS & TECHNOLOGIES:**
{chr(10).join(f"• {tool}" for tool in tools) if tools else 'Not specified'}

**CODE EXAMPLES EXTRACTED:**
{chr(10).join(f"• {snippet.get('purpose', 'Code')}: {snippet.get('language', 'unknown')} ({len(snippet.get('code', ''))} chars)" for snippet in code_snippets) if code_snippets else 'No code examples'}

**ERROR RESOLUTIONS:**
{chr(10).join(f"• {error.get('error', 'Error')}: {error.get('solution', 'Solution')}" for error in error_resolutions) if error_resolutions else 'No errors documented'}

**PERFORMANCE CONSIDERATIONS:**
{chr(10).join(f"• {note}" for note in performance_notes) if performance_notes else 'None mentioned'}

**SECURITY ASPECTS:**
{chr(10).join(f"• {consideration}" for consideration in security_considerations) if security_considerations else 'None mentioned'}

**PREREQUISITES:**
{chr(10).join(f"• {prereq}" for prereq in prerequisites) if prerequisites else 'None specified'}

**PROBLEM CONTEXT:**
{problem_context if problem_context else 'Not provided'}

**VISUAL CONCEPTS IDENTIFIED:**
{chr(10).join(f"• {concept}" for concept in visual_concepts) if visual_concepts else 'None identified'}

**INSTRUCTIONS FOR TEXTBOOK-QUALITY CONTENT:**

Create comprehensive technical documentation with these REQUIRED sections:

# {title}

## 📋 Chapter Overview
- Comprehensive introduction from first principles
- Real-world relevance and business impact
- Learning objectives and expected outcomes
- Difficulty assessment and time investment

## 🎯 Prerequisites & Context
- Required background knowledge with specific examples
- Environmental setup requirements
- Tool installation and configuration
- {problem_context if problem_context else 'Why this topic matters in professional development'}

## 🔍 Fundamental Concepts
- In-depth explanation of core principles
- Multiple approaches to implementation (not just the one shown)
- Theoretical background and industry standards
- Comparison with alternative methodologies

## 🛠️ Technical Implementation

### Architecture Overview
{"[DIAGRAM: System architecture showing component interaction]" if any("architecture" in concept.lower() for concept in visual_concepts) else ""}

### Step-by-Step Implementation
{"[DIAGRAM: Process flow from input to output]" if any("flow" in concept.lower() for concept in visual_concepts) else ""}

#### Minimal Example (Proof of Concept)
```{code_snippets[0].get('language', 'text') if code_snippets else 'text'}
// 10-15 line minimal working example
// Include inline comments explaining each step
```

#### Production Implementation  
```{code_snippets[0].get('language', 'text') if code_snippets else 'text'}
// 50+ line production-ready version
// Include error handling, logging, configuration
// Follow industry best practices
```

#### Anti-Pattern Example
```{code_snippets[0].get('language', 'text') if code_snippets else 'text'}
// What NOT to do and why
// Common mistakes and their consequences
```

## ⚡ Performance Analysis

### Complexity Analysis
- Time and space complexity with Big O notation
- Scalability considerations and bottlenecks
- Memory usage patterns and optimization opportunities

### Benchmarking & Optimization
{"[DIAGRAM: Performance comparison charts]" if performance_notes else ""}
- Performance metrics and measurement strategies
- Optimization techniques and their trade-offs
- Caching strategies and resource management

## 🔒 Security Considerations

### Security Audit Checklist
- Input validation and sanitization requirements
- Authentication and authorization patterns
- Data protection and privacy considerations
- Common vulnerabilities and mitigation strategies

### Security Best Practices
- Industry-standard security implementations
- Compliance requirements and regulatory considerations
- Security testing and monitoring approaches

## 🚀 Production Deployment

### Deployment Architecture
{"[DIAGRAM: Production deployment topology]" if production_ready else ""}

### Environment Configuration
- Development, staging, and production setups
- Configuration management and secrets handling
- Monitoring and observability requirements

### Scalability Planning
- Horizontal and vertical scaling strategies
- Load balancing and failover mechanisms
- Capacity planning and resource estimation

## 🐛 Troubleshooting Guide

### Common Issues & Resolutions
{chr(10).join(f"**{error.get('error', 'Error')}**{chr(10)}- Solution: {error.get('solution', 'Solution')}{chr(10)}- Prevention: {error.get('context', 'Additional context')}{chr(10)}" for error in error_resolutions) if error_resolutions else ""}

### Debugging Strategies
- Systematic debugging approaches
- Logging and monitoring best practices
- Performance profiling techniques

### Error Recovery Patterns
- Graceful degradation strategies
- Circuit breaker and retry mechanisms
- Fallback and backup procedures

## 🔄 Testing Strategies

### Unit Testing Approach
```{code_snippets[0].get('language', 'text') if code_snippets else 'text'}
// Comprehensive unit test examples
// Edge cases and boundary conditions
```

### Integration Testing
- API testing and contract validation
- Database integration testing
- Third-party service integration

### Load & Performance Testing
- Stress testing methodologies
- Performance regression testing
- Capacity and endurance testing

## 📊 Tool Comparison Matrix

| Feature | {tools[0] if tools else 'Tool A'} | Alternative 1 | Alternative 2 |
|---------|------------|---------------|---------------|
| Performance | | | |
| Learning Curve | | | |
| Community Support | | | |
| License Cost | | | |
| Enterprise Features | | | |

## 🔗 Advanced Topics & Extensions

### Related Technologies
- Ecosystem integration opportunities
- Migration strategies from legacy systems
- Future roadmap and emerging trends

### Advanced Use Cases
- Enterprise-scale implementations
- High-availability configurations
- Multi-cloud deployment strategies

## 📚 Comprehensive Resources

### Official Documentation
{chr(10).join(f"- [{resource}]({resource})" for resource in resources if resource.startswith('http')) if resources else ""}

### Books & Publications
- Industry-standard textbooks and references
- Academic papers and research publications
- Industry case studies and white papers

### Hands-On Learning
- Interactive tutorials and workshops
- Practice projects and coding challenges
- Community forums and discussion groups

### Professional Development
- Certification programs and learning paths
- Conference talks and technical presentations
- Industry blogs and thought leadership articles

## 🎓 Summary & Next Steps

### Key Takeaways
- Essential concepts for long-term retention
- Industry applications and career relevance
- Professional development implications

### Recommended Learning Path
1. Master fundamental concepts with hands-on practice
2. Implement production-grade solutions
3. Explore advanced patterns and architectures
4. Contribute to open-source projects

### Assessment Questions
- Self-evaluation questions for comprehension
- Technical interview preparation topics
- Practical project suggestions

---

**CONTENT REQUIREMENTS:**
- Minimum {Config.TARGET_CONTENT_LENGTH} words comprehensive coverage
- Include [DIAGRAM: description] placeholders where technical diagrams would enhance understanding
- Provide working code examples that can be executed
- Include specific version numbers and compatibility notes
- Add troubleshooting sections for common issues
- Create tool comparison tables with specific criteria
- Reference current industry standards and best practices

**FORMATTING STANDARDS:**
- Use professional technical writing style
- Include proper markdown formatting with syntax highlighting
- Add relevant emojis for section identification
- Structure content for easy navigation and reference
- Ensure content is suitable for direct publication

Write this as a comprehensive technical reference that could serve as a standalone chapter in a professional technology textbook."""
        
        return prompt


# Convenience function for external use
async def enrich_analysis(analysis: Dict[str, Any]) -> str:
    """
    Enrich Gemini analysis with Claude.
    
    Args:
        analysis: Analysis dictionary from Gemini
        
    Returns:
        Enriched Markdown content
    """
    service = ClaudeService()
    return await service.enrich_content(analysis)