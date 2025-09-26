"""Core data models for the Knowledge Bot pipeline."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

@dataclass
class VideoMetadata:
    """Basic video metadata."""
    url: str
    platform: str  # "tiktok", "youtube", "instagram"
    title: str = ""
    author: str = ""
    duration: float = 0.0
    posted_date: Optional[datetime] = None
    language: str = "en"
    hashtags: List[str] = field(default_factory=list)
    view_count: Optional[int] = None
    like_count: Optional[int] = None

@dataclass
class TranscriptSegment:
    """A segment of transcript with timestamp."""
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str] = None
    confidence: float = 1.0

@dataclass
class Entity:
    """An extracted entity with context."""
    name: str
    type: str  # "person", "organization", "technology", "concept", etc.
    mentions: List[Dict[str, Any]] = field(default_factory=list)  # [{text, timestamp, context}]
    confidence: float = 1.0
    description: Optional[str] = None

@dataclass
class Claim:
    """A factual claim that can be verified."""
    text: str
    timestamp: float
    confidence: float
    context: str
    is_factual: Optional[bool] = None  # True/False/None (opinion)
    evidence: List[str] = field(default_factory=list)  # Sources supporting/refuting
    corrections: List[str] = field(default_factory=list)  # Corrected information

@dataclass
class OCRResult:
    """Text extracted from video frames."""
    text: str
    timestamp: float
    confidence: float
    bounding_box: Optional[Dict[str, float]] = None
    context: str = ""

@dataclass
class WebResearchFact:
    """Fact-checked information from web research."""
    original_claim: str
    corrected_info: str
    sources: List[str]
    confidence: float
    research_timestamp: datetime
    is_correction: bool = False  # True if this corrects misinformation

@dataclass
class QualityScores:
    """Quality assessment scores."""
    content_accuracy: float = 0.0  # 0-100
    technical_depth: float = 0.0   # 0-100
    educational_value: float = 0.0  # 0-100
    source_credibility: float = 0.0  # 0-100
    completeness: float = 0.0      # 0-100
    overall: float = 0.0           # 0-100

@dataclass
class ContentOutline:
    """Structured outline of the content."""
    main_topic: str
    subtopics: List[str]
    key_concepts: List[str]
    learning_objectives: List[str]
    prerequisites: List[str]
    difficulty_level: str  # "beginner", "intermediate", "advanced", "expert"

@dataclass
class GeminiAnalysis:
    """Complete analysis output from Gemini processor."""
    # Basic metadata
    video_metadata: VideoMetadata
    
    # Content analysis
    transcript: List[TranscriptSegment]
    entities: List[Entity]
    claims: List[Claim]
    ocr_results: List[OCRResult]
    
    # Research and fact-checking
    web_research_facts: List[WebResearchFact]
    
    # Quality and structure
    quality_scores: QualityScores
    content_outline: ContentOutline
    
    # Citations and sources
    citations: List[str] = field(default_factory=list)
    
    # Technical metadata
    content_hash: str = ""
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    gemini_model: str = ""
    processing_time: float = 0.0
    
    def __post_init__(self):
        """Generate content hash after initialization."""
        if not self.content_hash:
            self.content_hash = self._generate_content_hash()
    
    def _generate_content_hash(self) -> str:
        """Generate unique hash for content deduplication."""
        # Use video URL + transcript text for hashing
        try:
            if self.transcript and len(self.transcript) > 0:
                if hasattr(self.transcript[0], 'text'):
                    # TranscriptSegment objects
                    transcript_text = " ".join([seg.text for seg in self.transcript])
                elif isinstance(self.transcript[0], dict):
                    # Dict format
                    transcript_text = " ".join([seg.get('text', '') for seg in self.transcript])
                else:
                    # Fallback to string representation
                    transcript_text = " ".join([str(seg) for seg in self.transcript])
            else:
                transcript_text = ""
        except Exception:
            transcript_text = "fallback_content"
            
        content_for_hash = f"{self.video_metadata.url}|{transcript_text[:1000]}"
        return hashlib.sha256(content_for_hash.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "video_metadata": {
                "url": self.video_metadata.url,
                "platform": self.video_metadata.platform,
                "title": self.video_metadata.title,
                "author": self.video_metadata.author,
                "duration": self.video_metadata.duration,
                "posted_date": self.video_metadata.posted_date.isoformat() if self.video_metadata.posted_date else None,
                "language": self.video_metadata.language,
                "hashtags": self.video_metadata.hashtags,
                "view_count": self.video_metadata.view_count,
                "like_count": self.video_metadata.like_count
            },
            "transcript": [
                {
                    "start_time": seg.start_time if hasattr(seg, 'start_time') else seg.get('start_time', 0),
                    "end_time": seg.end_time if hasattr(seg, 'end_time') else seg.get('end_time', 0),
                    "text": seg.text if hasattr(seg, 'text') else seg.get('text', ''),
                    "speaker": seg.speaker if hasattr(seg, 'speaker') else seg.get('speaker', ''),
                    "confidence": seg.confidence if hasattr(seg, 'confidence') else seg.get('confidence', 1.0)
                } for seg in self.transcript
            ],
            "entities": [
                {
                    "name": ent.name,
                    "type": ent.type,
                    "mentions": ent.mentions,
                    "confidence": ent.confidence,
                    "description": ent.description
                } for ent in self.entities
            ],
            "claims": [
                {
                    "text": claim.text,
                    "timestamp": claim.timestamp,
                    "confidence": claim.confidence,
                    "context": claim.context,
                    "is_factual": claim.is_factual,
                    "evidence": claim.evidence,
                    "corrections": claim.corrections
                } for claim in self.claims
            ],
            "ocr_results": [
                {
                    "text": ocr.text,
                    "timestamp": ocr.timestamp,
                    "confidence": ocr.confidence,
                    "bounding_box": ocr.bounding_box,
                    "context": ocr.context
                } for ocr in self.ocr_results
            ],
            "web_research_facts": [
                {
                    "original_claim": fact.original_claim,
                    "corrected_info": fact.corrected_info,
                    "sources": fact.sources,
                    "confidence": fact.confidence,
                    "research_timestamp": fact.research_timestamp.isoformat(),
                    "is_correction": fact.is_correction
                } for fact in self.web_research_facts
            ],
            "quality_scores": {
                "content_accuracy": self.quality_scores.content_accuracy,
                "technical_depth": self.quality_scores.technical_depth,
                "educational_value": self.quality_scores.educational_value,
                "source_credibility": self.quality_scores.source_credibility,
                "completeness": self.quality_scores.completeness,
                "overall": self.quality_scores.overall
            },
            "content_outline": {
                "main_topic": self.content_outline.main_topic,
                "subtopics": self.content_outline.subtopics,
                "key_concepts": self.content_outline.key_concepts,
                "learning_objectives": self.content_outline.learning_objectives,
                "prerequisites": self.content_outline.prerequisites,
                "difficulty_level": self.content_outline.difficulty_level
            },
            "citations": self.citations,
            "content_hash": self.content_hash,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "gemini_model": self.gemini_model,
            "processing_time": self.processing_time
        }

@dataclass
class ImagePlan:
    """Plan for generating images/diagrams."""
    image_type: str  # "flowchart", "diagram", "sequence", "architecture", "chart"
    description: str
    placement_section: str  # Which section to place the image in
    prompt: str  # Detailed prompt for image generation
    priority: int = 1  # 1-5, higher is more important

@dataclass
class ClaudeOutput:
    """Output from Claude textbook authoring."""
    markdown_content: str
    image_plans: List[ImagePlan] = field(default_factory=list)
    sections_count: int = 0
    word_count: int = 0
    estimated_reading_time: int = 0  # minutes
    
    def __post_init__(self):
        """Calculate derived fields."""
        self.word_count = len(self.markdown_content.split())
        self.sections_count = self.markdown_content.count('##')
        self.estimated_reading_time = max(1, self.word_count // 200)  # ~200 WPM

@dataclass
class GeneratedImage:
    """A generated image/diagram."""
    image_plan: ImagePlan
    image_url: str
    image_data: Optional[bytes] = None
    generation_timestamp: datetime = field(default_factory=datetime.now)
    alt_text: str = ""

@dataclass
class NotionPayload:
    """Final Notion API payload."""
    properties: Dict[str, Any]
    content_blocks: List[Dict[str, Any]]
    
    def to_notion_request(self, database_id: str) -> Dict[str, Any]:
        """Convert to Notion API request format."""
        return {
            "parent": {"database_id": database_id},
            "properties": self.properties,
            "children": self.content_blocks
        }

@dataclass
class ProcessingResult:
    """Final result of the entire processing pipeline."""
    gemini_analysis: GeminiAnalysis
    claude_output: ClaudeOutput
    generated_images: List[GeneratedImage] = field(default_factory=list)
    notion_payload: Optional[NotionPayload] = None
    notion_page_url: str = ""
    processing_success: bool = True
    error_message: str = ""
    total_processing_time: float = 0.0