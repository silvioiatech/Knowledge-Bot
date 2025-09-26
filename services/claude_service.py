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
                "max_tokens": Config.OPENROUTER_MAX_TOKENS,
                "temperature": 0.7
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
        
        # Pre-format complex strings to avoid f-string issues
        key_points_formatted = '\n'.join(f"• {point}" for point in key_points[:10]) if key_points else '• No key points extracted'
        tools_list = ', '.join(tools[:8]) if tools else 'Not specified'
        
        error_solutions_formatted = ""
        if error_resolutions:
            error_items = []
            for error in error_resolutions[:5]:
                error_text = f"**Issue: {error.get('error', 'Common Problem')}**\n"
                error_text += f"*Solution:* {error.get('solution', 'Detailed solution approach')}\n"
                error_text += f"*Prevention:* {error.get('context', 'How to prevent this issue')}\n"
                error_items.append(error_text)
            error_solutions_formatted = '\n'.join(error_items)
        else:
            error_solutions_formatted = "**Issue: Configuration Errors**\n*Solution:* Step-by-step debugging approach\n*Prevention:* Validation and testing strategies"
        
        resources_formatted = ""
        if resources:
            resource_links = []
            for resource in resources[:3]:
                if resource.startswith('http'):
                    resource_name = resource.split('/')[-1] if '/' in resource else resource
                    resource_links.append(f"- [{resource_name}]({resource}) - Official documentation")
            resources_formatted = '\n'.join(resource_links) if resource_links else "- [Official Documentation](https://example.com) - Core reference"
        else:
            resources_formatted = "- [Official Documentation](https://example.com) - Core reference"

        prompt = f"""You are a professional technical writer creating COMPREHENSIVE TEXTBOOK-QUALITY content. Transform this video analysis into a complete educational reference that could be published as a technical book chapter.

**ANALYSIS INPUT:**
Title: {title}
Subject: {subject}
Key Points: {len(key_points)} concepts identified
Tools: {tools_list}
Code Examples: {len(code_snippets)} blocks
Error Solutions: {len(error_resolutions)} troubleshooting items
Performance Notes: {len(performance_notes)} optimization tips
Security Items: {len(security_considerations)} considerations

**EXTRACTED KEY POINTS:**
{key_points_formatted}

**YOUR MISSION:**
Create a COMPREHENSIVE 15,000+ word professional technical guide. This must be publication-ready content suitable for:
- Professional textbooks
- Technical certification materials  
- Enterprise training programs
- Advanced university courses

# {title}

## 📚 Executive Summary

Write 4-5 comprehensive paragraphs (800+ words) explaining:
- What this technology/concept is and its fundamental purpose
- Why it's critical in today's tech landscape and business environment
- How professionals and organizations currently use it
- The problems it solves and value it provides
- Future trajectory and industry adoption trends

## 🎯 Learning Objectives & Prerequisites

### What You'll Master
Write 12+ specific, measurable learning outcomes covering:
- Theoretical foundations and core principles
- Practical implementation skills from beginner to expert
- Industry best practices and professional techniques
- Troubleshooting and optimization capabilities
- Advanced patterns and architectural decisions

### Prerequisites & Environment Setup
Detail exactly what learners need:
- Specific background knowledge with examples
- Required software versions and installation steps
- Development environment configuration
- Hardware requirements and performance considerations
- Account setup for cloud services or tools

### Time Investment & Learning Path
- Reading and comprehension: X hours
- Hands-on practice and exercises: Y hours  
- Project work and portfolio building: Z hours
- Mastery and advanced topics: W hours

## 🔍 Theoretical Foundation

### Historical Context & Evolution
Write 600+ words covering:
- Origin story and initial development
- Key milestones and breakthrough moments
- Evolution of approaches and methodologies
- Current state and industry maturity
- Comparison with predecessor technologies

### Core Principles & Concepts  
Provide deep technical explanation (1000+ words):
- Fundamental theoretical concepts from first principles
- Mathematical foundations where applicable
- Key terminology and precise definitions
- Conceptual models and mental frameworks
- Relationship to other technologies and standards

### Industry Context & Business Impact
- Market size, adoption rates, and growth trends
- Major companies and their implementations
- Business drivers and competitive advantages
- ROI considerations and cost-benefit analysis
- Career opportunities and salary implications

## 🛠️ Technical Implementation

### System Architecture & Design
[DIAGRAM: High-level system architecture with components and data flow]

Write comprehensive architectural analysis (1200+ words):
- Component breakdown and responsibilities
- Data flow and interaction patterns
- Scalability characteristics and limitations  
- Integration points and API boundaries
- Design patterns and architectural decisions

### Implementation Approaches

#### Approach 1: Production-Ready Implementation
```python
# Comprehensive working example (100+ lines)
# Include complete error handling, logging, configuration
# Add detailed inline comments explaining each section
# Follow industry best practices and security guidelines
# Make this truly production-ready code with:
# - Input validation
# - Error recovery  
# - Performance optimization
# - Security measures
# - Monitoring hooks
# - Configuration management
```

#### Approach 2: Alternative Pattern  
```python
# Different implementation strategy (75+ lines)
# Compare trade-offs with first approach
# Show when to use this pattern vs others
# Include performance comparisons
# Demonstrate different use cases
```

#### Anti-Patterns & Common Mistakes
```python
# Example of problematic implementation (50+ lines)
# Explain exactly why this approach fails
# Show the real-world problems it creates
# Demonstrate how to identify these issues
# Provide refactoring strategies
```

### Configuration & Customization
- Environment-specific configurations
- Feature flags and runtime options
- Performance tuning parameters
- Security configuration requirements
- Monitoring and observability setup

## ⚡ Performance Engineering

### Performance Analysis & Optimization
Write detailed analysis (800+ words):
- Computational complexity with Big O notation
- Memory usage patterns and optimization strategies
- I/O bottlenecks and mitigation techniques
- Concurrency and parallelization opportunities
- Caching strategies at multiple levels

### Benchmarking & Measurement
[DIAGRAM: Performance testing methodology and results visualization]

- Benchmark design and execution methodology
- Key performance indicators and metrics
- Baseline establishment and regression detection
- Load testing and stress testing strategies
- Performance profiling tools and techniques

### Scalability Architecture
| Metric | Small Scale | Medium Scale | Enterprise Scale |
|--------|------------|--------------|------------------|
| Concurrent Users | | | |
| Data Volume | | | |
| Response Time | | | |
| Memory Usage | | | |
| CPU Utilization | | | |

## 🔒 Security & Compliance

### Security Architecture
Write comprehensive security analysis (600+ words):
- Threat modeling and risk assessment
- Authentication and authorization strategies
- Data protection and encryption requirements
- Network security considerations
- Compliance framework alignment (GDPR, HIPAA, SOC2)

### Security Implementation Checklist
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS and CSRF protection  
- [ ] Secure configuration management
- [ ] Audit logging and monitoring
- [ ] Incident response procedures

### Security Testing & Validation
- Static application security testing (SAST)
- Dynamic application security testing (DAST)
- Penetration testing methodologies
- Security code review processes
- Vulnerability management workflows

## 🚀 Production Operations

### Deployment Architecture
[DIAGRAM: Multi-environment deployment pipeline with CI/CD integration]

Detail production deployment (800+ words):
- Environment strategy (dev, staging, production)
- CI/CD pipeline design and implementation
- Blue-green and canary deployment strategies
- Rollback procedures and disaster recovery
- Infrastructure as Code (IaC) implementation

### Monitoring & Observability
- Application performance monitoring (APM)
- Infrastructure monitoring and alerting
- Log aggregation and analysis
- Distributed tracing implementation
- SLA/SLO definition and measurement

### Operational Runbooks
- Standard operating procedures
- Incident response playbooks
- Maintenance and update procedures
- Capacity planning and scaling triggers
- Business continuity planning

## 🐛 Troubleshooting Mastery

### Common Issues & Expert Solutions
{error_solutions_formatted}

### Advanced Debugging Techniques
Write comprehensive debugging guide (600+ words):
- Systematic troubleshooting methodology
- Debugging tool selection and usage
- Log analysis and pattern recognition
- Performance profiling and bottleneck identification
- Root cause analysis frameworks

### Incident Management
- Incident classification and prioritization
- Escalation procedures and communication
- Post-incident analysis and learning
- Knowledge base maintenance
- Team training and skill development

## 🔄 Testing Strategy

### Comprehensive Testing Approach
```python
# Complete test suite implementation (200+ lines)
# Include unit tests with edge cases
# Integration test scenarios
# Performance and load testing
# Security testing examples
# Mock implementations and test data
```

### Test Automation & CI/CD
- Test pyramid strategy implementation
- Continuous testing in deployment pipeline
- Quality gates and deployment criteria
- Test data management and environments
- Testing tool selection and integration

## 📊 Tool Ecosystem Analysis

### Comprehensive Tool Comparison
| Capability | {tools[0] if tools else 'Primary Tool'} | {tools[1] if len(tools) > 1 else 'Alternative A'} | {tools[2] if len(tools) > 2 else 'Alternative B'} | Enterprise Solution |
|------------|----------|------------|------------|-------------------|
| Learning Curve | | | | |
| Performance | | | | |
| Scalability | | | | |
| Community Support | | | | |
| Enterprise Features | | | | |
| License Cost | | | | |
| Integration Ecosystem | | | | |
| Long-term Viability | | | | |

### Selection Criteria Framework
- Technical requirements analysis
- Business constraint evaluation
- Total cost of ownership calculation
- Risk assessment and mitigation
- Future roadmap alignment

## 🔗 Advanced Topics & Future Directions

### Emerging Patterns & Innovations
Write forward-looking analysis (500+ words):
- Industry trends and future developments
- Emerging technologies and integration opportunities
- Research directions and experimental approaches
- Standards evolution and community initiatives
- Career development and skill evolution

### Enterprise Integration Strategies
- Legacy system integration patterns
- Microservices architecture considerations
- Cloud-native transformation approaches
- Data architecture and governance
- Organizational change management

## 📚 Learning Resources & Professional Development

### Authoritative References
{resources_formatted}

### Professional Development Path
Write comprehensive career guidance (400+ words):
- Certification programs and learning tracks
- Hands-on project recommendations
- Community engagement opportunities
- Conference and networking events
- Thought leadership and content creation

### Hands-On Learning Projects
**Beginner Project:** Build basic implementation with core features
**Intermediate Project:** Add monitoring, error handling, and optimization
**Advanced Project:** Design enterprise-scale architecture
**Expert Project:** Contribute to open source or research

## 🎓 Assessment & Knowledge Validation

### Comprehensive Knowledge Check
1. **Theoretical Understanding:** Explain core principles and their relationships
2. **Implementation Skills:** Design and code production-ready solutions
3. **Architecture Design:** Plan scalable, secure, maintainable systems
4. **Troubleshooting:** Diagnose and resolve complex issues
5. **Strategic Thinking:** Evaluate technology choices and business impact

### Professional Application
- Real-world project planning and execution
- Technology evaluation and recommendation
- Team leadership and knowledge transfer
- Innovation and continuous improvement
- Industry contribution and thought leadership

---

**CRITICAL REQUIREMENTS:**
- Write 15,000+ words of comprehensive, detailed content
- Include working, tested code examples for all concepts
- Provide specific version numbers, configuration details, and compatibility notes
- Create detailed troubleshooting guides with step-by-step solutions
- Include performance benchmarks and optimization strategies
- Add security considerations and compliance requirements
- Structure content for professional publication and certification use
- Ensure every section provides actionable, practical value for professionals

This must be textbook-quality content suitable for professional publication, certification programs, and enterprise training materials."""

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