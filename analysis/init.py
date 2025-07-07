# Analysis package initialization
# This makes the analysis directory a Python package

from .text_analysis import (
    perform_realistic_unified_text_analysis,
    perform_basic_text_analysis,
    perform_advanced_text_analysis
)

from .news_analysis import (
    perform_basic_news_analysis,
    perform_advanced_news_analysis,
    perform_realistic_unified_news_check
)

from .image_analysis import (
    perform_realistic_image_analysis,
    perform_basic_image_analysis
)

from .speech_analysis import (
    extract_claims_from_speech,
    speech_to_text,
    stream_transcript,
    batch_factcheck,
    get_youtube_transcript,
    export_speech_report
)

__all__ = [
    'perform_realistic_unified_text_analysis',
    'perform_basic_text_analysis',
    'perform_advanced_text_analysis',
    'perform_basic_news_analysis',
    'perform_advanced_news_analysis',
    'perform_realistic_unified_news_check',
    'perform_realistic_image_analysis',
    'perform_basic_image_analysis',
    'extract_claims_from_speech',
    'speech_to_text',
    'stream_transcript',
    'batch_factcheck',
    'get_youtube_transcript',
    'export_speech_report'
]
