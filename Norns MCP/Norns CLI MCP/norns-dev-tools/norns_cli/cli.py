#!/usr/bin/env python3
"""
Norns CLI using Typer.
This provides a user-friendly command-line interface for interacting with Norns.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import Norns tools
from norns_cli.norns_ssh import NornsSSH
from norns_cli.github_integration import NornsGitHub

# Create console for rich output
console = Console()

# Import Norns docs manager
from norns_cli.docs_manager import NornsDocsManager, get_docs_manager

# Create Typer app
app = typer.Typer(
    help="Norns CLI - Tools for interacting with Norns from Claude Code",
    add_completion=False,
)

# Create Docs subcommand
docs_app = typer.Typer(help="Access Norns documentation")
app.add_typer(docs_app, name="docs")

# Shared connection parameters
host_option = typer.Option(None, "--host", "-h", help="Hostname or IP address of Norns device")
port_option = typer.Option(22, "--port", "-p", help="SSH port on Norns device")
username_option = typer.Option("we", "--username", "-u", help="Username for Norns device")
password_option = typer.Option("sleep", "--password", "-P", help="Password for Norns device")
config_option = typer.Option(None, "--config", "-c", help="Path to config file")


def get_ssh_client(host: str, port: int, username: str, password: str, config: str) -> NornsSSH:
    """Create an SSH client with the provided options."""
    return NornsSSH(
        host=host,
        port=port,
        username=username,
        password=password,
        config_path=config
    )


@app.command("run")
def run_command(
    command: str = typer.Argument(..., help="Shell command to run on Norns"),
    host: Optional[str] = host_option,
    port: int = port_option,
    username: str = username_option,
    password: str = password_option,
    config: Optional[str] = config_option,
):
    """Run a shell command on Norns."""
    async def _run():
        ssh = get_ssh_client(host, port, username, password, config)
        with console.status(f"Connecting to Norns at {ssh.host}..."):
            await ssh.connect()
        
        with console.status(f"Running command: {command}"):
            stdout, stderr, code = await ssh.run_command(command)
        
        if stdout:
            console.print(stdout)
        if stderr:
            console.print(f"[bold red]Error:[/bold red] {stderr}")
        
        await ssh.disconnect()
        return code
    
    code = asyncio.run(_run())
    sys.exit(code)


@app.command("lua")
def run_lua(
    code: str = typer.Argument(..., help="Lua code to run on Norns"),
    host: Optional[str] = host_option,
    port: int = port_option,
    username: str = username_option,
    password: str = password_option,
    config: Optional[str] = config_option,
):
    """Run Lua code on Norns."""
    async def _run():
        ssh = get_ssh_client(host, port, username, password, config)
        with console.status(f"Connecting to Norns at {ssh.host}..."):
            await ssh.connect()
        
        with console.status(f"Running Lua code..."):
            stdout, stderr, code = await ssh.run_lua(code)
        
        if stdout:
            console.print(stdout)
        if stderr:
            console.print(f"[bold red]Error:[/bold red] {stderr}")
        
        await ssh.disconnect()
        return code
    
    code = asyncio.run(_run())
    sys.exit(code)


@app.command("list")
def list_scripts(
    host: Optional[str] = host_option,
    port: int = port_option,
    username: str = username_option,
    password: str = password_option,
    config: Optional[str] = config_option,
):
    """List scripts on Norns."""
    async def _run():
        ssh = get_ssh_client(host, port, username, password, config)
        with console.status(f"Connecting to Norns at {ssh.host}..."):
            await ssh.connect()
        
        with console.status("Listing scripts..."):
            scripts = await ssh.list_scripts()
        
        # Create a table
        table = Table(title="Norns Scripts")
        table.add_column("Script", style="cyan")
        
        for script in scripts:
            table.add_row(script)
        
        console.print(table)
        
        await ssh.disconnect()
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@app.command("info")
def system_info(
    host: Optional[str] = host_option,
    port: int = port_option,
    username: str = username_option,
    password: str = password_option,
    config: Optional[str] = config_option,
):
    """Get system information from Norns."""
    async def _run():
        ssh = get_ssh_client(host, port, username, password, config)
        with console.status(f"Connecting to Norns at {ssh.host}..."):
            await ssh.connect()
        
        # Get OS info
        with console.status("Getting system information..."):
            cmd_results = {}
            
            # OS version
            stdout, _, _ = await ssh.run_command("cat /etc/os-release | grep PRETTY_NAME")
            if stdout:
                os_version = stdout.split('=')[1].strip().strip('"')
                cmd_results["OS Version"] = os_version
            
            # Try to get norns version
            stdout, _, _ = await ssh.run_lua('print(norns.version.norns)')
            if stdout and "nil value" not in stdout:
                cmd_results["Norns Version"] = stdout.strip()
            
            # Current script
            stdout, _, _ = await ssh.run_lua('print(norns.state.script)')
            if stdout and "nil value" not in stdout:
                cmd_results["Current Script"] = stdout.strip() or "None"
            
            # Free disk space
            stdout, _, _ = await ssh.run_command("df -h / | tail -1 | awk '{print $4}'")
            if stdout:
                cmd_results["Free Disk Space"] = f"{stdout.strip()}"
            
            # Memory
            stdout, _, _ = await ssh.run_command("free -m | grep Mem | awk '{print $2,$3,$4}'")
            if stdout:
                parts = stdout.strip().split()
                if len(parts) >= 3:
                    total, used, free = parts
                    cmd_results["Memory"] = f"{free} MB free / {total} MB total"
            
            # Uptime
            stdout, _, _ = await ssh.run_command("uptime -p")
            if stdout:
                cmd_results["Uptime"] = stdout.strip()
        
        # Create a table
        table = Table(title=f"Norns System Info - {ssh.host}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in cmd_results.items():
            table.add_row(key, value)
        
        console.print(table)
        
        await ssh.disconnect()
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@app.command("current")
def current_script(
    host: Optional[str] = host_option,
    port: int = port_option,
    username: str = username_option,
    password: str = password_option,
    config: Optional[str] = config_option,
):
    """Get the currently running script on Norns."""
    async def _run():
        ssh = get_ssh_client(host, port, username, password, config)
        with console.status(f"Connecting to Norns at {ssh.host}..."):
            await ssh.connect()
        
        with console.status("Getting current script..."):
            script = await ssh.get_current_script()
        
        if script:
            console.print(f"Current script: [bold cyan]{script}[/bold cyan]")
        else:
            console.print("No script currently running")
        
        await ssh.disconnect()
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@app.command("restart")
def restart_script(
    host: Optional[str] = host_option,
    port: int = port_option,
    username: str = username_option,
    password: str = password_option,
    config: Optional[str] = config_option,
):
    """Restart the current script on Norns."""
    async def _run():
        ssh = get_ssh_client(host, port, username, password, config)
        with console.status(f"Connecting to Norns at {ssh.host}..."):
            await ssh.connect()
        
        with console.status("Restarting current script..."):
            success = await ssh.restart_script()
        
        if success:
            console.print("[bold green]Successfully restarted script[/bold green]")
            code = 0
        else:
            console.print("[bold red]Failed to restart script[/bold red]")
            code = 1
        
        await ssh.disconnect()
        return code
    
    code = asyncio.run(_run())
    sys.exit(code)


@app.command("sync")
def sync_script(
    path: str = typer.Argument(..., help="Path to local script or directory"),
    remote: Optional[str] = typer.Option(None, "--remote", "-r", help="Remote path on Norns"),
    host: Optional[str] = host_option,
    port: int = port_option,
    username: str = username_option,
    password: str = password_option,
    config: Optional[str] = config_option,
):
    """Sync a script or directory to Norns."""
    async def _run():
        ssh = get_ssh_client(host, port, username, password, config)
        with console.status(f"Connecting to Norns at {ssh.host}..."):
            await ssh.connect()
        
        # Check if path is a file or directory
        path_obj = Path(path)
        if not path_obj.exists():
            console.print(f"[bold red]Error:[/bold red] Path {path} does not exist")
            return 1
        
        if path_obj.is_file():
            # Sync single file
            with console.status(f"Syncing {path} to Norns..."):
                success = await ssh.sync_script(path, remote)
            
            if success:
                console.print(f"[bold green]Successfully synced[/bold green] {path}")
                code = 0
            else:
                console.print(f"[bold red]Failed to sync[/bold red] {path}")
                code = 1
        
        elif path_obj.is_dir():
            # Sync directory
            github = NornsGitHub(norns_ssh=ssh)
            with console.status(f"Syncing directory {path} to Norns..."):
                results = await github.sync_repo_to_norns(path, remote)
            
            # Report results
            success_count = sum(1 for result in results.values() if result)
            fail_count = len(results) - success_count
            
            if fail_count == 0:
                console.print(f"[bold green]Successfully synced[/bold green] {success_count} files to Norns")
                code = 0
            else:
                console.print(f"[bold yellow]Synced {success_count} files, {fail_count} failed[/bold yellow]")
                
                # Show failed files
                console.print("\n[bold red]Failed files:[/bold red]")
                for file_path, success in results.items():
                    if not success:
                        console.print(f"  {file_path}")
                
                code = 1
        
        await ssh.disconnect()
        return code
    
    code = asyncio.run(_run())
    sys.exit(code)


@app.command("github")
def github_clone(
    repo_url: str = typer.Argument(..., help="URL of GitHub repository to clone"),
    script_name: Optional[str] = typer.Option(None, "--name", "-n", help="Name to use for script on Norns"),
    host: Optional[str] = host_option,
    port: int = port_option,
    username: str = username_option,
    password: str = password_option,
    config: Optional[str] = config_option,
):
    """Clone a GitHub repository and sync it to Norns."""
    async def _run():
        ssh = get_ssh_client(host, port, username, password, config)
        github = NornsGitHub(norns_ssh=ssh)
        
        with console.status(f"Cloning and syncing {repo_url} to Norns..."):
            success = await github.clone_and_sync(repo_url, script_name)
        
        if success:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            script_name_display = script_name or repo_name
            console.print(f"[bold green]Successfully cloned and synced[/bold green] {repo_url} to Norns as '{script_name_display}'")
            code = 0
        else:
            console.print(f"[bold red]Failed to clone and sync[/bold red] {repo_url}")
            code = 1
        
        return code
    
    code = asyncio.run(_run())
    sys.exit(code)


# Documentation commands
@docs_app.command("sync")
def docs_sync(
    force: bool = typer.Option(False, "--force", "-f", help="Force refresh even if cache is recent"),
):
    """Synchronize Norns documentation from monome.org."""
    async def _run():
        docs_manager = get_docs_manager()
        
        with console.status("Synchronizing documentation from monome.org..."):
            success = await docs_manager.sync_documentation(force)
        
        if success:
            console.print("[bold green]Documentation synchronized successfully![/bold green]")
            stats = docs_manager.get_stats()
            
            if stats:
                table = Table(title="Documentation Statistics")
                table.add_column("Category", style="cyan")
                table.add_column("Count", style="green")
                
                for key, value in stats.items():
                    if key.endswith("_count"):
                        category = key.replace("_count", "").replace("_", " ").title()
                        table.add_row(category, str(value))
                
                console.print(table)
        else:
            console.print("[bold red]Error synchronizing documentation[/bold red]")
        
        return 0 if success else 1
    
    code = asyncio.run(_run())
    sys.exit(code)


@docs_app.command("search")
def docs_search(
    query: str = typer.Argument(..., help="Search query"),
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Category to search"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results"),
):
    """Search Norns documentation."""
    async def _run():
        docs_manager = get_docs_manager()
        
        # Check if docs are available
        if not docs_manager.is_docs_available():
            console.print("[bold yellow]Documentation not available. Syncing...[/bold yellow]")
            with console.status("Synchronizing documentation..."):
                await docs_manager.sync_documentation()
        
        with console.status(f"Searching for '{query}'..."):
            results = docs_manager.search(query, category, limit)
        
        if not results:
            console.print(f"[bold yellow]No results found for '{query}'[/bold yellow]")
            return 0
        
        console.print(f"[bold]Found {len(results)} results for '{query}':[/bold]")
        
        table = Table(show_header=True, box=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Title", style="cyan")
        table.add_column("Category", style="green")
        table.add_column("Snippet", no_wrap=False)
        
        for i, doc in enumerate(results, 1):
            snippet = doc.get("snippet", "").replace("<mark>", "[bold yellow]").replace("</mark>", "[/bold yellow]")
            table.add_row(
                str(i), 
                doc["title"], 
                doc["category"], 
                snippet
            )
        
        console.print(table)
        console.print("\n[dim]Use 'norns docs view <id>' to view a document[/dim]")
        
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@docs_app.command("api")
def docs_api(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results"),
):
    """Search Norns API documentation."""
    async def _run():
        docs_manager = get_docs_manager()
        
        # Check if docs are available
        if not docs_manager.is_docs_available():
            console.print("[bold yellow]Documentation not available. Syncing...[/bold yellow]")
            with console.status("Synchronizing documentation..."):
                await docs_manager.sync_documentation()
        
        with console.status(f"Searching API for '{query}'..."):
            results = docs_manager.search_api(query, limit)
        
        if not results:
            console.print(f"[bold yellow]No API functions found for '{query}'[/bold yellow]")
            return 0
        
        console.print(f"[bold]Found {len(results)} API functions for '{query}':[/bold]")
        
        table = Table(show_header=True, box=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Function", style="cyan")
        table.add_column("Signature", style="yellow")
        table.add_column("Description", no_wrap=False)
        
        for i, func in enumerate(results, 1):
            description = func.get("description", "")
            if len(description) > 100:
                description = description[:100] + "..."
                
            signature = func.get("signature", "")
            if len(signature) > 50:
                signature = signature[:50] + "..."
                
            table.add_row(
                str(i), 
                func["name"], 
                signature, 
                description
            )
        
        console.print(table)
        console.print("\n[dim]Use 'norns docs api-view <id>' to view API function details[/dim]")
        
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@docs_app.command("engines")
def docs_engines(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results"),
):
    """Search Norns engine documentation."""
    async def _run():
        docs_manager = get_docs_manager()
        
        # Check if docs are available
        if not docs_manager.is_docs_available():
            console.print("[bold yellow]Documentation not available. Syncing...[/bold yellow]")
            with console.status("Synchronizing documentation..."):
                await docs_manager.sync_documentation()
        
        with console.status(f"Searching engines for '{query}'..."):
            results = docs_manager.search_engines(query, limit)
        
        if not results:
            console.print(f"[bold yellow]No engines found for '{query}'[/bold yellow]")
            return 0
        
        console.print(f"[bold]Found {len(results)} engines for '{query}':[/bold]")
        
        table = Table(show_header=True, box=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Engine", style="cyan")
        table.add_column("Description", no_wrap=False)
        
        for i, engine in enumerate(results, 1):
            description = engine.get("description", "")
            if len(description) > 100:
                description = description[:100] + "..."
                
            table.add_row(
                str(i), 
                engine["name"], 
                description
            )
        
        console.print(table)
        console.print("\n[dim]Use 'norns docs engine-view <id>' to view engine details[/dim]")
        
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@docs_app.command("view")
def docs_view(
    doc_id: int = typer.Argument(..., help="Document ID to view"),
):
    """View a Norns documentation document."""
    async def _run():
        docs_manager = get_docs_manager()
        
        doc = docs_manager.get_document(doc_id)
        if not doc:
            console.print(f"[bold red]Document with ID {doc_id} not found[/bold red]")
            return 1
        
        docs_manager.print_document(doc)
        
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@docs_app.command("api-view")
def docs_api_view(
    func_id: int = typer.Argument(..., help="API function ID to view"),
):
    """View a Norns API function."""
    async def _run():
        docs_manager = get_docs_manager()
        
        func = docs_manager.get_api_function(func_id)
        if not func:
            console.print(f"[bold red]API function with ID {func_id} not found[/bold red]")
            return 1
        
        docs_manager.print_api_function(func)
        
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@docs_app.command("engine-view")
def docs_engine_view(
    engine_id: int = typer.Argument(..., help="Engine ID to view"),
):
    """View a Norns engine."""
    async def _run():
        docs_manager = get_docs_manager()
        
        engine = docs_manager.get_engine(engine_id)
        if not engine:
            console.print(f"[bold red]Engine with ID {engine_id} not found[/bold red]")
            return 1
        
        docs_manager.print_engine(engine)
        
        return 0
    
    code = asyncio.run(_run())
    sys.exit(code)


@docs_app.command("status")
def docs_status():
    """Show documentation synchronization status."""
    docs_manager = get_docs_manager()
    
    status = docs_manager.get_sync_status()
    
    if not status:
        console.print("[dim]No synchronization status available[/dim]")
        return
    
    table = Table(title="Documentation Synchronization Status")
    table.add_column("Category", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Last Sync", style="dim")
    
    for category, info in status.items():
        status_text = info["status"]
        status_style = "green" if status_text == "success" else "red" if status_text == "failed" else "yellow"
        
        table.add_row(
            category,
            f"[{status_style}]{status_text}[/{status_style}]",
            info["last_sync"]
        )
    
    console.print(table)


if __name__ == "__main__":
    app()