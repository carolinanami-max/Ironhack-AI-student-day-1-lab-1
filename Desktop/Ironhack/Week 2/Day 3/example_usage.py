"""
Example Usage of product_listing_utils.py
This file shows you exactly how to use the modular utilities in your own code.

Run this file:
    python example_usage.py
"""

import os
from dotenv import load_dotenv

# ============================================================================
# STEP 1: Import only what you need
# ============================================================================

from product_listing_utils import (
    ImageProcessor,
    JSONParser,
    PromptGenerator,
    APIHandler,
    FileHandler,
    validate_product_data,
    validate_listing_data,
    format_price,
    calculate_statistics,
    batch_items,
    progress_tracker
)

# ============================================================================
# EXAMPLE 1: Process a Single Image
# ============================================================================

def example_1_process_image():
    """Example: Process an image from URL or local file."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Process Image")
    print("="*60)

    # From URL
    image_url = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"

    print(f"Processing image from URL...")
    base64_img = ImageProcessor.process_and_encode(
        image_url,
        max_size=(512, 512),
        quality=85
    )

    if base64_img:
        print(f"✅ Success! Image encoded: {len(base64_img)} characters")
        print(f"   First 50 chars: {base64_img[:50]}...")
    else:
        print("❌ Failed to process image")

    return base64_img


# ============================================================================
# EXAMPLE 2: Parse JSON from API Response
# ============================================================================

def example_2_parse_json():
    """Example: Parse JSON from various formats."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Parse JSON from API Response")
    print("="*60)

    # Simulate API response with markdown code block (common issue!)
    api_response = '''```json
    {
        "title": "Premium Wireless Headphones",
        "description": "Experience superior sound quality with our premium headphones.",
        "features": [
            "Active noise cancellation",
            "40-hour battery life",
            "Bluetooth 5.0",
            "Comfortable design",
            "Premium sound quality"
        ],
        "keywords": "headphones, wireless, audio, bluetooth"
    }
    ```'''

    print("Parsing API response (with markdown wrapper)...")
    data = JSONParser.smart_parse(api_response)

    if data:
        print(f"✅ Success! Parsed JSON:")
        print(f"   Title: {data['title']}")
        print(f"   Features: {len(data['features'])} items")
        print(f"   First feature: {data['features'][0]}")
    else:
        print("❌ Failed to parse JSON")

    return data


# ============================================================================
# EXAMPLE 3: Create Prompts
# ============================================================================

def example_3_create_prompts():
    """Example: Create different types of prompts."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Create Prompts")
    print("="*60)

    # Basic prompt
    print("\n1. Basic Prompt:")
    basic = PromptGenerator.create_basic_prompt(
        "Wireless Mouse",
        29.99,
        "Electronics"
    )
    print(f"   Length: {len(basic)} characters")
    print(f"   Preview: {basic[:100]}...")

    # Detailed prompt
    print("\n2. Detailed Prompt with SEO:")
    detailed = PromptGenerator.create_detailed_prompt(
        product_name="Smart Watch",
        price=299.99,
        category="Wearables",
        additional_info="Heart rate monitor, GPS, waterproof",
        include_seo=True,
        word_count=150
    )
    print(f"   Length: {len(detailed)} characters")
    print(f"   Includes SEO: {'keywords' in detailed}")

    # Custom prompt from template
    print("\n3. Custom Prompt from Template:")
    template = "Create a listing for {product} priced at {price} in the {category} category."
    custom = PromptGenerator.create_custom_prompt(
        template,
        {
            "product": "Bluetooth Speaker",
            "price": "$79.99",
            "category": "Audio"
        }
    )
    print(f"   Result: {custom}")

    return detailed


# ============================================================================
# EXAMPLE 4: Validate Data
# ============================================================================

def example_4_validate_data():
    """Example: Validate product and listing data."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Validate Data")
    print("="*60)

    # Valid product
    print("\n1. Validating VALID product:")
    valid_product = {
        "id": 1,
        "name": "Wireless Keyboard",
        "price": 49.99,
        "category": "Electronics",
        "image_path": "keyboard.jpg"
    }

    is_valid, error = validate_product_data(valid_product)
    if is_valid:
        print(f"   ✅ Valid product!")
    else:
        print(f"   ❌ Invalid: {error}")

    # Invalid product (negative price)
    print("\n2. Validating INVALID product (negative price):")
    invalid_product = {
        "id": 2,
        "name": "Widget",
        "price": -10.00,  # Invalid!
        "category": "Gadgets",
        "image_path": "widget.jpg"
    }

    is_valid, error = validate_product_data(invalid_product)
    if is_valid:
        print(f"   ✅ Valid product!")
    else:
        print(f"   ❌ Invalid: {error}")

    # Valid listing
    print("\n3. Validating listing data:")
    listing = {
        "title": "Amazing Wireless Keyboard",
        "description": "This is a great keyboard with mechanical switches and RGB lighting. Perfect for gaming and productivity. Features include hot-swappable switches and programmable keys.",
        "features": ["Mechanical switches", "RGB lighting", "Hot-swappable"],
        "keywords": "keyboard, wireless, mechanical, gaming"
    }

    is_valid, error = validate_listing_data(listing)
    if is_valid:
        print(f"   ✅ Valid listing!")
    else:
        print(f"   ❌ Invalid: {error}")


# ============================================================================
# EXAMPLE 5: File Operations
# ============================================================================

def example_5_file_operations():
    """Example: Save and load files."""
    print("\n" + "="*60)
    print("EXAMPLE 5: File Operations")
    print("="*60)

    # Ensure directory exists
    print("\n1. Creating directory...")
    FileHandler.ensure_directory("examples_output")
    print("   ✅ Directory ready: examples_output/")

    # Save JSON
    print("\n2. Saving JSON file...")
    test_data = {
        "product_id": 1,
        "name": "Test Product",
        "price": 99.99,
        "features": ["Feature 1", "Feature 2"]
    }

    success = FileHandler.save_json(
        test_data,
        "examples_output/test_product.json"
    )

    if success:
        print("   ✅ Saved: examples_output/test_product.json")

    # Load JSON
    print("\n3. Loading JSON file...")
    loaded = FileHandler.load_json("examples_output/test_product.json")

    if loaded:
        print(f"   ✅ Loaded successfully!")
        print(f"   Product name: {loaded['name']}")
        print(f"   Price: ${loaded['price']}")

    # Save text
    print("\n4. Saving text file...")
    FileHandler.save_text(
        "This is a test description.\nWith multiple lines.",
        "examples_output/description.txt"
    )
    print("   ✅ Saved: examples_output/description.txt")

    # List files
    print("\n5. Listing all JSON files...")
    json_files = FileHandler.list_files("examples_output", "*.json")
    print(f"   Found {len(json_files)} JSON files:")
    for f in json_files:
        print(f"   - {f.name}")


# ============================================================================
# EXAMPLE 6: Utility Functions
# ============================================================================

def example_6_utilities():
    """Example: Use utility functions."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Utility Functions")
    print("="*60)

    # Format prices
    print("\n1. Format Prices:")
    prices = [29.99, 99.99, 199.99]
    for price in prices:
        formatted = format_price(price)
        print(f"   {price} → {formatted}")

    # Calculate statistics
    print("\n2. Calculate Statistics:")
    token_counts = [100, 150, 200, 125, 175, 180, 190]
    stats = calculate_statistics(token_counts)
    print(f"   Data: {token_counts}")
    print(f"   Count: {stats['count']}")
    print(f"   Mean: {stats['mean']:.1f}")
    print(f"   Min: {stats['min']}")
    print(f"   Max: {stats['max']}")
    print(f"   Sum: {stats['sum']}")

    # Batch items
    print("\n3. Batch Items:")
    products = list(range(1, 26))  # 25 products
    batches = batch_items(products, 5)
    print(f"   Total items: {len(products)}")
    print(f"   Batch size: 5")
    print(f"   Number of batches: {len(batches)}")
    print(f"   First batch: {batches[0]}")
    print(f"   Last batch: {batches[-1]}")

    # Progress tracker
    print("\n4. Progress Tracker:")
    for i in range(1, 6):
        progress = progress_tracker(i, 5, "Processing: ")
        print(f"   {progress}")


# ============================================================================
# EXAMPLE 7: Complete Workflow (Without API Call)
# ============================================================================

def example_7_complete_workflow():
    """Example: Complete workflow using multiple utilities."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Complete Workflow")
    print("="*60)

    # Product data
    product = {
        "id": 1,
        "name": "Premium Wireless Headphones",
        "price": 129.99,
        "category": "Electronics",
        "image_path": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        "additional_info": "Noise cancelling, 40-hour battery"
    }

    print("\n1. Validating product...")
    is_valid, error = validate_product_data(product)
    if not is_valid:
        print(f"   ❌ Validation failed: {error}")
        return
    print("   ✅ Product valid")

    print("\n2. Processing image...")
    image_base64 = ImageProcessor.process_and_encode(
        product['image_path'],
        max_size=(512, 512)
    )
    if not image_base64:
        print("   ❌ Image processing failed")
        return
    print(f"   ✅ Image processed: {len(image_base64)} chars")

    print("\n3. Creating prompt...")
    prompt = PromptGenerator.create_detailed_prompt(
        product['name'],
        product['price'],
        product['category'],
        product['additional_info']
    )
    print(f"   ✅ Prompt created: {len(prompt)} chars")

    # Simulate API response (in real usage, you'd call OpenAI API here)
    print("\n4. Simulating API response...")
    simulated_response = '''```json
    {
        "title": "Premium Wireless Headphones - 40Hr Battery",
        "description": "Experience superior audio quality with our premium wireless headphones. Featuring active noise cancellation technology, these headphones deliver crystal-clear sound while blocking out ambient noise. With an impressive 40-hour battery life, you can enjoy your music all day without interruption. The comfortable over-ear design ensures long-lasting comfort during extended listening sessions.",
        "features": [
            "Active noise cancellation technology",
            "40-hour battery life on single charge",
            "Premium audio drivers for superior sound",
            "Comfortable over-ear design",
            "Wireless Bluetooth connectivity"
        ],
        "keywords": "wireless headphones, noise cancelling, bluetooth, premium audio, long battery"
    }
    ```'''

    print("\n5. Parsing API response...")
    listing = JSONParser.smart_parse(simulated_response)
    if not listing:
        print("   ❌ JSON parsing failed")
        return
    print("   ✅ Response parsed successfully")

    print("\n6. Validating listing...")
    is_valid, error = validate_listing_data(listing)
    if not is_valid:
        print(f"   ❌ Listing validation failed: {error}")
        return
    print("   ✅ Listing valid")

    print("\n7. Saving to file...")
    FileHandler.ensure_directory("examples_output")

    # Add metadata
    listing['product_id'] = product['id']
    listing['original_name'] = product['name']
    listing['original_price'] = product['price']
    listing['formatted_price'] = format_price(product['price'])

    success = FileHandler.save_json(
        listing,
        f"examples_output/product_{product['id']}.json"
    )

    if success:
        print(f"   ✅ Saved: examples_output/product_{product['id']}.json")

    print("\n8. Results:")
    print(f"   Title: {listing['title']}")
    print(f"   Price: {listing['formatted_price']}")
    print(f"   Features: {len(listing['features'])} items")
    print(f"   Description length: {len(listing['description'])} chars")


# ============================================================================
# EXAMPLE 8: Using with OpenAI API (Optional)
# ============================================================================

def example_8_with_openai_api():
    """Example: Complete workflow WITH actual OpenAI API call."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Using with OpenAI API (OPTIONAL)")
    print("="*60)

    # Check if API key is available
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("⚠️  OPENAI_API_KEY not found in .env file")
        print("   This example is skipped (it's optional)")
        print("   To use: Add OPENAI_API_KEY to your .env file")
        return

    print("✅ API key found! Running full example with OpenAI...")

    from openai import OpenAI

    # Product data
    product = {
        "id": 1,
        "name": "Wireless Mouse",
        "price": 29.99,
        "category": "Electronics",
        "image_path": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"
    }

    # 1. Process image
    print("\n1. Processing image...")
    image_base64 = ImageProcessor.process_and_encode(product['image_path'])

    # 2. Create prompt
    print("2. Creating prompt...")
    prompt = PromptGenerator.create_detailed_prompt(
        product['name'],
        product['price'],
        product['category']
    )

    # 3. Create API message
    print("3. Creating API message...")
    messages = APIHandler.create_vision_message(prompt, image_base64)

    # 4. Call OpenAI API
    print("4. Calling OpenAI API...")
    client = OpenAI(api_key=api_key)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=800,
            temperature=0.7
        )

        # 5. Parse response
        print("5. Parsing response...")
        parsed = APIHandler.parse_api_response(response)
        listing = JSONParser.smart_parse(parsed['content'])

        # 6. Calculate cost
        cost = APIHandler.calculate_cost(parsed['tokens_used'], "gpt-4o-mini")

        # 7. Save result
        print("6. Saving result...")
        FileHandler.ensure_directory("examples_output")
        FileHandler.save_json(
            listing,
            "examples_output/openai_generated.json"
        )

        # Show results
        print("\n✅ SUCCESS!")
        print(f"   Title: {listing['title']}")
        print(f"   Features: {len(listing['features'])} items")
        print(f"   Tokens used: {parsed['tokens_used']}")
        print(f"   Estimated cost: ${cost:.4f}")
        print(f"   Saved to: examples_output/openai_generated.json")

    except Exception as e:
        print(f"❌ API call failed: {e}")


# ============================================================================
# MAIN: Run All Examples
# ============================================================================

def main():
    """Run all examples."""
    print("="*60)
    print("PRODUCT LISTING UTILS - USAGE EXAMPLES")
    print("="*60)
    print("\nThese examples show you how to use each utility function.")
    print("You can copy these examples into your own code!\n")

    # Run examples
    example_1_process_image()
    example_2_parse_json()
    example_3_create_prompts()
    example_4_validate_data()
    example_5_file_operations()
    example_6_utilities()
    example_7_complete_workflow()

    # Optional: OpenAI API example
    example_8_with_openai_api()

    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Check the 'examples_output/' folder for generated files")
    print("2. Copy any example function into your own code")
    print("3. Modify the examples for your specific needs")
    print("\nHappy coding! 🚀")


if __name__ == "__main__":
    main()
