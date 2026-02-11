# Modular Product Listing Utils - Usage Guide

## Overview

The code has been refactored into **highly reusable, modular functions** that can be used independently or combined. All 47 tests pass successfully!

---

## Files Created

### 1. [product_listing_utils.py](product_listing_utils.py)
**Reusable utility functions organized by purpose**

- ✅ **ImageProcessor**: All image operations
- ✅ **JSONParser**: Smart JSON extraction
- ✅ **PromptGenerator**: Flexible prompt creation
- ✅ **APIHandler**: API interaction helpers
- ✅ **FileHandler**: File I/O operations
- ✅ **Validation Functions**: Data validation
- ✅ **Utility Functions**: General helpers

### 2. [test.py](test.py)
**Comprehensive test suite with 47 tests**

- ✅ All tests pass (47/47)
- ✅ Tests cover all utility functions
- ✅ Includes edge cases and error handling
- ✅ Mock external dependencies (API, HTTP)

---

## Quick Start Examples

### Example 1: Use Image Processor Only

```python
from product_listing_utils import ImageProcessor

# Process any image (URL or local file)
base64_img = ImageProcessor.process_and_encode(
    "https://example.com/image.jpg",
    max_size=(512, 512),
    quality=85
)

if base64_img:
    print(f"Image encoded: {len(base64_img)} chars")
```

**Functions available:**
- `load_image()` - Load from URL or file
- `resize_image()` - Resize with quality preservation
- `convert_to_rgb()` - Convert any format to RGB
- `image_to_base64()` - Encode to base64
- `process_and_encode()` - Complete pipeline

---

### Example 2: Use JSON Parser Only

```python
from product_listing_utils import JSONParser

# Handle any JSON format (direct, markdown-wrapped, etc.)
api_response = '''```json
{
    "title": "Product Name",
    "description": "Great product",
    "features": ["Feature 1", "Feature 2"]
}
```'''

data = JSONParser.smart_parse(api_response)
print(data['title'])  # "Product Name"

# Extract specific fields with defaults
fields = JSONParser.extract_fields(
    data,
    ['title', 'description', 'price'],
    default_value="N/A"
)
```

**Functions available:**
- `parse_json()` - Direct JSON parsing
- `extract_from_markdown()` - Extract from code blocks
- `smart_parse()` - Tries multiple methods
- `extract_fields()` - Get specific fields with defaults

---

### Example 3: Use Prompt Generator Only

```python
from product_listing_utils import PromptGenerator

# Create a basic prompt
basic = PromptGenerator.create_basic_prompt(
    "Wireless Mouse",
    29.99,
    "Electronics"
)

# Create a detailed prompt
detailed = PromptGenerator.create_detailed_prompt(
    product_name="Wireless Headphones",
    price=129.99,
    category="Audio",
    additional_info="Noise cancelling, 40-hour battery",
    include_seo=True,
    word_count=150
)

# Create a custom prompt from template
template = "Sell me a {product} for {price} in {category}"
custom = PromptGenerator.create_custom_prompt(
    template,
    {"product": "smartwatch", "price": "$299", "category": "Wearables"}
)
```

**Functions available:**
- `create_basic_prompt()` - Simple prompts
- `create_detailed_prompt()` - Full-featured prompts
- `create_custom_prompt()` - Template-based prompts

---

### Example 4: Use File Handler Only

```python
from product_listing_utils import FileHandler

# Ensure directory exists
FileHandler.ensure_directory("output/products")

# Save JSON
data = {"product": "Widget", "price": 99.99}
FileHandler.save_json(data, "output/products/widget.json")

# Load JSON
loaded = FileHandler.load_json("output/products/widget.json")

# Save text
FileHandler.save_text("Product description", "output/desc.txt")

# List all JSON files
json_files = FileHandler.list_files("output/products", "*.json")
print(f"Found {len(json_files)} JSON files")
```

**Functions available:**
- `ensure_directory()` - Create directories
- `save_json()` / `load_json()` - JSON operations
- `save_text()` / `load_text()` - Text operations
- `list_files()` - Find files with patterns

---

### Example 5: Validation Functions

```python
from product_listing_utils import validate_product_data, validate_listing_data

# Validate product data before processing
product = {
    "id": 1,
    "name": "Wireless Mouse",
    "price": 29.99,
    "category": "Electronics",
    "image_path": "mouse.jpg"
}

is_valid, error = validate_product_data(product)
if not is_valid:
    print(f"Validation failed: {error}")
else:
    print("Product data is valid!")

# Validate generated listing
listing = {
    "title": "Amazing Wireless Mouse",
    "description": "A great mouse with excellent features...",
    "features": ["Feature 1", "Feature 2"],
    "keywords": "mouse, wireless, computer"
}

is_valid, error = validate_listing_data(listing)
```

**Functions available:**
- `validate_product_data()` - Validate input
- `validate_listing_data()` - Validate output

---

### Example 6: Combine Multiple Utilities

```python
from product_listing_utils import (
    ImageProcessor,
    JSONParser,
    PromptGenerator,
    FileHandler,
    validate_product_data
)

# 1. Validate product
product = {
    "id": 1,
    "name": "Smart Watch",
    "price": 299.99,
    "category": "Wearables",
    "image_path": "https://example.com/watch.jpg"
}

is_valid, error = validate_product_data(product)
if not is_valid:
    print(f"Error: {error}")
    exit(1)

# 2. Process image
image_base64 = ImageProcessor.process_and_encode(
    product['image_path'],
    max_size=(768, 768)
)

# 3. Generate prompt
prompt = PromptGenerator.create_detailed_prompt(
    product['name'],
    product['price'],
    product['category']
)

# 4. Parse API response (example)
api_response = get_api_response(prompt, image_base64)  # Your API call
listing_data = JSONParser.smart_parse(api_response)

# 5. Save result
if listing_data:
    FileHandler.ensure_directory("output")
    FileHandler.save_json(
        listing_data,
        f"output/product_{product['id']}.json"
    )
```

---

### Example 7: Use Utility Functions

```python
from product_listing_utils import (
    merge_dicts,
    filter_dict,
    clean_text,
    truncate_text,
    format_price,
    calculate_statistics,
    batch_items,
    progress_tracker
)

# Merge product data from multiple sources
basic_info = {"name": "Product", "price": 99.99}
detailed_info = {"description": "Great product", "stock": 50}
all_info = merge_dicts(basic_info, detailed_info)

# Filter dictionary to specific fields
public_info = filter_dict(all_info, ["name", "price", "description"])

# Clean messy text
messy = "  This   has    too   many   spaces  "
clean = clean_text(messy)  # "This has too many spaces"

# Truncate long descriptions
long_desc = "This is a very long description that needs truncating"
short = truncate_text(long_desc, 30)  # "This is a very long desc..."

# Format prices consistently
price_str = format_price(99.99)  # "$99.99"
euro_price = format_price(99.99, "€")  # "€99.99"

# Calculate statistics from batch results
token_counts = [100, 150, 200, 175, 125]
stats = calculate_statistics(token_counts)
# {'count': 5, 'sum': 750, 'mean': 150.0, 'min': 100, 'max': 200}

# Batch large lists
products = list(range(100))
batches = batch_items(products, batch_size=10)  # 10 batches of 10

# Track progress
for i, batch in enumerate(batches, 1):
    progress = progress_tracker(i, len(batches), "Processing: ")
    print(progress)  # "Processing: [1/10] 10.0%"
```

---

## API Handler Functions

```python
from product_listing_utils import APIHandler

# Create vision message for OpenAI API
messages = APIHandler.create_vision_message(
    prompt="Describe this product",
    image_base64="base64_encoded_image_string",
    detail="high"
)

# Use with OpenAI client
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    max_tokens=800
)

# Parse the response
parsed = APIHandler.parse_api_response(response)
content = parsed['content']
tokens = parsed['tokens_used']

# Calculate cost
cost = APIHandler.calculate_cost(tokens, "gpt-4o-mini")
print(f"Cost: ${cost:.4f}")
```

---

## Running Tests

### Run All Tests
```bash
python test.py
```

### Run Specific Test Class
```python
python -m unittest test.TestImageProcessor
```

### Run Single Test
```python
python -m unittest test.TestImageProcessor.test_resize_image_larger
```

### Test Output
```
======================================================================
TEST SUMMARY
======================================================================
Tests Run: 47
✅ Passed: 47
❌ Failed: 0
⚠️  Errors: 0
⏭️  Skipped: 0
======================================================================
```

---

## Test Coverage

### ✅ TestValidation (6 tests)
- Valid product data
- Missing fields
- Negative price
- Empty name
- Listing validation

### ✅ TestImageProcessor (7 tests)
- Resize larger images
- Don't upscale smaller images
- RGB conversion
- Base64 encoding
- Load from file
- Load from URL (mocked)
- File not found handling

### ✅ TestJSONParser (7 tests)
- Valid JSON parsing
- Invalid JSON handling
- Markdown extraction with json tag
- Markdown extraction without tag
- Smart parse (multiple formats)
- Field extraction

### ✅ TestPromptGenerator (5 tests)
- Basic prompt creation
- Detailed prompt with options
- Custom template prompts
- Missing variables handling

### ✅ TestAPIHandler (4 tests)
- Vision message creation
- Response parsing
- Cost calculation
- Different model pricing

### ✅ TestFileHandler (5 tests)
- Directory creation
- JSON save/load
- Text save/load
- File listing
- Recursive listing

### ✅ TestUtilityFunctions (11 tests)
- Dictionary merging
- Dictionary filtering
- Text cleaning
- Text truncation
- Price formatting
- Statistics calculation
- Batch creation
- Progress tracking

### ✅ TestDataModels (2 tests)
- ProductData creation
- ListingData creation

---

## Benefits of Modular Design

### 1. **Reusability**
```python
# Use just the parts you need
from product_listing_utils import ImageProcessor

# Use in any project
base64_img = ImageProcessor.process_and_encode("image.jpg")
```

### 2. **Testability**
```python
# Each function can be tested independently
def test_resize_image():
    image = Image.new('RGB', (1000, 1000))
    resized = ImageProcessor.resize_image(image, (512, 512))
    assert resized.size[0] <= 512
```

### 3. **Maintainability**
```python
# Update one function without breaking others
def resize_image(image, max_size, resample=LANCZOS):
    # Change implementation here
    # All code using this function benefits
    pass
```

### 4. **Flexibility**
```python
# Mix and match utilities as needed
from product_listing_utils import (
    ImageProcessor,    # For images
    FileHandler,       # For saving
    clean_text         # For text cleanup
)
```

### 5. **Documentation**
- Every function has docstrings
- Type hints for better IDE support
- Clear parameter descriptions
- Return value documentation

---

## Migration from Original Code

### Before (Original):
```python
# Mixed concerns, repeated code
def process_batch_products(products_data, output_folder="listings"):
    # Image encoding inside
    # API call inside
    # JSON parsing inside
    # File saving inside
    # Error handling mixed
    pass
```

### After (Modular):
```python
# Clear separation of concerns
from product_listing_utils import (
    ImageProcessor,
    JSONParser,
    FileHandler
)

# Each step is independent and reusable
image_base64 = ImageProcessor.process_and_encode(image_path)
listing_data = JSONParser.smart_parse(api_response)
FileHandler.save_json(listing_data, filepath)
```

---

## Best Practices

### 1. Import Only What You Need
```python
# Good ✅
from product_listing_utils import ImageProcessor

# Less ideal (imports everything)
from product_listing_utils import *
```

### 2. Handle Errors Appropriately
```python
# Functions return None on failure
image_base64 = ImageProcessor.process_and_encode(path)
if image_base64 is None:
    print("Failed to process image")
    # Handle error
```

### 3. Use Validation
```python
# Always validate before processing
is_valid, error = validate_product_data(product)
if not is_valid:
    raise ValueError(f"Invalid product: {error}")
```

### 4. Leverage Type Hints
```python
# Your IDE will provide autocomplete and type checking
from product_listing_utils import ImageProcessor

processor = ImageProcessor()
# IDE knows what methods are available
processor.resize_image(...)  # ✅ Autocomplete works
```

---

## Performance Tips

### 1. Batch Image Processing
```python
from product_listing_utils import ImageProcessor, batch_items

images = ["img1.jpg", "img2.jpg", ...]
batches = batch_items(images, 10)

for batch in batches:
    for img in batch:
        ImageProcessor.process_and_encode(img)
    time.sleep(1)  # Rate limiting
```

### 2. Reuse Configurations
```python
# Define once, use multiple times
max_size = (768, 768)
quality = 90

for image_path in images:
    base64_img = ImageProcessor.process_and_encode(
        image_path,
        max_size=max_size,
        quality=quality
    )
```

### 3. Use Statistics for Monitoring
```python
from product_listing_utils import calculate_statistics

token_counts = []
for product in products:
    result = process_product(product)
    token_counts.append(result['tokens'])

stats = calculate_statistics(token_counts)
print(f"Average tokens: {stats['mean']:.1f}")
print(f"Total tokens: {stats['sum']}")
```

---

## Troubleshooting

### Image Loading Fails
```python
# Check if it's a URL or file
from product_listing_utils import ImageProcessor

# For URLs
img = ImageProcessor.load_image_from_url(url)

# For files
img = ImageProcessor.load_image_from_file(path)

# Auto-detect
img = ImageProcessor.load_image(source)
```

### JSON Parsing Fails
```python
# Use smart_parse for robust parsing
from product_listing_utils import JSONParser

data = JSONParser.smart_parse(api_response)
if data is None:
    print("Could not parse JSON")
    print("Raw response:", api_response[:100])
```

### File Operations Fail
```python
# Ensure directory exists first
from product_listing_utils import FileHandler

FileHandler.ensure_directory("output/results")
success = FileHandler.save_json(data, "output/results/data.json")
if not success:
    print("Save failed!")
```

---

## Summary

### ✅ What You Get

1. **product_listing_utils.py**
   - 7 modular classes
   - 40+ reusable functions
   - Complete documentation
   - Type hints throughout

2. **test.py**
   - 47 comprehensive tests
   - All tests passing
   - Edge case coverage
   - Mocked external dependencies

3. **Benefits**
   - Use any function independently
   - Easy to test and maintain
   - Clear separation of concerns
   - Production-ready code

---

**Next Steps:**
1. Import specific utilities you need
2. Run tests to verify everything works
3. Use in your projects
4. Extend with custom functions

All code is tested, documented, and ready to use! 🚀
