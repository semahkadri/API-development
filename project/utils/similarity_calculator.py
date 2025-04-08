from typing import Dict, List, Set
import nltk
from nltk.tokenize import word_tokenize
import logging
from collections import Counter
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize NLTK resources
nltk.download('punkt', quiet=True)

def preprocess_text(text: str) -> List[str]:
    """Preprocess text by tokenizing, keeping all meaningful words.

    Args:
        text: Input text string.

    Returns:
        List[str]: List of processed words.
    """
    try:
        if not text or not text.strip():
            logger.warning("Empty or whitespace-only text provided for preprocessing")
            return []

        tokens = word_tokenize(text.lower())
        processed = [word for word in tokens if word.isalnum() or word.isdigit()]
        logger.debug(f"Raw text: {text[:200]}")
        logger.debug(f"Preprocessed tokens: {processed}")
        logger.debug(f"Total processed tokens: {len(processed)}")
        if not processed:
            logger.warning("No tokens remaining after preprocessing")
        return processed
    except Exception as e:
        logger.error(f"Error preprocessing text: {str(e)}")
        return []

def create_word_vector(text: List[str]) -> Dict[str, int]:
    """Create a word frequency vector from processed text.

    Args:
        text: List of processed words.

    Returns:
        Dict[str, int]: Dictionary with words as keys and frequencies as values.
    """
    try:
        if not text:
            logger.warning("Empty text provided for vector creation")
            return {}
        vector = Counter(text)
        logger.debug(f"Word vector: {dict(vector)}")
        return vector
    except Exception as e:
        logger.error(f"Error creating word vector: {str(e)}")
        return {}

def cosine_similarity(vector1: Dict[str, int], vector2: Dict[str, int]) -> float:
    """Calculate cosine similarity between two word frequency vectors.

    Args:
        vector1: First word frequency vector.
        vector2: Second word frequency vector.

    Returns:
        float: Cosine similarity value between 0 and 1.
    """
    try:
        if not vector1 or not vector2:
            logger.warning("One or both vectors are empty; returning 0 similarity")
            return 0.0

        all_words: Set[str] = set(vector1.keys()).union(set(vector2.keys()))
        if not all_words:
            logger.warning("No words in combined vocabulary; returning 0 similarity")
            return 0.0

        v1 = [vector1.get(word, 0) for word in all_words]
        v2 = [vector2.get(word, 0) for word in all_words]

        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        logger.debug(f"Vector 1 values: {v1}")
        logger.debug(f"Vector 2 values: {v2}")
        logger.debug(f"Dot product: {dot_product}, Norm1: {norm1}, Norm2: {norm2}")

        if norm1 == 0 or norm2 == 0:
            logger.warning("One or both vectors have zero magnitude; returning 0 similarity")
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        logger.debug(f"Cosine similarity calculated: {similarity}")
        return similarity
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {str(e)}")
        return 0.0

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings.

    Args:
        s1: First string.
        s2: Second string.

    Returns:
        int: Number of single-character edits required.
    """
    try:
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        distance = previous_row[-1]
        logger.debug(f"Levenshtein distance calculated: {distance}")
        return distance
    except Exception as e:
        logger.error(f"Error calculating Levenshtein distance: {str(e)}")
        return -1

def jaccard_index(set1: Set[str], set2: Set[str]) -> float:
    """Calculate Jaccard Index between two sets of words.

    Args:
        set1: First set of words.
        set2: Second set of words.

    Returns:
        float: Jaccard Index value between 0 and 1.
    """
    try:
        if not set1 or not set2:
            logger.warning("One or both sets are empty; returning 0 similarity")
            return 0.0

        intersection = set1.intersection(set2)
        union = set1.union(set2)
        if not union:
            logger.warning("No union of sets; returning 0 similarity")
            return 0.0

        index = len(intersection) / len(union)
        logger.debug(f"Jaccard Index: {index}, Intersection: {intersection}, Union: {union}")
        return index
    except Exception as e:
        logger.error(f"Error calculating Jaccard Index: {str(e)}")
        return 0.0

def calculate_similarities(job_text: str, cv_text: str) -> Dict[str, float]:
    """Calculate all similarities between job description and CV.

    Args:
        job_text: Text from a job description.
        cv_text: Text from a CV.

    Returns:
        Dict[str, float]: Dictionary with cosine similarity, Levenshtein distance, and Jaccard Index.
    """
    try:
        logger.debug(f"Input job text: {job_text}")
        logger.debug(f"Input CV text: {cv_text}")

        # Preprocess texts
        job_words = preprocess_text(job_text)
        cv_words = preprocess_text(cv_text)

        # Create word vectors and sets
        job_vector = create_word_vector(job_words)
        cv_vector = create_word_vector(cv_words)
        job_set = set(job_words)
        cv_set = set(cv_words)

        # Log vectors and sets
        logger.debug(f"Job vector: {job_vector}")
        logger.debug(f"CV vector: {cv_vector}")
        logger.debug(f"Job set: {job_set}")
        logger.debug(f"CV set: {cv_set}")

        # Calculate similarities
        cosine_sim = cosine_similarity(job_vector, cv_vector)
        levenshtein_dist = float(levenshtein_distance(job_text, cv_text))
        jaccard_idx = jaccard_index(job_set, cv_set)

        result = {
            "cosine_similarity": cosine_sim,
            "levenshtein_distance": levenshtein_dist,
            "jaccard_index": jaccard_idx
        }
        logger.info(f"Similarity results: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in similarity calculations: {str(e)}")
        return {
            "cosine_similarity": 0.0,
            "levenshtein_distance": -1.0,
            "jaccard_index": 0.0
        }