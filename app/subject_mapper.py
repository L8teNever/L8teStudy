"""
Subject Mapper für L8teStudy Drive Integration
Ordnet unordentliche Ordnernamen intelligenten offiziellen Fächern zu
"""

from typing import Optional, List, Tuple
from difflib import SequenceMatcher
from . import db
from .models import Subject, SubjectMapping


class SubjectMapper:
    """
    Intelligente Fach-Zuordnung
    
    Features:
    - Fuzzy-Matching für ähnliche Namen
    - Alias-System (Ph -> Physik)
    - Benutzer- und klassenspezifische Zuordnungen
    - Automatische Vorschläge
    """
    
    # Häufige Abkürzungen und Alias
    COMMON_ALIASES = {
        'ph': 'physik',
        'ma': 'mathematik',
        'mathe': 'mathematik',
        'de': 'deutsch',
        'en': 'englisch',
        'eng': 'englisch',
        'fr': 'französisch',
        'bio': 'biologie',
        'che': 'chemie',
        'chem': 'chemie',
        'geo': 'geographie',
        'gdt': 'grundlagen der technik',
        'technik': 'grundlagen der technik',
        'inf': 'informatik',
        'info': 'informatik',
        'sport': 'sport',
        'kunst': 'kunst',
        'musik': 'musik',
        'gesch': 'geschichte',
        'geschichte': 'geschichte',
        'powi': 'politik und wirtschaft',
        'politik': 'politik und wirtschaft',
        'reli': 'religion',
        'religion': 'religion',
        'ethik': 'ethik',
        'phil': 'philosophie',
        'philosophie': 'philosophie',
    }
    
    def __init__(self, class_id: Optional[int] = None, user_id: Optional[int] = None):
        """
        Initialisiert den Subject Mapper
        
        Args:
            class_id: Optional - Klassen-ID für klassenspezifische Zuordnungen
            user_id: Optional - Benutzer-ID für benutzerspezifische Zuordnungen
        """
        self.class_id = class_id
        self.user_id = user_id
    
    def normalize_name(self, name: str) -> str:
        """
        Normalisiert einen Fach-/Ordnernamen
        
        Args:
            name: Eingabename
        
        Returns:
            Normalisierter Name (lowercase, ohne Sonderzeichen)
        """
        # Lowercase
        normalized = name.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes = ['fach ', 'kurs ', 'lk ', 'gk ']
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        
        # Remove special characters (keep spaces and hyphens)
        import re
        normalized = re.sub(r'[^\w\s-]', '', normalized)
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def get_similarity(self, str1: str, str2: str) -> float:
        """
        Berechnet die Ähnlichkeit zwischen zwei Strings
        
        Args:
            str1: Erster String
            str2: Zweiter String
        
        Returns:
            Ähnlichkeit zwischen 0.0 und 1.0
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def find_existing_mapping(self, informal_name: str) -> Optional[Subject]:
        """
        Sucht nach einer existierenden Zuordnung
        
        Args:
            informal_name: Informeller Name (z.B. "Ph")
        
        Returns:
            Subject oder None
        """
        normalized = self.normalize_name(informal_name)
        
        # Check user-specific mapping first
        if self.user_id:
            mapping = SubjectMapping.query.filter_by(
                informal_name=normalized,
                user_id=self.user_id
            ).first()
            if mapping:
                return mapping.official_subject
        
        # Check class-specific mapping
        if self.class_id:
            mapping = SubjectMapping.query.filter_by(
                informal_name=normalized,
                class_id=self.class_id,
                is_global=True
            ).first()
            if mapping:
                return mapping.official_subject
        
        # Check global mapping
        mapping = SubjectMapping.query.filter_by(
            informal_name=normalized,
            is_global=True,
            class_id=None,
            user_id=None
        ).first()
        if mapping:
            return mapping.official_subject
        
        return None
    
    def map_folder_to_subject(self, folder_name: str, auto_create: bool = True) -> Optional[Subject]:
        """
        Ordnet einen Ordnernamen einem Fach zu
        
        Args:
            folder_name: Name des Ordners
            auto_create: Wenn True, erstellt automatisch eine Zuordnung
        
        Returns:
            Subject oder None
        """
        # Check existing mapping
        existing = self.find_existing_mapping(folder_name)
        if existing:
            return existing
        
        # Try to find subject by similarity
        subject = self.suggest_subject(folder_name)
        
        if subject and auto_create:
            # Create mapping
            self.create_mapping(folder_name, subject.id, auto_mapped=True)
        
        return subject
    
    def suggest_subject(self, informal_name: str) -> Optional[Subject]:
        """
        Schlägt ein Fach basierend auf dem Namen vor
        
        Args:
            informal_name: Informeller Name
        
        Returns:
            Subject oder None
        """
        normalized = self.normalize_name(informal_name)
        
        # Check common aliases
        if normalized in self.COMMON_ALIASES:
            canonical_name = self.COMMON_ALIASES[normalized]
            subject = self._find_subject_by_name(canonical_name)
            if subject:
                return subject
        
        # Get all subjects for the class
        subjects = self._get_available_subjects()
        
        if not subjects:
            return None
        
        # Find best match using fuzzy matching
        best_match = None
        best_score = 0.0
        
        for subject in subjects:
            subject_normalized = self.normalize_name(subject.name)
            
            # Exact match
            if normalized == subject_normalized:
                return subject
            
            # Fuzzy match
            score = self.get_similarity(normalized, subject_normalized)
            
            # Also check if informal name is contained in subject name
            if normalized in subject_normalized:
                score = max(score, 0.8)
            
            if score > best_score:
                best_score = score
                best_match = subject
        
        # Only return if similarity is high enough
        if best_score >= 0.6:
            return best_match
        
        return None
    
    def suggest_multiple(self, informal_name: str, limit: int = 5) -> List[Tuple[Subject, float]]:
        """
        Schlägt mehrere mögliche Fächer vor
        
        Args:
            informal_name: Informeller Name
            limit: Maximale Anzahl Vorschläge
        
        Returns:
            Liste von (Subject, similarity_score) Tupeln
        """
        normalized = self.normalize_name(informal_name)
        subjects = self._get_available_subjects()
        
        if not subjects:
            return []
        
        # Calculate scores for all subjects
        scores = []
        for subject in subjects:
            subject_normalized = self.normalize_name(subject.name)
            score = self.get_similarity(normalized, subject_normalized)
            
            # Boost score if informal name is contained
            if normalized in subject_normalized:
                score = max(score, 0.8)
            
            scores.append((subject, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top matches with score >= 0.3
        return [(s, score) for s, score in scores[:limit] if score >= 0.3]
    
    def create_mapping(
        self,
        informal_name: str,
        subject_id: int,
        auto_mapped: bool = False,
        is_global: bool = False
    ) -> SubjectMapping:
        """
        Erstellt eine neue Fach-Zuordnung
        
        Args:
            informal_name: Informeller Name
            subject_id: ID des offiziellen Fachs
            auto_mapped: Wurde automatisch zugeordnet?
            is_global: Gilt für alle Benutzer?
        
        Returns:
            SubjectMapping
        """
        normalized = self.normalize_name(informal_name)
        
        # Check if mapping already exists
        existing = SubjectMapping.query.filter_by(
            informal_name=normalized,
            class_id=self.class_id if is_global else None,
            user_id=self.user_id if not is_global else None
        ).first()
        
        if existing:
            # Update existing
            existing.subject_id = subject_id
            db.session.commit()
            return existing
        
        # Create new mapping
        mapping = SubjectMapping(
            informal_name=normalized,
            subject_id=subject_id,
            class_id=self.class_id if is_global else None,
            user_id=self.user_id if not is_global else None,
            is_global=is_global
        )
        
        db.session.add(mapping)
        db.session.commit()
        
        return mapping
    
    def delete_mapping(self, mapping_id: int) -> bool:
        """
        Löscht eine Fach-Zuordnung
        
        Args:
            mapping_id: ID der Zuordnung
        
        Returns:
            True wenn erfolgreich gelöscht
        """
        mapping = SubjectMapping.query.get(mapping_id)
        if not mapping:
            return False
        
        # Check permissions
        if mapping.user_id and mapping.user_id != self.user_id:
            return False
        
        db.session.delete(mapping)
        db.session.commit()
        return True
    
    def _get_available_subjects(self) -> List[Subject]:
        """
        Holt alle verfügbaren Fächer für die Klasse
        
        Returns:
            Liste von Subject-Objekten
        """
        if self.class_id:
            from .models import SchoolClass
            school_class = SchoolClass.query.get(self.class_id)
            if school_class:
                return list(school_class.subjects)
        
        # Fallback: All subjects
        return Subject.query.all()
    
    def _find_subject_by_name(self, name: str) -> Optional[Subject]:
        """
        Findet ein Fach anhand des Namens
        
        Args:
            name: Fachname
        
        Returns:
            Subject oder None
        """
        normalized = self.normalize_name(name)
        
        # Get available subjects
        subjects = self._get_available_subjects()
        
        for subject in subjects:
            if self.normalize_name(subject.name) == normalized:
                return subject
        
        return None


# Utility function
def get_subject_mapper(class_id: Optional[int] = None, user_id: Optional[int] = None) -> SubjectMapper:
    """
    Get a Subject Mapper instance
    
    Args:
        class_id: Optional class ID
        user_id: Optional user ID
    
    Returns:
        SubjectMapper instance
    """
    return SubjectMapper(class_id=class_id, user_id=user_id)
