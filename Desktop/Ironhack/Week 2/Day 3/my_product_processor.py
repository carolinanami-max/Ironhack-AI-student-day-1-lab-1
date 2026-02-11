"""
My Product Processor
Your first complete workflow!
"""

from product_listing_utils import (
    ImageProcessor,
    JSONParser,
    PromptGenerator,
    FileHandler,
    validate_product_data,
    format_price
)

def process_my_product():
    # Step 1: Define your product
    product = {
        "id": 1,
        "name": "Vitamin C Gummybears",  # Change this!
        "price": 149.99,  # Change this!
        "category": "Health & Wellness",  # Change this!
        "image_path": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"
    }
    
    # Step 2: Validate
    print("Step 1: Validating product...")
    is_valid, error = validate_product_data(product)
    if not is_valid:
        print(f"❌ Error: {error}")
        return
    print("✅ Valid!")
    
    # Step 3: Process image
    print("\nStep 2: Processing image...")
    image_base64 = ImageProcessor.process_and_encode(product['image_path'])
    if image_base64:
        print(f"✅ Image encoded: {len(image_base64)} chars")
    
    # Step 4: Create prompt
    print("\nStep 3: Creating prompt...")
    prompt = PromptGenerator.create_detailed_prompt(
        product['name'],
        product['price'],
        product['category']
    )
    print(f"✅ Prompt created")
    print(f"\nPrompt preview:\n{prompt[:300]}...\n")
    
    # Step 5: Simulate API response (normally you'd call OpenAI here)
    simulated_listing = {
        "title": f"Amazing {product['name']}",
        "description": f"A great {product['name']} for only {format_price(product['price'])}!",
        "features": ["Feature 1", "Feature 2", "Feature 3"],
        "keywords": "product, amazing, great"
    }
    
    # Step 6: Save result
    print("Step 4: Saving result...")
    FileHandler.ensure_directory("my_output")
    FileHandler.save_json(
        simulated_listing,
        f"my_output/product_{product['id']}.json"
    )
    print(f"✅ Saved to my_output/product_{product['id']}.json")
    
    # Step 7: Show results
    print("\n" + "="*50)
    print("RESULTS:")
    print("="*50)
    print(f"Title: {simulated_listing['title']}")
    print(f"Description: {simulated_listing['description']}")
    print(f"Features: {len(simulated_listing['features'])} items")
    print("\n✅ Done!")

if __name__ == "__main__":
    process_my_product()
