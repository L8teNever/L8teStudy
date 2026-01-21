"""
Drive Search Service für L8teStudy
Volltextsuche in Drive-Dateien mit SQLite FTS5
"""

from typing import List, Dict, Optional
from sqlalchemy import text
from flask import current_app
from . import db
from .models import DriveFile, DriveFileContent, DriveFolder, User, Subject


class DriveSearchService:
    """
    Drive Search Service
    
    Features:
    - Volltextsuche mit SQLite FTS5
    - Filter nach Fach, Benutzer, Datum
    - Ranking nach Relevanz
    - Snippet-Extraktion
    - Privacy-Level Berücksichtigung
    """
    
    def __init__(self, current_user_id: Optional[int] = None, class_id: Optional[int] = None):
        """
        Initialisiert den Search Service
        
        Args:
            current_user_id: ID des aktuellen Benutzers
            class_id: ID der Klasse
        """
        self.current_user_id = current_user_id
        self.class_id = class_id
    
    def ensure_fts_table(self):
        """
        Stellt sicher, dass die FTS5-Tabelle existiert
        """
        try:
            # Create FTS5 virtual table if it doesn't exist
            db.session.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS drive_file_content_fts
                USING fts5(
                    content_text,
                    content='drive_file_content',
                    content_rowid='id'
                )
            """))
            
            # Create triggers to keep FTS table in sync
            db.session.execute(text("""
                CREATE TRIGGER IF NOT EXISTS drive_file_content_ai
                AFTER INSERT ON drive_file_content
                BEGIN
                    INSERT INTO drive_file_content_fts(rowid, content_text)
                    VALUES (new.id, new.content_text);
                END
            """))
            
            db.session.execute(text("""
                CREATE TRIGGER IF NOT EXISTS drive_file_content_ad
                AFTER DELETE ON drive_file_content
                BEGIN
                    DELETE FROM drive_file_content_fts WHERE rowid = old.id;
                END
            """))
            
            db.session.execute(text("""
                CREATE TRIGGER IF NOT EXISTS drive_file_content_au
                AFTER UPDATE ON drive_file_content
                BEGIN
                    DELETE FROM drive_file_content_fts WHERE rowid = old.id;
                    INSERT INTO drive_file_content_fts(rowid, content_text)
                    VALUES (new.id, new.content_text);
                END
            """))
            
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Failed to create FTS table: {e}")
            db.session.rollback()
    
    def rebuild_fts_index(self):
        """
        Baut den FTS-Index neu auf
        """
        try:
            # Delete all FTS entries
            db.session.execute(text("DELETE FROM drive_file_content_fts"))
            
            # Rebuild from drive_file_content
            db.session.execute(text("""
                INSERT INTO drive_file_content_fts(rowid, content_text)
                SELECT id, content_text FROM drive_file_content
            """))
            
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Failed to rebuild FTS index: {e}")
            db.session.rollback()
            raise
    
    def search(
        self,
        query: str,
        subject_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Sucht in Drive-Dateien (Inhalt, Dateiname, Fach, Username)
        """
        if not query or len(query.strip()) < 2:
            return []
        
        try:
            # Ensure FTS table exists
            self.ensure_fts_table()
            
            # Build privacy filter
            privacy_filter = ""
            if self.current_user_id:
                privacy_filter = "AND (dfolder.user_id = :current_user_id OR dfolder.privacy_level = 'public')"
            else:
                privacy_filter = "AND dfolder.privacy_level = 'public'"
            
            # Build subject filter
            subject_filter = ""
            if subject_id:
                subject_filter = f"AND df.subject_id = {subject_id}"
            
            # Build user filter
            user_filter = ""
            if user_id:
                user_filter = f"AND dfolder.user_id = {user_id}"
            
            # Prepare search parameters
            like_query = f'%{query}%'
            
            # Try FTS search first
            fts_results = []
            try:
                fts_sql = f"""
                    SELECT DISTINCT
                        df.id,
                        df.filename,
                        COALESCE(snippet(drive_file_content_fts, 0, '<mark>', '</mark>', '...', 32), '...') as snippet,
                        bm25(drive_file_content_fts) as rank,
                        u.id as user_id,
                        u.username,
                        s.id as subject_id,
                        s.name as subject_name,
                        df.file_size,
                        COALESCE(dfc.page_count, 0) as page_count,
                        df.created_at,
                        df.parent_folder_name,
                        dfolder.folder_name
                    FROM drive_file_content_fts fts
                    JOIN drive_file_content dfc ON fts.rowid = dfc.id
                    JOIN drive_file df ON dfc.drive_file_id = df.id
                    JOIN drive_folder dfolder ON df.drive_folder_id = dfolder.id
                    JOIN user u ON dfolder.user_id = u.id
                    LEFT JOIN subject s ON df.subject_id = s.id
                    WHERE fts MATCH :fts_query
                    {privacy_filter}
                    {subject_filter}
                    {user_filter}
                    ORDER BY rank
                    LIMIT :limit
                """
                
                fts_query_param = f'"{query}"*'
                fts_results = db.session.execute(text(fts_sql), {
                    'fts_query': fts_query_param,
                    'current_user_id': self.current_user_id,
                    'limit': limit
                }).fetchall()
            except Exception as fts_error:
                current_app.logger.warning(f"FTS search failed, falling back to LIKE: {fts_error}")
            
            # Metadata search (filename, subject, username)
            meta_sql = f"""
                SELECT DISTINCT
                    df.id,
                    df.filename,
                    'Treffer im Titel/Fach/User' as snippet,
                    -10.0 as rank,
                    u.id as user_id,
                    u.username,
                    s.id as subject_id,
                    s.name as subject_name,
                    df.file_size,
                    COALESCE(dfc.page_count, 0) as page_count,
                    df.created_at,
                    df.parent_folder_name,
                    dfolder.folder_name
                FROM drive_file df
                JOIN drive_folder dfolder ON df.drive_folder_id = dfolder.id
                JOIN user u ON dfolder.user_id = u.id
                LEFT JOIN subject s ON df.subject_id = s.id
                LEFT JOIN drive_file_content dfc ON df.id = dfc.drive_file_id
                WHERE (
                    df.filename LIKE :like_query 
                    OR s.name LIKE :like_query 
                    OR u.username LIKE :like_query
                )
                {privacy_filter}
                {subject_filter}
                {user_filter}
                LIMIT :limit
            """
            
            meta_results = db.session.execute(text(meta_sql), {
                'like_query': like_query,
                'current_user_id': self.current_user_id,
                'limit': limit
            }).fetchall()
            
            # Combine results and deduplicate by file ID
            seen_ids = set()
            combined_results = []
            
            # Add FTS results first (higher priority)
            for row in fts_results:
                if row[0] not in seen_ids:
                    seen_ids.add(row[0])
                    combined_results.append(row)
            
            # Add metadata results
            for row in meta_results:
                if row[0] not in seen_ids:
                    seen_ids.add(row[0])
                    combined_results.append(row)
            
            # Format results
            formatted_results = []
            for row in combined_results[:limit]:
                formatted_results.append({
                    'id': row[0],
                    'file_id': row[0],
                    'filename': row[1],
                    'snippet': row[2],
                    'rank': float(row[3]) if row[3] is not None else 0.0,
                    'user_id': row[4],
                    'owner_username': row[5],
                    'subject_id': row[6],
                    'subject_name': row[7],
                    'file_size': row[8],
                    'page_count': row[9],
                    'created_at': row[10].isoformat() if row[10] else None,
                    'parent_folder_name': row[11],
                    'folder_name': row[12]
                })
            
            return formatted_results
            
        except Exception as e:
            current_app.logger.error(f"Search failed completely: {e}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return []
    
    def _build_search_query(
        self,
        query: str,
        subject_id: Optional[int],
        user_id: Optional[int],
        limit: int,
        offset: int
    ) -> str:
        """
        Legacy method - kept for compatibility
        """
        return ""
    
    def get_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """
        Gibt Autocomplete-Vorschläge
        
        Args:
            query: Suchbegriff
            limit: Maximale Anzahl Vorschläge
        
        Returns:
            Liste von Vorschlägen
        """
        if not query or len(query.strip()) < 2:
            return []
        
        # Simple implementation: return matching filenames
        try:
            results = DriveFile.query.filter(
                DriveFile.filename.ilike(f'%{query}%')
            ).limit(limit).all()
            
            return [f.filename for f in results]
            
        except Exception as e:
            current_app.logger.error(f"Suggestions failed: {e}")
            return []
    
    def get_user_files(
        self,
        user_id: int,
        subject_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Holt alle Dateien eines Benutzers
        
        Args:
            user_id: Benutzer-ID
            subject_id: Optional - Filter nach Fach
            limit: Limit
            offset: Offset
        
        Returns:
            Liste von Dateien
        """
        query = db.session.query(
            DriveFile, DriveFolder, User, Subject, DriveFileContent
        ).join(
            DriveFolder, DriveFile.drive_folder_id == DriveFolder.id
        ).join(
            User, DriveFolder.user_id == User.id
        ).outerjoin(
            Subject, DriveFile.subject_id == Subject.id
        ).outerjoin(
            DriveFileContent, DriveFile.id == DriveFileContent.drive_file_id
        ).filter(
            DriveFolder.user_id == user_id
        )
        
        # Privacy check
        if self.current_user_id and self.current_user_id != user_id:
            query = query.filter(DriveFolder.privacy_level == 'public')
        
        # Subject filter
        if subject_id:
            query = query.filter(DriveFile.subject_id == subject_id)
        
        # Order and limit
        query = query.order_by(DriveFile.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        results = query.all()
        
        # Format results
        formatted = []
        for df, dfolder, u, s, dfc in results:
            formatted.append({
                'file_id': df.id,
                'filename': df.filename,
                'user_id': u.id,
                'username': u.username,
                'subject_id': s.id if s else None,
                'subject_name': s.name if s else None,
                'file_size': df.file_size,
                'page_count': dfc.page_count if dfc else 0,
                'created_at': df.created_at.isoformat() if df.created_at else None,
                'privacy_level': dfolder.privacy_level
            })
        
        return formatted
    
    def get_file_stats(self) -> Dict:
        """
        Holt Statistiken über Drive-Dateien
        
        Returns:
            Dictionary mit Statistiken
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'total_pages': 0,
            'files_by_subject': {},
            'files_by_user': {}
        }
        
        try:
            # Total files
            stats['total_files'] = DriveFile.query.count()
            
            # Total size
            result = db.session.query(
                db.func.sum(DriveFile.file_size)
            ).scalar()
            stats['total_size'] = result or 0
            
            # Total pages
            result = db.session.query(
                db.func.sum(DriveFileContent.page_count)
            ).scalar()
            stats['total_pages'] = result or 0
            
            # Files by subject
            results = db.session.query(
                Subject.name,
                db.func.count(DriveFile.id)
            ).join(
                DriveFile, Subject.id == DriveFile.subject_id
            ).group_by(Subject.name).all()
            
            stats['files_by_subject'] = {name: count for name, count in results}
            
            # Files by user
            results = db.session.query(
                User.username,
                db.func.count(DriveFile.id)
            ).join(
                DriveFolder, User.id == DriveFolder.user_id
            ).join(
                DriveFile, DriveFolder.id == DriveFile.drive_folder_id
            ).group_by(User.username).all()
            
            stats['files_by_user'] = {name: count for name, count in results}
            
        except Exception as e:
            current_app.logger.error(f"Failed to get file stats: {e}")
        
        return stats


# Utility function
def get_drive_search_service(
    current_user_id: Optional[int] = None,
    class_id: Optional[int] = None
) -> DriveSearchService:
    """
    Get a Drive Search Service instance
    
    Args:
        current_user_id: Current user ID
        class_id: Class ID
    
    Returns:
        DriveSearchService instance
    """
    return DriveSearchService(current_user_id=current_user_id, class_id=class_id)
