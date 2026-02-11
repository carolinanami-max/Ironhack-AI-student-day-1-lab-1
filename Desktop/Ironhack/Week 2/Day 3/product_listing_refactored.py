"""
Product Listing Generator - Refactored Version
A modular, clean implementation for generating e-commerce product listings using OpenAI API.

Key Improvements:
- Separated concerns (image handling, API calls, file operations)
- Smart JSON extraction from markdown-wrapped responses
- Centralized configuration
- Better error handling with recovery
- Reusable components
- Input validation
"""

import os
import base64
import json
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import io

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import requests


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Centralized configuration for the application."""

    # API Settings
    model_name: str = "gpt-4o-mini"
    max_tokens: int = 800
    temperature: float = 0.7
    request_timeout: int = 30

    # Image Settings
    max_image_size: tuple = (512, 512)
    image_quality: int = 85
    image_format: str = "JPEG"

    # Batch Processing
    batch_delay: float = 1.0  # seconds between requests
    max_retries: int = 3

    # Output Settings
    output_folder: str = "generated_listings"
    save_raw_responses: bool = False


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ProductInfo:
    """Product information container."""
    id: Union[int, str]
    name: str
    price: float
    category: str
    image_path: str
    additional_info: Optional[str] = None

    def validate(self) -> bool:
        """Validate product information."""
        if not self.name or not self.image_path:
            return False
        if self.price < 0:
            return False
        return True


@dataclass
class ProductListing:
    """Generated product listing container."""
    title: str
    description: str
    features: List[str]
    keywords: str

    # Metadata
    product_id: Optional[Union[int, str]] = None
    original_name: Optional[str] = None
    original_price: Optional[float] = None
    category: Optional[str] = None
    generated_at: Optional[str] = None
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)


# ============================================================================
# IMAGE HANDLER
# ============================================================================

class ImageHandler:
    """Handles all image-related operations."""

    def __init__(self, config: Config):
        self.config = config

    def encode_to_base64(self, image_path: str) -> Optional[str]:
        """
        Encode an image to base64 format.

        Args:
            image_path: Path to local image or URL

        Returns:
            Base64 encoded string or None if failed
        """
        try:
            image = self._load_image(image_path)
            if image is None:
                return None

            image = self._process_image(image)
            return self._encode_image(image)

        except Exception as e:
            print(f"❌ Error encoding image {image_path}: {e}")
            return None

    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image from URL or local file."""
        try:
            if isinstance(image_path, str) and image_path.startswith('http'):
                response = requests.get(image_path, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                response.raise_for_status()
                return Image.open(io.BytesIO(response.content))
            else:
                path = Path(image_path)
                if not path.exists():
                    print(f"❌ Image not found: {image_path}")
                    return None
                return Image.open(path)
        except Exception as e:
            print(f"❌ Error loading image: {e}")
            return None

    def _process_image(self, image: Image.Image) -> Image.Image:
        """Resize and convert image as needed."""
        # Resize if too large
        if image.size[0] > self.config.max_image_size[0] or \
           image.size[1] > self.config.max_image_size[1]:
            image.thumbnail(self.config.max_image_size, Image.Resampling.LANCZOS)

        # Convert to RGB if needed
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')

        return image

    def _encode_image(self, image: Image.Image) -> str:
        """Encode PIL Image to base64 string."""
        buffered = io.BytesIO()
        image.save(
            buffered,
            format=self.config.image_format,
            quality=self.config.image_quality
        )
        return base64.b64encode(buffered.getvalue()).decode('utf-8')


# ============================================================================
# PROMPT BUILDER
# ============================================================================

class PromptBuilder:
    """Builds prompts for the API."""

    @staticmethod
    def create_listing_prompt(product: ProductInfo) -> str:
        """Create a prompt for product listing generation."""
        additional = f"- Additional Info: {product.additional_info}\n" if product.additional_info else ""

        return f"""You are an expert e-commerce copywriter. Analyze the product image and create a compelling product listing.

Product Information:
- Name: {product.name}
- Price: ${product.price:.2f}
- Category: {product.category}
{additional}
CRITICAL: Respond with ONLY valid JSON. No markdown, no code blocks, no extra text.

Create this EXACT JSON structure:
{{
    "title": "Catchy product title (60 chars max)",
    "description": "Detailed description mentioning what you see in the image (150-200 words)",
    "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
    "keywords": "keyword1, keyword2, keyword3, keyword4, keyword5, keyword6, keyword7"
}}

Focus on visible details: colors, materials, design elements, and distinctive features."""


# ============================================================================
# JSON EXTRACTOR
# ============================================================================

class JSONExtractor:
    """Intelligently extracts JSON from API responses."""

    @staticmethod
    def extract(response_text: str) -> Optional[dict]:
        """
        Extract JSON from response, handling markdown code blocks.

        Args:
            response_text: Raw API response

        Returns:
            Parsed JSON dict or None if failed
        """
        # Try direct parsing first
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        patterns = [
            r'```json\s*(\{.*?\})\s*```',  # ```json {...} ```
            r'```\s*(\{.*?\})\s*```',       # ``` {...} ```
            r'(\{.*?\})',                   # Just find any {...}
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        print("⚠ Could not extract valid JSON from response")
        return None


# ============================================================================
# API CLIENT
# ============================================================================

class OpenAIClient:
    """Handles all OpenAI API interactions."""

    def __init__(self, api_key: str, config: Config):
        self.client = OpenAI(api_key=api_key)
        self.config = config
        self.json_extractor = JSONExtractor()

    def generate_listing(
        self,
        image_base64: str,
        prompt: str
    ) -> Dict[str, any]:
        """
        Call OpenAI API to generate product listing.

        Args:
            image_base64: Base64 encoded image
            prompt: Text prompt

        Returns:
            Dictionary with success status and response/error
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Try to extract JSON
            listing_data = self.json_extractor.extract(content)

            return {
                "success": True,
                "listing_data": listing_data,
                "raw_response": content,
                "tokens_used": tokens_used
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================================
# FILE MANAGER
# ============================================================================

class FileManager:
    """Handles all file operations."""

    def __init__(self, output_folder: str):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

    def save_listing(
        self,
        listing: ProductListing,
        product_id: Union[int, str]
    ) -> Path:
        """Save product listing to JSON file."""
        filename = self.output_folder / f"product_{product_id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(listing.to_dict(), f, indent=2, ensure_ascii=False)
        return filename

    def save_raw_response(
        self,
        response: str,
        product_id: Union[int, str]
    ) -> Path:
        """Save raw API response to text file."""
        filename = self.output_folder / f"product_{product_id}_raw.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response)
        return filename

    def save_summary(self, summary: dict) -> Path:
        """Save processing summary."""
        filename = self.output_folder / "summary.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        return filename


# ============================================================================
# PRODUCT LISTING GENERATOR
# ============================================================================

class ProductListingGenerator:
    """Main class that orchestrates product listing generation."""

    def __init__(self, api_key: str, config: Optional[Config] = None):
        self.config = config or Config()
        self.image_handler = ImageHandler(self.config)
        self.prompt_builder = PromptBuilder()
        self.api_client = OpenAIClient(api_key, self.config)
        self.file_manager = FileManager(self.config.output_folder)

    def process_single(self, product: ProductInfo) -> Optional[ProductListing]:
        """
        Process a single product.

        Args:
            product: ProductInfo object

        Returns:
            ProductListing object or None if failed
        """
        # Validate input
        if not product.validate():
            print(f"❌ Invalid product info for {product.name}")
            return None

        print(f"\n📦 Processing: {product.name}")

        # Encode image
        print("  📷 Encoding image...")
        image_base64 = self.image_handler.encode_to_base64(product.image_path)
        if not image_base64:
            print("  ❌ Image encoding failed")
            return None
        print("  ✅ Image encoded")

        # Create prompt
        prompt = self.prompt_builder.create_listing_prompt(product)

        # Call API
        print("  🔄 Calling OpenAI API...")
        result = self.api_client.generate_listing(image_base64, prompt)

        if not result["success"]:
            print(f"  ❌ API call failed: {result['error']}")
            return None

        print(f"  ✅ API call successful ({result['tokens_used']} tokens)")

        # Process response
        listing_data = result["listing_data"]
        if not listing_data:
            print("  ⚠ Could not parse JSON, saving raw response")
            if self.config.save_raw_responses:
                self.file_manager.save_raw_response(
                    result["raw_response"],
                    product.id
                )
            return None

        # Create ProductListing object
        listing = ProductListing(
            title=listing_data.get("title", ""),
            description=listing_data.get("description", ""),
            features=listing_data.get("features", []),
            keywords=listing_data.get("keywords", ""),
            product_id=product.id,
            original_name=product.name,
            original_price=product.price,
            category=product.category,
            generated_at=datetime.now().isoformat(),
            model_used=self.config.model_name,
            tokens_used=result["tokens_used"]
        )

        # Save to file
        saved_path = self.file_manager.save_listing(listing, product.id)
        print(f"  💾 Saved: {saved_path}")

        return listing

    def process_batch(
        self,
        products: List[ProductInfo],
        show_progress: bool = True
    ) -> Dict[str, any]:
        """
        Process multiple products in batch.

        Args:
            products: List of ProductInfo objects
            show_progress: Whether to print progress

        Returns:
            Dictionary with results and statistics
        """
        results = []
        failed = []

        if show_progress:
            print(f"\n{'='*60}")
            print(f"🚀 Starting batch processing: {len(products)} products")
            print('='*60)

        for i, product in enumerate(products, 1):
            if show_progress:
                print(f"\n[{i}/{len(products)}]", end=" ")

            try:
                listing = self.process_single(product)

                if listing:
                    results.append(listing)
                else:
                    failed.append({
                        "id": product.id,
                        "name": product.name,
                        "error": "Processing failed"
                    })

            except Exception as e:
                print(f"  ❌ Unexpected error: {e}")
                failed.append({
                    "id": product.id,
                    "name": product.name,
                    "error": str(e)
                })

            # Delay between requests
            if i < len(products):
                time.sleep(self.config.batch_delay)

        # Create summary
        summary = {
            "total_products": len(products),
            "successful": len(results),
            "failed": len(failed),
            "success_rate": f"{(len(results)/len(products)*100):.1f}%" if products else "0%",
            "total_tokens": sum(r.tokens_used or 0 for r in results),
            "timestamp": datetime.now().isoformat(),
            "model_used": self.config.model_name,
            "failed_products": failed
        }

        # Save summary
        self.file_manager.save_summary(summary)

        if show_progress:
            print(f"\n{'='*60}")
            print("🎉 Batch Processing Complete!")
            print('='*60)
            print(f"📊 Summary:")
            print(f"  ✅ Successful: {len(results)}/{len(products)}")
            print(f"  ❌ Failed: {len(failed)}")
            print(f"  📈 Success Rate: {summary['success_rate']}")
            print(f"  🔢 Total Tokens: {summary['total_tokens']}")
            print(f"  📁 Output: {self.config.output_folder}/")

        return {
            "results": results,
            "failed": failed,
            "summary": summary
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_api_key(env_file: str = ".env") -> Optional[str]:
    """Load API key from environment."""
    load_dotenv(env_file)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return None

    return api_key


def create_sample_products() -> List[ProductInfo]:
    """Create sample product data for testing."""
    return [
        ProductInfo(
            id=1,
            name="Premium Wireless Headphones",
            price=129.99,
            category="Electronics",
            image_path="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
            additional_info="Noise cancelling, 40-hour battery"
        ),
        ProductInfo(
            id=2,
            name="Running Shoes",
            price=89.99,
            category="Sports",
            image_path="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            additional_info="Lightweight, breathable mesh"
        ),
        ProductInfo(
            id=3,
            name="Office Chair",
            price=199.99,
            category="Furniture",
            image_path="https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
            additional_info="Ergonomic design, adjustable height"
        )
    ]


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function for testing."""
    print("="*60)
    print("PRODUCT LISTING GENERATOR - REFACTORED VERSION")
    print("="*60)

    # Load API key
    api_key = load_api_key()
    if not api_key:
        return

    print(f"✅ API Key loaded: {api_key[:12]}...")

    # Create configuration
    config = Config(
        model_name="gpt-4o-mini",
        batch_delay=1.0,
        output_folder="generated_listings_refactored",
        save_raw_responses=True
    )

    # Initialize generator
    generator = ProductListingGenerator(api_key, config)

    # Get sample products
    products = create_sample_products()

    # Process batch
    result = generator.process_batch(products)

    # Display sample result
    if result["results"]:
        print(f"\n📋 Sample Result:")
        sample = result["results"][0]
        print(f"  Product: {sample.original_name}")
        print(f"  Title: {sample.title}")
        print(f"  Features: {len(sample.features)} items")
        for i, feature in enumerate(sample.features[:3], 1):
            print(f"    {i}. {feature[:50]}...")


if __name__ == "__main__":
    main()
