#!/usr/bin/env python3
"""
Norns documentation manager.
Handles downloading, caching, and searching Norns documentation.
"""

import os
import sys
import json
import time
import asyncio
import logging
import re
import sqlite3
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from datetime import datetime, timedelta

import aiohttp
from bs4 import BeautifulSoup
import markdown
from rich.console import Console
from rich.markdown import Markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("norns_docs")

# Documentation sources
DOCS_SOURCES = {
    "norns": "https://monome.org/docs/norns/",
    "api": "https://monome.org/docs/norns/api/",
    "studies": "https://monome.org/docs/norns/studies/",
    "reference": "https://monome.org/docs/norns/reference/",
    "help": "https://monome.org/docs/norns/help/",
    "maiden": "https://monome.org/docs/norns/maiden/",
    "play": "https://monome.org/docs/norns/play/",
    "scripting": "https://monome.org/docs/norns/scripting/",
    "handbook": "https://monome.org/docs/norns/handbook/",
}

# Extension to document type mapping
EXTENSION_MAP = {
    ".lua": "lua",
    ".sc": "supercollider",
    ".md": "markdown",
    ".html": "html",
    ".txt": "text",
}


class NornsDocsManager:
    """
    Manages Norns documentation.
    Handles downloading, caching, and searching documentation from monome.org.
    """
    
    def __init__(self, cache_dir: str = None, refresh_days: int = 7):
        """
        Initialize the documentation manager.
        
        Args:
            cache_dir: Directory to cache documentation (defaults to ~/.norns-cli/docs)
            refresh_days: Number of days after which to refresh the cache
        """
        self.refresh_days = refresh_days
        
        # Set up cache directory
        if cache_dir is None:
            home_dir = os.path.expanduser("~")
            self.cache_dir = os.path.join(home_dir, ".norns-cli", "docs")
        else:
            self.cache_dir = cache_dir
            
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Database path
        self.db_path = os.path.join(self.cache_dir, "docs.db")
        
        # Initialize database
        self._init_db()
        
        # Console for rich output
        self.console = Console()
    
    def _init_db(self):
        """Initialize the SQLite database for documentation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS docs (
            id INTEGER PRIMARY KEY,
            category TEXT,
            title TEXT,
            url TEXT,
            content TEXT,
            html_content TEXT,
            last_updated TIMESTAMP,
            UNIQUE(url)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_functions (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category TEXT,
            description TEXT,
            signature TEXT,
            parameters TEXT,
            return_value TEXT,
            example TEXT,
            source_url TEXT,
            UNIQUE(name, category)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS engines (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            parameters TEXT,
            commands TEXT,
            example TEXT,
            source_url TEXT,
            UNIQUE(name)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_status (
            category TEXT PRIMARY KEY,
            last_sync TIMESTAMP,
            status TEXT
        )
        ''')
        
        # Create full-text search index
        cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
            title, content, category, url
        )
        ''')
        
        conn.commit()
        conn.close()
    
    async def sync_documentation(self, force: bool = False) -> bool:
        """
        Synchronize documentation from monome.org.
        
        Args:
            force: Force refresh even if cache is recent
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if we need to sync
            if not force and not self._needs_sync():
                logger.info("Documentation is up to date")
                return True
            
            # Update sync status
            self._update_sync_status("all", "in_progress")
            
            # Create session for requests
            async with aiohttp.ClientSession() as session:
                # Process each documentation source
                tasks = []
                for category, url in DOCS_SOURCES.items():
                    task = self._process_doc_source(session, category, url)
                    tasks.append(task)
                
                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Check results
                success = all(isinstance(r, bool) and r for r in results)
                
                # Update sync status
                status = "success" if success else "failed"
                self._update_sync_status("all", status)
                
                return success
                
        except Exception as e:
            logger.error(f"Error syncing documentation: {e}")
            self._update_sync_status("all", "failed")
            return False
    
    async def _process_doc_source(self, session: aiohttp.ClientSession, category: str, url: str) -> bool:
        """
        Process a documentation source.
        
        Args:
            session: aiohttp session
            category: Documentation category
            url: URL to fetch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch main page
            logger.info(f"Fetching {category} documentation from {url}")
            html = await self._fetch_url(session, url)
            if not html:
                return False
            
            # Parse main page
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract links to documentation pages
            links = []
            content_div = soup.find("div", class_="content")
            if content_div:
                for a in content_div.find_all("a", href=True):
                    href = a["href"]
                    # Only process relative links or links to monome.org
                    if href.startswith("/") or href.startswith("https://monome.org"):
                        if href.startswith("/"):
                            href = f"https://monome.org{href}"
                        links.append(href)
            
            # Store the main page
            self._store_doc_page(category, url, html)
            
            # Process each link
            link_tasks = []
            for link in links:
                if link != url:  # Avoid processing the same page
                    task = self._process_doc_page(session, category, link)
                    link_tasks.append(task)
            
            # Wait for all tasks to complete
            if link_tasks:
                await asyncio.gather(*link_tasks, return_exceptions=True)
            
            # Special processing for API documentation
            if category == "api":
                await self._extract_api_functions(session)
            
            # Special processing for engine documentation
            if category == "engines":
                await self._extract_engines(session)
            
            # Update sync status
            self._update_sync_status(category, "success")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {category} documentation: {e}")
            self._update_sync_status(category, "failed")
            return False
    
    async def _process_doc_page(self, session: aiohttp.ClientSession, category: str, url: str) -> bool:
        """
        Process a documentation page.
        
        Args:
            session: aiohttp session
            category: Documentation category
            url: URL to fetch
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch page
            html = await self._fetch_url(session, url)
            if not html:
                return False
            
            # Store page
            self._store_doc_page(category, url, html)
            return True
            
        except Exception as e:
            logger.error(f"Error processing page {url}: {e}")
            return False
    
    async def _fetch_url(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """
        Fetch a URL.
        
        Args:
            session: aiohttp session
            url: URL to fetch
            
        Returns:
            HTML content if successful, None otherwise
        """
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Error fetching {url}: {response.status}")
                    return None
                return await response.text()
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _store_doc_page(self, category: str, url: str, html: str) -> bool:
        """
        Store a documentation page.
        
        Args:
            category: Documentation category
            url: URL of the page
            html: HTML content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse HTML
            soup = BeautifulSoup(html, "html.parser")
            
            # Extract title
            title = "Untitled"
            title_elem = soup.find("title")
            if title_elem:
                title = title_elem.text.strip()
            
            # Extract content
            content = ""
            content_div = soup.find("div", class_="content")
            if content_div:
                content = content_div.text.strip()
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update page
            cursor.execute('''
            INSERT OR REPLACE INTO docs 
            (category, title, url, content, html_content, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (category, title, url, content, html, datetime.now()))
            
            # Update full-text search index
            doc_id = cursor.lastrowid
            cursor.execute('''
            INSERT OR REPLACE INTO docs_fts 
            (rowid, title, content, category, url)
            VALUES (?, ?, ?, ?, ?)
            ''', (doc_id, title, content, category, url))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error storing page {url}: {e}")
            return False
    
    async def _extract_api_functions(self, session: aiohttp.ClientSession) -> bool:
        """
        Extract API functions from documentation.
        
        Args:
            session: aiohttp session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get API documentation pages
            cursor.execute("SELECT id, url, html_content FROM docs WHERE category = 'api'")
            pages = cursor.fetchall()
            
            for page_id, url, html in pages:
                if not html:
                    continue
                
                soup = BeautifulSoup(html, "html.parser")
                
                # Find function definitions
                for section in soup.find_all(["section", "div"], class_=["function", "method"]):
                    # Extract function details
                    name = ""
                    description = ""
                    signature = ""
                    parameters = ""
                    return_value = ""
                    example = ""
                    
                    # Name
                    name_elem = section.find(["h2", "h3", "h4"])
                    if name_elem:
                        name = name_elem.text.strip()
                    
                    # Description
                    desc_elem = section.find(["p", "div"], class_="description")
                    if desc_elem:
                        description = desc_elem.text.strip()
                    
                    # Signature
                    sig_elem = section.find(["pre", "code"], class_="signature")
                    if sig_elem:
                        signature = sig_elem.text.strip()
                    
                    # Parameters
                    params_elem = section.find(["div", "table"], class_="parameters")
                    if params_elem:
                        parameters = params_elem.text.strip()
                    
                    # Return value
                    ret_elem = section.find(["div", "p"], class_="return")
                    if ret_elem:
                        return_value = ret_elem.text.strip()
                    
                    # Example
                    example_elem = section.find(["pre", "code"], class_="example")
                    if example_elem:
                        example = example_elem.text.strip()
                    
                    # Skip if no name
                    if not name:
                        continue
                    
                    # Store function
                    cursor.execute('''
                    INSERT OR REPLACE INTO api_functions 
                    (name, category, description, signature, parameters, return_value, example, source_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (name, "api", description, signature, parameters, return_value, example, url))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error extracting API functions: {e}")
            return False
    
    async def _extract_engines(self, session: aiohttp.ClientSession) -> bool:
        """
        Extract engine information from documentation.
        
        Args:
            session: aiohttp session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get engine documentation pages
            cursor.execute("SELECT id, url, html_content FROM docs WHERE category = 'engines'")
            pages = cursor.fetchall()
            
            for page_id, url, html in pages:
                if not html:
                    continue
                
                soup = BeautifulSoup(html, "html.parser")
                
                # Find engine definitions
                for section in soup.find_all(["section", "div"], class_=["engine", "module"]):
                    # Extract engine details
                    name = ""
                    description = ""
                    parameters = ""
                    commands = ""
                    example = ""
                    
                    # Name
                    name_elem = section.find(["h2", "h3", "h4"])
                    if name_elem:
                        name = name_elem.text.strip()
                    
                    # Description
                    desc_elem = section.find(["p", "div"], class_="description")
                    if desc_elem:
                        description = desc_elem.text.strip()
                    
                    # Parameters
                    params_elem = section.find(["div", "table"], class_="parameters")
                    if params_elem:
                        parameters = params_elem.text.strip()
                    
                    # Commands
                    cmd_elem = section.find(["div", "table"], class_="commands")
                    if cmd_elem:
                        commands = cmd_elem.text.strip()
                    
                    # Example
                    example_elem = section.find(["pre", "code"], class_="example")
                    if example_elem:
                        example = example_elem.text.strip()
                    
                    # Skip if no name
                    if not name:
                        continue
                    
                    # Store engine
                    cursor.execute('''
                    INSERT OR REPLACE INTO engines 
                    (name, description, parameters, commands, example, source_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (name, description, parameters, commands, example, url))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error extracting engines: {e}")
            return False
    
    def _update_sync_status(self, category: str, status: str) -> None:
        """
        Update the synchronization status.
        
        Args:
            category: Documentation category
            status: Synchronization status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO sync_status 
            (category, last_sync, status)
            VALUES (?, ?, ?)
            ''', (category, datetime.now(), status))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating sync status: {e}")
    
    def _needs_sync(self) -> bool:
        """
        Check if documentation needs to be synchronized.
        
        Returns:
            True if sync is needed, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check sync status
            cursor.execute("SELECT last_sync FROM sync_status WHERE category = 'all'")
            result = cursor.fetchone()
            
            conn.close()
            
            if not result:
                return True
                
            last_sync = datetime.fromisoformat(result[0])
            return (datetime.now() - last_sync) > timedelta(days=self.refresh_days)
            
        except Exception as e:
            logger.error(f"Error checking sync status: {e}")
            return True
    
    def search(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search documentation.
        
        Args:
            query: Search query
            category: Optional category to search
            limit: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            sql = "SELECT docs.id, docs.title, docs.url, docs.category, snippet(docs_fts, 1, '<mark>', '</mark>', '...', 30) FROM docs_fts JOIN docs ON docs_fts.rowid = docs.id WHERE docs_fts MATCH ?"
            params = [query]
            
            if category:
                sql += " AND docs.category = ?"
                params.append(category)
            
            sql += f" ORDER BY rank LIMIT {limit}"
            
            # Execute query
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # Format results
            docs = []
            for doc_id, title, url, category, snippet in results:
                docs.append({
                    "id": doc_id,
                    "title": title,
                    "url": url,
                    "category": category,
                    "snippet": snippet
                })
            
            conn.close()
            return docs
            
        except Exception as e:
            logger.error(f"Error searching documentation: {e}")
            return []
    
    def search_api(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search API functions.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching API functions
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute("""
            SELECT id, name, category, description, signature, parameters, return_value, example, source_url
            FROM api_functions
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            results = cursor.fetchall()
            
            # Format results
            functions = []
            for row in results:
                functions.append({
                    "id": row[0],
                    "name": row[1],
                    "category": row[2],
                    "description": row[3],
                    "signature": row[4],
                    "parameters": row[5],
                    "return_value": row[6],
                    "example": row[7],
                    "source_url": row[8]
                })
            
            conn.close()
            return functions
            
        except Exception as e:
            logger.error(f"Error searching API functions: {e}")
            return []
    
    def search_engines(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search engines.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching engines
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute("""
            SELECT id, name, description, parameters, commands, example, source_url
            FROM engines
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY name LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            results = cursor.fetchall()
            
            # Format results
            engines = []
            for row in results:
                engines.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "parameters": row[3],
                    "commands": row[4],
                    "example": row[5],
                    "source_url": row[6]
                })
            
            conn.close()
            return engines
            
        except Exception as e:
            logger.error(f"Error searching engines: {e}")
            return []
    
    def get_document(self, doc_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document details if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute("""
            SELECT id, category, title, url, content, html_content, last_updated
            FROM docs
            WHERE id = ?
            """, (doc_id,))
            
            result = cursor.fetchone()
            
            conn.close()
            
            if not result:
                return None
                
            return {
                "id": result[0],
                "category": result[1],
                "title": result[2],
                "url": result[3],
                "content": result[4],
                "html_content": result[5],
                "last_updated": result[6]
            }
            
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    def get_api_function(self, func_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an API function by ID.
        
        Args:
            func_id: Function ID
            
        Returns:
            Function details if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute("""
            SELECT id, name, category, description, signature, parameters, return_value, example, source_url
            FROM api_functions
            WHERE id = ?
            """, (func_id,))
            
            result = cursor.fetchone()
            
            conn.close()
            
            if not result:
                return None
                
            return {
                "id": result[0],
                "name": result[1],
                "category": result[2],
                "description": result[3],
                "signature": result[4],
                "parameters": result[5],
                "return_value": result[6],
                "example": result[7],
                "source_url": result[8]
            }
            
        except Exception as e:
            logger.error(f"Error getting API function: {e}")
            return None
    
    def get_engine(self, engine_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an engine by ID.
        
        Args:
            engine_id: Engine ID
            
        Returns:
            Engine details if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute("""
            SELECT id, name, description, parameters, commands, example, source_url
            FROM engines
            WHERE id = ?
            """, (engine_id,))
            
            result = cursor.fetchone()
            
            conn.close()
            
            if not result:
                return None
                
            return {
                "id": result[0],
                "name": result[1],
                "description": result[2],
                "parameters": result[3],
                "commands": result[4],
                "example": result[5],
                "source_url": result[6]
            }
            
        except Exception as e:
            logger.error(f"Error getting engine: {e}")
            return None
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get synchronization status.
        
        Returns:
            Synchronization status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute("SELECT category, last_sync, status FROM sync_status")
            results = cursor.fetchall()
            
            conn.close()
            
            status = {}
            for category, last_sync, sync_status in results:
                status[category] = {
                    "last_sync": last_sync,
                    "status": sync_status
                }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get documentation statistics.
        
        Returns:
            Documentation statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Count documents by category
            cursor.execute("SELECT category, COUNT(*) FROM docs GROUP BY category")
            for category, count in cursor.fetchall():
                stats[f"{category}_count"] = count
            
            # Count API functions
            cursor.execute("SELECT COUNT(*) FROM api_functions")
            stats["api_functions_count"] = cursor.fetchone()[0]
            
            # Count engines
            cursor.execute("SELECT COUNT(*) FROM engines")
            stats["engines_count"] = cursor.fetchone()[0]
            
            # Total document count
            cursor.execute("SELECT COUNT(*) FROM docs")
            stats["total_docs"] = cursor.fetchone()[0]
            
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def print_document(self, doc: Dict[str, Any]) -> None:
        """
        Print a document in formatted form.
        
        Args:
            doc: Document details
        """
        self.console.print(f"[bold cyan]{doc['title']}[/bold cyan]")
        self.console.print(f"[dim]Category: {doc['category']}[/dim]")
        self.console.print(f"[dim]URL: {doc['url']}[/dim]")
        self.console.print()
        
        # Convert HTML to Markdown
        content = doc["content"]
        if content:
            self.console.print(content)
        else:
            self.console.print("[dim]No content available[/dim]")
    
    def print_api_function(self, func: Dict[str, Any]) -> None:
        """
        Print an API function in formatted form.
        
        Args:
            func: Function details
        """
        self.console.print(f"[bold cyan]{func['name']}[/bold cyan]")
        
        if func["signature"]:
            self.console.print("[bold]Signature:[/bold]")
            self.console.print(f"[yellow]{func['signature']}[/yellow]")
        
        if func["description"]:
            self.console.print("\n[bold]Description:[/bold]")
            self.console.print(func["description"])
        
        if func["parameters"]:
            self.console.print("\n[bold]Parameters:[/bold]")
            self.console.print(func["parameters"])
        
        if func["return_value"]:
            self.console.print("\n[bold]Returns:[/bold]")
            self.console.print(func["return_value"])
        
        if func["example"]:
            self.console.print("\n[bold]Example:[/bold]")
            self.console.print(f"[green]{func['example']}[/green]")
        
        self.console.print(f"\n[dim]Source: {func['source_url']}[/dim]")
    
    def print_engine(self, engine: Dict[str, Any]) -> None:
        """
        Print an engine in formatted form.
        
        Args:
            engine: Engine details
        """
        self.console.print(f"[bold cyan]{engine['name']}[/bold cyan]")
        
        if engine["description"]:
            self.console.print("\n[bold]Description:[/bold]")
            self.console.print(engine["description"])
        
        if engine["parameters"]:
            self.console.print("\n[bold]Parameters:[/bold]")
            self.console.print(engine["parameters"])
        
        if engine["commands"]:
            self.console.print("\n[bold]Commands:[/bold]")
            self.console.print(engine["commands"])
        
        if engine["example"]:
            self.console.print("\n[bold]Example:[/bold]")
            self.console.print(f"[green]{engine['example']}[/green]")
        
        self.console.print(f"\n[dim]Source: {engine['source_url']}[/dim]")
    
    def is_docs_available(self) -> bool:
        """
        Check if documentation is available.
        
        Returns:
            True if documentation is available, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if any documents exist
            cursor.execute("SELECT COUNT(*) FROM docs")
            count = cursor.fetchone()[0]
            
            conn.close()
            return count > 0
            
        except Exception as e:
            logger.error(f"Error checking documentation availability: {e}")
            return False


async def main():
    """
    Main function for command line use.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Norns documentation manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Synchronize documentation")
    sync_parser.add_argument("--force", action="store_true", help="Force refresh even if cache is recent")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search documentation")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--category", help="Category to search")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    
    # API search command
    api_parser = subparsers.add_parser("api", help="Search API functions")
    api_parser.add_argument("query", help="Search query")
    api_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    
    # Engine search command
    engine_parser = subparsers.add_parser("engine", help="Search engines")
    engine_parser.add_argument("query", help="Search query")
    engine_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    
    # View command
    view_parser = subparsers.add_parser("view", help="View a document")
    view_parser.add_argument("id", type=int, help="Document ID")
    
    # API view command
    api_view_parser = subparsers.add_parser("view-api", help="View an API function")
    api_view_parser.add_argument("id", type=int, help="Function ID")
    
    # Engine view command
    engine_view_parser = subparsers.add_parser("view-engine", help="View an engine")
    engine_view_parser.add_argument("id", type=int, help="Engine ID")
    
    # Status command
    subparsers.add_parser("status", help="Show synchronization status")
    
    # Stats command
    subparsers.add_parser("stats", help="Show documentation statistics")
    
    args = parser.parse_args()
    
    docs = NornsDocsManager()
    
    if args.command == "sync":
        console = Console()
        with console.status("Synchronizing documentation..."):
            success = await docs.sync_documentation(args.force)
        
        if success:
            console.print("[bold green]Documentation synchronized successfully[/bold green]")
        else:
            console.print("[bold red]Error synchronizing documentation[/bold red]")
    
    elif args.command == "search":
        # Check if docs are available
        if not docs.is_docs_available():
            console = Console()
            console.print("[bold yellow]Documentation not available. Syncing...[/bold yellow]")
            with console.status("Synchronizing documentation..."):
                await docs.sync_documentation()
        
        results = docs.search(args.query, args.category, args.limit)
        
        console = Console()
        console.print(f"[bold]Found {len(results)} results for '{args.query}':[/bold]")
        
        for i, doc in enumerate(results, 1):
            console.print(f"[bold cyan]{i}. {doc['title']}[/bold cyan]")
            console.print(f"   [dim]Category: {doc['category']}[/dim]")
            console.print(f"   [dim]URL: {doc['url']}[/dim]")
            if "snippet" in doc and doc["snippet"]:
                console.print(f"   {doc['snippet']}")
            console.print()
    
    elif args.command == "api":
        # Check if docs are available
        if not docs.is_docs_available():
            console = Console()
            console.print("[bold yellow]Documentation not available. Syncing...[/bold yellow]")
            with console.status("Synchronizing documentation..."):
                await docs.sync_documentation()
        
        results = docs.search_api(args.query, args.limit)
        
        console = Console()
        console.print(f"[bold]Found {len(results)} API functions for '{args.query}':[/bold]")
        
        for i, func in enumerate(results, 1):
            console.print(f"[bold cyan]{i}. {func['name']}[/bold cyan]")
            if func["signature"]:
                console.print(f"   [yellow]{func['signature']}[/yellow]")
            if func["description"]:
                desc = func["description"]
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                console.print(f"   {desc}")
            console.print()
    
    elif args.command == "engine":
        # Check if docs are available
        if not docs.is_docs_available():
            console = Console()
            console.print("[bold yellow]Documentation not available. Syncing...[/bold yellow]")
            with console.status("Synchronizing documentation..."):
                await docs.sync_documentation()
        
        results = docs.search_engines(args.query, args.limit)
        
        console = Console()
        console.print(f"[bold]Found {len(results)} engines for '{args.query}':[/bold]")
        
        for i, engine in enumerate(results, 1):
            console.print(f"[bold cyan]{i}. {engine['name']}[/bold cyan]")
            if engine["description"]:
                desc = engine["description"]
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                console.print(f"   {desc}")
            console.print()
    
    elif args.command == "view":
        doc = docs.get_document(args.id)
        if doc:
            docs.print_document(doc)
        else:
            print(f"Document with ID {args.id} not found")
    
    elif args.command == "view-api":
        func = docs.get_api_function(args.id)
        if func:
            docs.print_api_function(func)
        else:
            print(f"API function with ID {args.id} not found")
    
    elif args.command == "view-engine":
        engine = docs.get_engine(args.id)
        if engine:
            docs.print_engine(engine)
        else:
            print(f"Engine with ID {args.id} not found")
    
    elif args.command == "status":
        status = docs.get_sync_status()
        
        console = Console()
        console.print("[bold]Documentation Synchronization Status:[/bold]")
        
        if not status:
            console.print("[dim]No synchronization status available[/dim]")
        else:
            for category, info in status.items():
                status_color = "green" if info["status"] == "success" else "red"
                console.print(f"[bold]{category}[/bold]: [{status_color}]{info['status']}[/{status_color}] (Last sync: {info['last_sync']})")
    
    elif args.command == "stats":
        stats = docs.get_stats()
        
        console = Console()
        console.print("[bold]Documentation Statistics:[/bold]")
        
        if not stats:
            console.print("[dim]No statistics available[/dim]")
        else:
            for key, value in stats.items():
                console.print(f"[bold]{key}[/bold]: {value}")
    
    else:
        parser.print_help()


# Helper function to easily access documentation in code
def get_docs_manager() -> NornsDocsManager:
    """Get a documentation manager instance."""
    return NornsDocsManager()


if __name__ == "__main__":
    asyncio.run(main())