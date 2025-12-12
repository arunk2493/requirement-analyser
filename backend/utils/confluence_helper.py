"""Confluence utilities for consistent page creation and management"""
import logging
from typing import Tuple, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def add_timestamp(name: str) -> str:
    """
    Add timestamp to name for uniqueness.
    
    Args:
        name: Base name
        
    Returns:
        Name with timestamp suffix
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{ts}"


def create_confluence_html_content(title: str, content: Dict[str, Any], section_configs: Optional[Dict] = None) -> str:
    """
    Create HTML content for Confluence pages from structured data.
    
    Args:
        title: Page title
        content: Dictionary with content fields
        section_configs: Configuration for special handling of sections
        
    Returns:
        HTML string for Confluence
    """
    html_parts = [f"<h2>{title}</h2>"]
    
    section_configs = section_configs or {}
    
    for key, value in content.items():
        if value is None:
            continue
            
        # Skip metadata fields
        if key.startswith('_') or key in ['id', 'name']:
            continue
        
        # Get section config
        config = section_configs.get(key, {})
        heading_level = config.get('heading_level', 3)
        is_list = config.get('is_list', isinstance(value, list))
        
        # Create heading
        heading_tag = f"h{heading_level}"
        html_parts.append(f"<{heading_tag}>{key.replace('_', ' ').title()}</{heading_tag}>")
        
        # Handle different value types
        if is_list and isinstance(value, list):
            html_parts.append("<ul>")
            for item in value:
                if isinstance(item, dict):
                    html_parts.append(f"<li><strong>{item.get('name', 'Item')}:</strong> {item.get('description', '')}</li>")
                else:
                    html_parts.append(f"<li>{str(item)}</li>")
            html_parts.append("</ul>")
        elif isinstance(value, dict):
            html_parts.append("<table><tbody>")
            for k, v in value.items():
                html_parts.append(f"<tr><td><strong>{k}</strong></td><td>{str(v)}</td></tr>")
            html_parts.append("</tbody></table>")
        else:
            html_parts.append(f"<p>{str(value)}</p>")
    
    return "".join(html_parts)


def build_confluence_page(confluence_client, space_key: str, title: str, content: str, 
                         parent_id: Optional[str] = None, page_type: str = 'page') -> Dict[str, Any]:
    """
    Safely create a Confluence page with error handling.
    
    Args:
        confluence_client: Atlassian Confluence client
        space_key: Confluence space key
        title: Page title
        content: HTML content
        parent_id: Optional parent page ID
        page_type: Type of page (default 'page')
        
    Returns:
        Created page dictionary
        
    Raises:
        Exception: If page creation fails
    """
    try:
        page = confluence_client.create_page(
            space=space_key,
            title=title,
            body=content,
            parent_id=parent_id,
            type=page_type,
            representation='storage'
        )
        logger.info(f"Created Confluence page: {title} (ID: {page.get('id')})")
        return page
    except Exception as e:
        logger.error(f"Failed to create Confluence page '{title}': {str(e)}")
        raise


def batch_create_pages(confluence_client, space_key: str, pages_config: list, parent_id: Optional[str] = None) -> list:
    """
    Create multiple Confluence pages with error recovery.
    
    Args:
        confluence_client: Atlassian Confluence client
        space_key: Confluence space key
        pages_config: List of dicts with 'title', 'content', and optional 'type'
        parent_id: Optional parent page ID for all pages
        
    Returns:
        List of created pages
    """
    created_pages = []
    
    for page_config in pages_config:
        try:
            page = build_confluence_page(
                confluence_client,
                space_key,
                page_config.get('title', 'Untitled'),
                page_config.get('content', ''),
                parent_id,
                page_config.get('type', 'page')
            )
            created_pages.append(page)
        except Exception as e:
            logger.warning(f"Skipped Confluence page due to error: {str(e)}")
            created_pages.append(None)
    
    return created_pages
