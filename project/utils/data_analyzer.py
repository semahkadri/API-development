from typing import List, Tuple, Dict, Optional, Union
import nltk
from collections import Counter
import plotly.graph_objects as go
import logging
import config
import os

logger = logging.getLogger(__name__)

def initialize_nltk_resources() -> None:
    """Initialize NLTK resources by downloading required datasets.

    Ensures stopwords and punkt_tab are available for text analysis.

    Raises:
        Exception: If resource download fails.
    """
    try:
        config.configure_dependencies()
        logger.debug("NLTK resources initialized successfully")
    except Exception as e:
        logger.error(f"Failed to configure dependencies: {str(e)}")
        try:
            nltk.download("stopwords", quiet=False)
            logger.info("Fallback: Downloaded stopwords directly")
        except Exception as download_error:
            logger.error(f"Failed to download stopwords: {str(download_error)}")
            raise

initialize_nltk_resources()

def analyze_text(text_data: List[str]) -> Dict[str, Union[List[Tuple[str, int]], Dict[str, float]]]:
    """Analyze textual data to extract word frequency and basic statistics, excluding numbers.

    Args:
        text_data: List of text strings from job descriptions.

    Returns:
        Dictionary containing top words and data understanding statistics.
    """
    try:
        all_text = " ".join(text_data)
        stop_words = set(nltk.corpus.stopwords.words("english"))
        words = nltk.word_tokenize(all_text.lower())
        filtered_words = [word for word in words if word.isalpha() and word not in stop_words]
        word_freq = Counter(filtered_words)
        top_words = word_freq.most_common(20)

        total_docs = len(text_data)
        total_words = len(words)
        unique_words = len(set(words))
        avg_words_per_doc = total_words / total_docs if total_docs > 0 else 0

        stats = {
            "total_documents": total_docs,
            "total_words": total_words,
            "unique_words": unique_words,
            "average_words_per_document": avg_words_per_doc
        }

        logger.info("Text analysis completed with statistics")
        return {"top_words": top_words, "stats": stats}
    except Exception as e:
        logger.error(f"Error during text analysis: {str(e)}")
        return {"top_words": [], "stats": {}}

def generate_word_frequency_plot(top_words: List[Tuple[str, int]]) -> Optional[str]:
    """Generate a bar plot of word frequencies using Plotly and save it as HTML.

    Args:
        top_words: List of tuples with (word, frequency) pairs.

    Returns:
        Path to the saved HTML file or None if failed.
    """
    try:
        words = [word for word, _ in top_words]
        frequencies = [freq for _, freq in top_words]
        
        fig = go.Figure(data=[go.Bar(x=words, y=frequencies)])
        fig.update_layout(
            title="Top 20 Most Frequent Words in Job Descriptions",
            xaxis_title="Words",
            yaxis_title="Frequency"
        )
        
        output_path = os.path.join(config.UPLOAD_FOLDER, "word_frequency.html")
        fig.write_html(output_path)
        logger.info(f"Word frequency plot saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating plot: {str(e)}")
        return None