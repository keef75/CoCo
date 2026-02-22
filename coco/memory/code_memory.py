"""
Persistent code library and computational memory system.

Stores successful code snippets and reusable functions in a local SQLite
database for recall across sessions. Standalone module with minimal
dependencies (sqlite3, pathlib, hashlib).

Extracted from the monolithic cocoa.py CodeMemory class.
"""

import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional


class CodeMemory:
    """Persistent code library and computational memory system"""

    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.code_library = workspace / "code_library"
        self.code_library.mkdir(exist_ok=True)

        # Initialize code memory database
        self.memory_db = workspace / "code_memory.db"
        self.init_code_memory()

    def init_code_memory(self):
        """Initialize code memory database"""
        self.conn = sqlite3.connect(self.memory_db)

        # Store successful code snippets
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS code_snippets (
                id INTEGER PRIMARY KEY,
                language TEXT,
                purpose TEXT,
                code_hash TEXT UNIQUE,
                code_content TEXT,
                execution_count INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 1.0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')

        # Store useful functions
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS functions_library (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                language TEXT,
                description TEXT,
                code_content TEXT,
                parameters TEXT,
                return_type TEXT,
                usage_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def store_successful_code(self, code: str, language: str, purpose: str = "general") -> str:
        """Store successful code execution for future reference"""
        code_hash = hashlib.md5(code.encode()).hexdigest()

        try:
            self.conn.execute('''
                UPDATE code_snippets
                SET execution_count = execution_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE code_hash = ?
            ''', (code_hash,))

            if self.conn.execute(
                "SELECT changes()"
            ).fetchone()[0] == 0:
                self.conn.execute('''
                    INSERT INTO code_snippets (language, purpose, code_hash, code_content)
                    VALUES (?, ?, ?, ?)
                ''', (language, purpose, code_hash, code))

            self.conn.commit()
            return f"Code stored in memory library (hash: {code_hash[:8]})"

        except Exception as e:
            return f"Failed to store code: {e}"

    def find_similar_code(self, purpose: str, language: str = None) -> List[dict]:
        """Find similar code snippets for a given purpose"""
        query = '''
            SELECT code_content, language, purpose, execution_count, success_rate
            FROM code_snippets
            WHERE purpose LIKE ?
        '''
        params: list = [f"%{purpose}%"]

        if language:
            query += " AND language = ?"
            params.append(language)

        query += " ORDER BY success_rate DESC, execution_count DESC LIMIT 5"

        cursor = self.conn.execute(query, params)
        results = []

        for row in cursor.fetchall():
            results.append({
                "code": row[0],
                "language": row[1],
                "purpose": row[2],
                "usage": row[3],
                "success_rate": row[4]
            })

        return results

    def save_function(
        self,
        name: str,
        code: str,
        language: str,
        description: str,
        parameters: str = "",
        return_type: str = "",
    ) -> str:
        """Save a reusable function to the library"""
        try:
            self.conn.execute('''
                INSERT OR REPLACE INTO functions_library
                (name, language, description, code_content, parameters, return_type)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (name, language, description, code, parameters, return_type),
            )

            func_file = self.code_library / f"{name}_{language}.txt"
            func_content = (
                f"# {name} ({language})\n"
                f"# Description: {description}\n"
                f"# Parameters: {parameters}\n"
                f"# Returns: {return_type}\n\n"
                f"{code}\n"
            )
            func_file.write_text(func_content)

            self.conn.commit()
            return f"Function '{name}' saved to library"

        except Exception as e:
            return f"Failed to save function: {e}"

    def get_function(self, name: str) -> Optional[dict]:
        """Retrieve a function from the library"""
        cursor = self.conn.execute('''
            SELECT name, language, description, code_content, parameters, return_type
            FROM functions_library
            WHERE name = ?
        ''', (name,))

        result = cursor.fetchone()
        if result:
            return {
                "name": result[0],
                "language": result[1],
                "description": result[2],
                "code": result[3],
                "parameters": result[4],
                "return_type": result[5]
            }
        return None

    def list_functions(self, language: str = None) -> List[dict]:
        """List all functions in the library"""
        query = "SELECT name, language, description, usage_count FROM functions_library"
        params: list = []

        if language:
            query += " WHERE language = ?"
            params.append(language)

        query += " ORDER BY usage_count DESC"

        cursor = self.conn.execute(query, params)
        results = []

        for row in cursor.fetchall():
            results.append({
                "name": row[0],
                "language": row[1],
                "description": row[2],
                "usage": row[3]
            })

        return results

    def get_memory_stats(self) -> dict:
        """Get statistics about code memory"""
        stats: Dict = {}

        cursor = self.conn.execute('''
            SELECT
                COUNT(*) as total_snippets,
                COUNT(DISTINCT language) as languages,
                AVG(success_rate) as avg_success_rate
            FROM code_snippets
        ''')
        row = cursor.fetchone()
        stats["snippets"] = {
            "total": row[0],
            "languages": row[1],
            "avg_success_rate": row[2] or 0.0
        }

        cursor = self.conn.execute('''
            SELECT COUNT(*) as total_functions, SUM(usage_count) as total_usage
            FROM functions_library
        ''')
        row = cursor.fetchone()
        stats["functions"] = {
            "total": row[0],
            "total_usage": row[1] or 0
        }

        return stats
