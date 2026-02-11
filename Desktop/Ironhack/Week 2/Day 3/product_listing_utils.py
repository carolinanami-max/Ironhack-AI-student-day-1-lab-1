"""
Product Listing Utilities - Modular Reusable Functions
Separated components for maximum reusability and testability.

Usage:
    from product_listing_utils import (
        ImageProcessor,
        JSONParser,
        PromptGenerator,
        APIHandler,
        FileHandler,
        validate_product_data
    )
"""

import os
import base64
import json
import re
import io
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict

from PIL import Image
import requests


# ============================================================================
# CONFIGURATION & DATA MODELS
# ============================================================================

@dataclass
class ProductData:
    """Lightweight product data container."""
    id: Union[int, str]
    name: str
    price: float
    category: str
    image_path: str
    additional_info: Optional[str] = None


@dataclass
class ListingData:
    """Generated listing data container."""
    title: str
    description: str
    features: List[str]
    keywords: str


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_product_data(product: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate product data dictionary.

    Args:
        product: Dictionary with product information

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['id', 'name', 'price', 'category', 'image_path']

    # Check required fields
    for field in required_fields:
        if field not in product:
            return False, f"Missing required field: {field}"

    # Check name is not empty
    if not product['name'] or not str(product['name']).strip():
        return False, "Product name cannot be empty"

    # Check price is valid
    try:
        price = float(product['price'])
        if price < 0:
            return False, "Price cannot be negative"
    except (ValueError, TypeError):
        return False, "Price must be a valid number"

    # Check image path is not empty
    if not product['image_path'] or not str(product['image_path']).strip():
        return False, "Image path cannot be empty"

    return True, None


def validate_listing_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate generated listing data.

    Args:
        data: Dictionary with listing information

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['title', 'description', 'features', 'keywords']

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate title
    if not data['title'] or len(data['title']) > 100:
        return False, "Title must be 1-100 characters"

    # Validate description
    if not data['description'] or len(data['description']) < 50:
        return False, "Description must be at least 50 characters"

    # Validate features
    if not isinstance(data['features'], list) or len(data['features']) == 0:
        return False, "Features must be a non-empty list"

    # Validate keywords
    if not data['keywords'] or not isinstance(data['keywords'], str):
        return False, "Keywords must be a non-empty string"

    return True, None


# ============================================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================================

class ImageProcessor:
    """Reusable image processing functions."""

    @staticmethod
    def load_image_from_url(
        url: str,
        timeout: int = 10,
        user_agent: str = 'Mozilla/5.0'
    ) -> Optional[Image.Image]:
        """
        Load image from URL.

        Args:
            url: Image URL
            timeout: Request timeout in seconds
            user_agent: User agent string

        Returns:
            PIL Image or None if failed
        """
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={'User-Agent': user_agent}
            )
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        except Exception as e:
            print(f"❌ Error loading image from URL: {e}")
            return None

    @staticmethod
    def load_image_from_file(file_path: str) -> Optional[Image.Image]:
        """
        Load image from local file.

        Args:
            file_path: Path to image file

        Returns:
            PIL Image or None if failed
        """
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                return None
            return Image.open(path)
        except Exception as e:
            print(f"❌ Error loading image from file: {e}")
            return None

    @staticmethod
    def load_image(image_source: str) -> Optional[Image.Image]:
        """
        Load image from URL or file path.

        Args:
            image_source: URL or file path

        Returns:
            PIL Image or None if failed
        """
        if isinstance(image_source, str) and image_source.startswith('http'):
            return ImageProcessor.load_image_from_url(image_source)
        else:
            return ImageProcessor.load_image_from_file(image_source)

    @staticmethod
    def resize_image(
        image: Image.Image,
        max_size: Tuple[int, int] = (512, 512),
        resample: int = Image.Resampling.LANCZOS
    ) -> Image.Image:
        """
        Resize image if larger than max_size.

        Args:
            image: PIL Image
            max_size: Maximum dimensions (width, height)
            resample: Resampling filter

        Returns:
            Resized PIL Image
        """
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, resample)
        return image

    @staticmethod
    def convert_to_rgb(image: Image.Image) -> Image.Image:
        """
        Convert image to RGB mode if needed.

        Args:
            image: PIL Image

        Returns:
            RGB PIL Image
        """
        if image.mode not in ('RGB', 'L'):
            return image.convert('RGB')
        return image

    @staticmethod
    def image_to_base64(
        image: Image.Image,
        format: str = "JPEG",
        quality: int = 85
    ) -> str:
        """
        Convert PIL Image to base64 string.

        Args:
            image: PIL Image
            format: Output format (JPEG, PNG, etc.)
            quality: JPEG quality (1-100)

        Returns:
            Base64 encoded string
        """
        buffered = io.BytesIO()
        image.save(buffered, format=format, quality=quality)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    @staticmethod
    def process_and_encode(
        image_source: str,
        max_size: Tuple[int, int] = (512, 512),
        quality: int = 85
    ) -> Optional[str]:
        """
        Complete pipeline: load, resize, convert, and encode image.

        Args:
            image_source: URL or file path
            max_size: Maximum dimensions
            quality: JPEG quality

        Returns:
            Base64 encoded string or None if failed
        """
        try:
            # Load image
            image = ImageProcessor.load_image(image_source)
            if image is None:
                return None

            # Resize
            image = ImageProcessor.resize_image(image, max_size)

            # Convert to RGB
            image = ImageProcessor.convert_to_rgb(image)

            # Encode
            return ImageProcessor.image_to_base64(image, quality=quality)

        except Exception as e:
            print(f"❌ Error processing image: {e}")
            return None


# ============================================================================
# JSON PARSING FUNCTIONS
# ============================================================================

class JSONParser:
    """Reusable JSON extraction functions."""

    @staticmethod
    def parse_json(text: str) -> Optional[Dict]:
        """
        Parse JSON string directly.

        Args:
            text: JSON string

        Returns:
            Parsed dictionary or None
        """
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def extract_from_markdown(text: str) -> Optional[str]:
        """
        Extract JSON from markdown code blocks.

        Args:
            text: Text containing markdown code blocks

        Returns:
            Extracted JSON string or None
        """
        patterns = [
            r'```json\s*(\{.*?\})\s*```',  # ```json {...} ```
            r'```\s*(\{.*?\})\s*```',       # ``` {...} ```
            r'(\{.*?\})',                   # Just {...}
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1)

        return None

    @staticmethod
    def smart_parse(text: str) -> Optional[Dict]:
        """
        Intelligently parse JSON from various formats.

        Args:
            text: Text containing JSON

        Returns:
            Parsed dictionary or None
        """
        # Try direct parsing
        result = JSONParser.parse_json(text)
        if result:
            return result

        # Try extracting from markdown
        json_str = JSONParser.extract_from_markdown(text)
        if json_str:
            result = JSONParser.parse_json(json_str)
            if result:
                return result

        return None

    @staticmethod
    def extract_fields(
        data: Dict,
        required_fields: List[str],
        default_value: any = None
    ) -> Dict:
        """
        Extract specific fields from dictionary with defaults.

        Args:
            data: Source dictionary
            required_fields: List of field names to extract
            default_value: Default value for missing fields

        Returns:
            Dictionary with extracted fields
        """
        return {
            field: data.get(field, default_value)
            for field in required_fields
        }


# ============================================================================
# PROMPT GENERATION FUNCTIONS
# ============================================================================

class PromptGenerator:
    """Reusable prompt generation functions."""

    @staticmethod
    def create_basic_prompt(
        product_name: str,
        price: float,
        category: str
    ) -> str:
        """
        Create a basic product listing prompt.

        Args:
            product_name: Name of the product
            price: Product price
            category: Product category

        Returns:
            Prompt string
        """
        return f"""Create a product listing for:
- Name: {product_name}
- Price: ${price:.2f}
- Category: {category}

Respond with JSON only."""

    @staticmethod
    def create_detailed_prompt(
        product_name: str,
        price: float,
        category: str,
        additional_info: Optional[str] = None,
        include_seo: bool = True,
        word_count: int = 150
    ) -> str:
        """
        Create a detailed product listing prompt.

        Args:
            product_name: Name of the product
            price: Product price
            category: Product category
            additional_info: Additional product information
            include_seo: Whether to include SEO keywords
            word_count: Target word count for description

        Returns:
            Detailed prompt string
        """
        additional = f"- Additional Info: {additional_info}\n" if additional_info else ""
        seo_section = '"keywords": "comma,separated,keywords"' if include_seo else ""

        return f"""You are an expert e-commerce copywriter. Analyze the product image and create a compelling listing.

Product Information:
- Name: {product_name}
- Price: ${price:.2f}
- Category: {category}
{additional}
CRITICAL: Respond with ONLY valid JSON. No markdown, no code blocks, no extra text.

Create this EXACT JSON structure:
{{
    "title": "Catchy product title (60 chars max)",
    "description": "Detailed description ({word_count}-{word_count+50} words)",
    "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
    {seo_section}
}}

Focus on visible details in the image: colors, materials, design, distinctive features."""

    @staticmethod
    def create_custom_prompt(
        template: str,
        variables: Dict[str, any]
    ) -> str:
        """
        Create prompt from custom template.

        Args:
            template: Prompt template with {variable} placeholders
            variables: Dictionary of variable values

        Returns:
            Formatted prompt string
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            print(f"⚠ Missing variable in template: {e}")
            return template


# ============================================================================
# API HANDLER FUNCTIONS
# ============================================================================

class APIHandler:
    """Reusable API interaction functions."""

    @staticmethod
    def create_vision_message(
        prompt: str,
        image_base64: str,
        detail: str = "high"
    ) -> List[Dict]:
        """
        Create message format for vision API.

        Args:
            prompt: Text prompt
            image_base64: Base64 encoded image
            detail: Image detail level ("low", "high", "auto")

        Returns:
            List of message dictionaries
        """
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": detail
                        }
                    }
                ]
            }
        ]

    @staticmethod
    def parse_api_response(response: any) -> Dict[str, any]:
        """
        Parse OpenAI API response.

        Args:
            response: OpenAI API response object

        Returns:
            Dictionary with parsed data
        """
        try:
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            print(f"❌ Error parsing API response: {e}")
            return {}

    @staticmethod
    def calculate_cost(
        tokens_used: int,
        model: str = "gpt-4o-mini"
    ) -> float:
        """
        Calculate approximate API cost.

        Args:
            tokens_used: Number of tokens used
            model: Model name

        Returns:
            Estimated cost in USD
        """
        # Approximate pricing (as of 2024)
        pricing = {
            "gpt-4o-mini": 0.00015 / 1000,  # $0.15 per 1M tokens
            "gpt-4o": 0.0025 / 1000,         # $2.50 per 1M tokens
            "gpt-4": 0.03 / 1000,            # $30 per 1M tokens
        }

        rate = pricing.get(model, 0.0001)
        return tokens_used * rate


# ============================================================================
# FILE HANDLING FUNCTIONS
# ============================================================================

class FileHandler:
    """Reusable file operation functions."""

    @staticmethod
    def ensure_directory(directory: str) -> Path:
        """
        Ensure directory exists, create if not.

        Args:
            directory: Directory path

        Returns:
            Path object
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def save_json(
        data: Dict,
        filepath: str,
        indent: int = 2,
        ensure_ascii: bool = False
    ) -> bool:
        """
        Save dictionary as JSON file.

        Args:
            data: Dictionary to save
            filepath: Output file path
            indent: JSON indentation
            ensure_ascii: Whether to escape non-ASCII

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
            return True
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return False

    @staticmethod
    def load_json(filepath: str) -> Optional[Dict]:
        """
        Load JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Loaded dictionary or None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading JSON: {e}")
            return None

    @staticmethod
    def save_text(text: str, filepath: str) -> bool:
        """
        Save text to file.

        Args:
            text: Text content
            filepath: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            print(f"❌ Error saving text: {e}")
            return False

    @staticmethod
    def load_text(filepath: str) -> Optional[str]:
        """
        Load text from file.

        Args:
            filepath: Path to text file

        Returns:
            File contents or None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error loading text: {e}")
            return None

    @staticmethod
    def list_files(
        directory: str,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """
        List files in directory matching pattern.

        Args:
            directory: Directory to search
            pattern: Glob pattern
            recursive: Whether to search recursively

        Returns:
            List of Path objects
        """
        path = Path(directory)
        if not path.exists():
            return []

        if recursive:
            return list(path.rglob(pattern))
        else:
            return list(path.glob(pattern))


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Variable number of dictionaries

    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def filter_dict(data: Dict, keys: List[str]) -> Dict:
    """
    Filter dictionary to only include specified keys.

    Args:
        data: Source dictionary
        keys: List of keys to keep

    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k in keys}


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace.

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncating

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_price(price: float, currency: str = "$") -> str:
    """
    Format price as currency string.

    Args:
        price: Price value
        currency: Currency symbol

    Returns:
        Formatted price string
    """
    return f"{currency}{price:.2f}"


def calculate_statistics(numbers: List[Union[int, float]]) -> Dict[str, float]:
    """
    Calculate basic statistics for a list of numbers.

    Args:
        numbers: List of numbers

    Returns:
        Dictionary with statistics
    """
    if not numbers:
        return {}

    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }


# ============================================================================
# BATCH PROCESSING HELPERS
# ============================================================================

def batch_items(items: List, batch_size: int) -> List[List]:
    """
    Split list into batches.

    Args:
        items: List to batch
        batch_size: Size of each batch

    Returns:
        List of batches
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def progress_tracker(current: int, total: int, prefix: str = "") -> str:
    """
    Create progress string.

    Args:
        current: Current item number
        total: Total items
        prefix: Optional prefix

    Returns:
        Progress string
    """
    percentage = (current / total * 100) if total > 0 else 0
    return f"{prefix}[{current}/{total}] {percentage:.1f}%"


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PRODUCT LISTING UTILS - REUSABLE FUNCTIONS")
    print("=" * 60)

    # Example 1: Image Processing
    print("\n1. Image Processing Example:")
    image_url = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"
    base64_img = ImageProcessor.process_and_encode(image_url)
    if base64_img:
        print(f"✅ Image encoded: {len(base64_img)} characters")

    # Example 2: JSON Parsing
    print("\n2. JSON Parsing Example:")
    json_text = '''```json
    {
        "title": "Test Product",
        "description": "A great product",
        "features": ["Feature 1", "Feature 2"],
        "keywords": "test, product"
    }
    ```'''
    parsed = JSONParser.smart_parse(json_text)
    if parsed:
        print(f"✅ JSON parsed: {parsed['title']}")

    # Example 3: Prompt Generation
    print("\n3. Prompt Generation Example:")
    prompt = PromptGenerator.create_detailed_prompt(
        "Wireless Headphones",
        129.99,
        "Electronics",
        "Noise cancelling"
    )
    print(f"✅ Prompt created: {len(prompt)} characters")

    # Example 4: File Operations
    print("\n4. File Operations Example:")
    test_data = {"test": "data"}
    FileHandler.ensure_directory("test_output")
    success = FileHandler.save_json(test_data, "test_output/test.json")
    if success:
        print("✅ File saved successfully")

    # Example 5: Validation
    print("\n5. Validation Example:")
    product = {
        "id": 1,
        "name": "Test Product",
        "price": 99.99,
        "category": "Electronics",
        "image_path": "test.jpg"
    }
    is_valid, error = validate_product_data(product)
    print(f"✅ Validation: {is_valid}")

    print("\n" + "=" * 60)
    print("All utility functions are ready to use!")
    print("=" * 60)
