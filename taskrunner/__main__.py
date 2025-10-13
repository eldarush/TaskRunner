"""
Main entry point for the TaskRunner CLI application.

This module provides the primary entry point for executing TaskRunner
from the command line. It imports and runs the main CLI interface.
"""

from .cli import cli

if __name__ == "__main__":
    cli()