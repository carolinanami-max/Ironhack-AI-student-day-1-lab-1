# Quick Start Guide - Refactored Product Listing Generator

## Installation

```bash
pip install openai python-dotenv pillow requests
```

## Basic Setup

1. **Create `.env` file** in your project root:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

2. **Import the module:**
```python
from product_listing_refactored import (
    ProductListingGenerator,
    ProductInfo,
    Config,
    load_api_key
)
```

---

## Usage Examples

### Example 1: Single Product

```python
# Load API key
api_key = load_api_key()

# Create generator
generator = ProductListingGenerator(api_key)

# Define product
product = ProductInfo(
    id=1,
    name="Wireless Bluetooth Speaker",
    price=79.99,
    category="Electronics",
    image_path="https://example.com/speaker.jpg",
    additional_info="360° sound, waterproof"
)

# Generate listing
listing = generator.process_single(product)

# Access results
print(listing.title)
print(listing.description)
print(listing.features)
```

---

### Example 2: Batch Processing

```python
# Define multiple products
products = [
    ProductInfo(
        id=1,
        name="Wireless Headphones",
        price=129.99,
        category="Electronics",
        image_path="url_or_path_to_image_1"
    ),
    ProductInfo(
        id=2,
        name="Running Shoes",
        price=89.99,
        category="Sports",
        image_path="url_or_path_to_image_2"
    ),
    ProductInfo(
        id=3,
        name="Coffee Maker",
        price=149.99,
        category="Home Appliances",
        image_path="url_or_path_to_image_3"
    ),
]

# Process all products
result = generator.process_batch(products)

# Check results
print(f"Successful: {len(result['results'])}")
print(f"Failed: {len(result['failed'])}")

# Access individual results
for listing in result['results']:
    print(f"{listing.original_name}: {listing.title}")
```

---

### Example 3: Custom Configuration

```python
# Create custom configuration
config = Config(
    model_name="gpt-4o-mini",      # Model to use
    max_tokens=1000,                # Max response tokens
    temperature=0.7,                # Creativity level
    max_image_size=(768, 768),      # Larger images
    image_quality=90,               # Higher quality
    batch_delay=2.0,                # 2 seconds between requests
    output_folder="my_listings",    # Custom output folder
    save_raw_responses=True         # Save raw API responses
)

# Use custom config
generator = ProductListingGenerator(api_key, config)
result = generator.process_batch(products)
```

---

### Example 4: Using Components Separately

#### A. Image Encoding Only

```python
from product_listing_refactored import ImageHandler, Config

config = Config()
image_handler = ImageHandler(config)

# Encode image
base64_string = image_handler.encode_to_base64("path/to/image.jpg")
print(f"Encoded {len(base64_string)} characters")
```

#### B. JSON Extraction Only

```python
from product_listing_refactored import JSONExtractor

extractor = JSONExtractor()

# Extract JSON from markdown response
response = '''```json
{
    "title": "Great Product",
    "description": "Amazing features"
}
```'''

data = extractor.extract(response)
print(data['title'])  # "Great Product"
```

#### C. Prompt Building Only

```python
from product_listing_refactored import PromptBuilder, ProductInfo

product = ProductInfo(
    id=1,
    name="Smartwatch",
    price=299.99,
    category="Wearables",
    image_path="path/to/image.jpg",
    additional_info="Heart rate monitor, GPS"
)

prompt = PromptBuilder.create_listing_prompt(product)
print(prompt)
```

---

### Example 5: From HuggingFace Dataset

```python
from datasets import load_dataset
from product_listing_refactored import ProductListingGenerator, ProductInfo, load_api_key

# Load dataset
ds = load_dataset("ashraq/fashion-product-images-small", split="train")

# Convert to ProductInfo objects
products = []
for i, item in enumerate(ds.select(range(10))):  # First 10 items
    products.append(ProductInfo(
        id=item['id'],
        name=item['productDisplayName'],
        price=99.99,  # You'd get real price from your data
        category=item['masterCategory'],
        image_path=item['image'],  # PIL Image object
        additional_info=f"{item['articleType']} - {item['baseColour']}"
    ))

# Process batch
api_key = load_api_key()
generator = ProductListingGenerator(api_key)
result = generator.process_batch(products)

print(f"Processed {len(result['results'])} fashion items")
```

---

### Example 6: Error Handling

```python
# Process with error handling
try:
    listing = generator.process_single(product)

    if listing:
        print(f"✅ Success: {listing.title}")
        print(f"Tokens used: {listing.tokens_used}")
    else:
        print("❌ Failed to generate listing")

except Exception as e:
    print(f"❌ Error: {e}")
```

---

### Example 7: Accessing Generated Files

```python
import json

# Process products
result = generator.process_batch(products)

# Read generated JSON files
with open('generated_listings_refactored/product_1.json', 'r') as f:
    listing = json.load(f)
    print(listing['title'])
    print(listing['description'])
    print(listing['features'])

# Read summary
with open('generated_listings_refactored/summary.json', 'r') as f:
    summary = json.load(f)
    print(f"Total tokens used: {summary['total_tokens']}")
    print(f"Success rate: {summary['success_rate']}")
```

---

## Common Use Cases

### Use Case 1: E-commerce Website Integration

```python
def import_products_from_csv(csv_path):
    """Import products from CSV and generate listings"""
    import pandas as pd

    df = pd.read_csv(csv_path)
    products = []

    for _, row in df.iterrows():
        products.append(ProductInfo(
            id=row['product_id'],
            name=row['product_name'],
            price=row['price'],
            category=row['category'],
            image_path=row['image_url']
        ))

    generator = ProductListingGenerator(load_api_key())
    return generator.process_batch(products)

# Usage
result = import_products_from_csv('products.csv')
```

### Use Case 2: Update Existing Products

```python
def update_product_listings(product_ids, database):
    """Update listings for specific products"""

    products = []
    for pid in product_ids:
        product_data = database.get_product(pid)
        products.append(ProductInfo(
            id=pid,
            name=product_data['name'],
            price=product_data['price'],
            category=product_data['category'],
            image_path=product_data['image_url']
        ))

    generator = ProductListingGenerator(load_api_key())
    result = generator.process_batch(products)

    # Save to database
    for listing in result['results']:
        database.update_listing(
            product_id=listing.product_id,
            title=listing.title,
            description=listing.description,
            features=listing.features
        )
```

### Use Case 3: A/B Testing Different Prompts

```python
class CustomPromptBuilder(PromptBuilder):
    """Custom prompt for specific brand voice"""

    @staticmethod
    def create_listing_prompt(product):
        return f"""You are a luxury brand copywriter...

Product: {product.name}
Price: ${product.price}

Create an EXCLUSIVE, premium listing..."""

# Use custom prompt
from product_listing_refactored import ProductListingGenerator

class CustomGenerator(ProductListingGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt_builder = CustomPromptBuilder()

generator = CustomGenerator(api_key)
```

---

## Output Structure

Each generated listing is saved as JSON:

```json
{
  "title": "Product Title Here",
  "description": "Detailed description...",
  "features": [
    "Feature 1",
    "Feature 2",
    "Feature 3"
  ],
  "keywords": "keyword1, keyword2, keyword3",
  "product_id": 1,
  "original_name": "Original Product Name",
  "original_price": 99.99,
  "category": "Electronics",
  "generated_at": "2026-02-11T15:40:44.662520",
  "model_used": "gpt-4o-mini",
  "tokens_used": 8934
}
```

---

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_name` | str | "gpt-4o-mini" | OpenAI model to use |
| `max_tokens` | int | 800 | Max tokens in response |
| `temperature` | float | 0.7 | Creativity (0-1) |
| `request_timeout` | int | 30 | API timeout (seconds) |
| `max_image_size` | tuple | (512, 512) | Max image dimensions |
| `image_quality` | int | 85 | JPEG quality (1-100) |
| `image_format` | str | "JPEG" | Output format |
| `batch_delay` | float | 1.0 | Delay between requests |
| `max_retries` | int | 3 | Max retry attempts |
| `output_folder` | str | "generated_listings" | Output directory |
| `save_raw_responses` | bool | False | Save raw API responses |

---

## Troubleshooting

### Issue: API Key Not Found

```python
# Solution 1: Check .env file exists
import os
print(os.path.exists('.env'))

# Solution 2: Load from different location
from dotenv import load_dotenv
load_dotenv('/path/to/.env')

# Solution 3: Set directly
os.environ['OPENAI_API_KEY'] = 'sk-...'
```

### Issue: Image Loading Failed

```python
# Solution: Check image path/URL
from product_listing_refactored import ImageHandler, Config

handler = ImageHandler(Config())
result = handler.encode_to_base64(image_path)

if result is None:
    print("Image loading failed")
    # Check if URL is accessible
    # Check if file exists
    # Check file format
```

### Issue: JSON Parsing Failed

```python
# The refactored code handles this automatically
# But you can also use JSONExtractor directly

from product_listing_refactored import JSONExtractor

extractor = JSONExtractor()
data = extractor.extract(api_response)

if data is None:
    print("Could not extract JSON")
    print("Raw response:", api_response)
```

---

## Performance Tips

1. **Reduce Image Size** for faster processing:
   ```python
   config = Config(max_image_size=(256, 256))
   ```

2. **Increase Batch Delay** to avoid rate limits:
   ```python
   config = Config(batch_delay=2.0)
   ```

3. **Use Lower Temperature** for more consistent results:
   ```python
   config = Config(temperature=0.3)
   ```

4. **Save Raw Responses** for debugging:
   ```python
   config = Config(save_raw_responses=True)
   ```

---

## Testing

```python
# Test with sample products
from product_listing_refactored import create_sample_products

products = create_sample_products()
print(f"Loaded {len(products)} sample products")

generator = ProductListingGenerator(load_api_key())
result = generator.process_batch(products)

assert len(result['results']) == 3, "Should process all samples"
assert result['summary']['success_rate'] == "100.0%", "Should succeed"
```

---

## Need Help?

- Check [REFACTORING_REPORT.md](REFACTORING_REPORT.md) for detailed analysis
- Review the code in [product_listing_refactored.py](product_listing_refactored.py)
- All functions have docstrings explaining usage
- Use type hints for IDE autocomplete

---

**Last Updated:** 2026-02-11
**Version:** 1.0
**Status:** Production Ready ✅
