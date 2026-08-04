"""News deduplication using hash and similarity."""

import hashlib
from typing import List, Optional, Tuple

from petro.core import get_logger

logger = get_logger(__name__)


class NewsDeduplicator:
    """Deduplicates news articles using hash-based and similarity-based methods."""

    @staticmethod
    def hash_title(title: str) -> str:
        """Generate hash of title for quick deduplication.

        Args:
            title: News title

        Returns:
            SHA256 hash of title
        """
        normalized = title.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()

    @staticmethod
    def levenshtein_distance(s1: str, s2: str, max_distance: Optional[int] = None) -> int:
        """Calculate Levenshtein distance between two strings.

        Args:
            s1: First string
            s2: Second string
            max_distance: Early termination if distance exceeds this

        Returns:
            Levenshtein distance
        """
        if len(s1) < len(s2):
            return NewsDeduplicator.levenshtein_distance(s2, s1, max_distance)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row = [i + 1]

            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))

            # Early termination
            if max_distance and min(current_row) > max_distance:
                return max_distance + 1

            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def similarity_score(s1: str, s2: str) -> float:
        """Calculate similarity score between 0 and 1.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score (0=completely different, 1=identical)
        """
        s1_lower = s1.lower()
        s2_lower = s2.lower()

        if s1_lower == s2_lower:
            return 1.0

        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 0.0

        distance = NewsDeduplicator.levenshtein_distance(s1_lower, s2_lower)
        return 1.0 - (distance / max_len)

    @staticmethod
    def is_duplicate(title1: str, title2: str, threshold: float = 0.85) -> bool:
        """Check if two titles are duplicates.

        Args:
            title1: First title
            title2: Second title
            threshold: Similarity threshold (0-1)

        Returns:
            True if articles are likely duplicates
        """
        score = NewsDeduplicator.similarity_score(title1, title2)
        return score >= threshold

    @staticmethod
    def find_duplicates_in_batch(titles: List[str], threshold: float = 0.85) -> List[Tuple[int, int, float]]:
        """Find duplicate pairs in a batch of titles.

        Args:
            titles: List of titles
            threshold: Similarity threshold

        Returns:
            List of (idx1, idx2, score) tuples for duplicates found
        """
        duplicates = []

        for i in range(len(titles)):
            for j in range(i + 1, len(titles)):
                score = NewsDeduplicator.similarity_score(titles[i], titles[j])
                if score >= threshold:
                    duplicates.append((i, j, score))

        return duplicates

    @staticmethod
    def deduplicate_batch(titles: List[str], threshold: float = 0.85) -> Tuple[List[str], List[int]]:
        """Remove duplicates from batch, keeping first occurrence.

        Args:
            titles: List of titles
            threshold: Similarity threshold

        Returns:
            Tuple of (unique_titles, kept_indices)
        """
        duplicates = NewsDeduplicator.find_duplicates_in_batch(titles, threshold)

        # Mark indices to remove
        to_remove = set()
        for idx1, idx2, score in duplicates:
            # Keep first, mark second for removal
            to_remove.add(idx2)

        # Build result
        unique = []
        indices = []
        for i, title in enumerate(titles):
            if i not in to_remove:
                unique.append(title)
                indices.append(i)

        return unique, indices
