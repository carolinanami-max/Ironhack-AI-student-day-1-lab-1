from product_listing_utils import ImageProcessor

# Process an image from URL
image_url = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"

base64_img = ImageProcessor.process_and_encode(
    image_url,
    max_size=(512, 512),
    quality=85
)

if base64_img:
    print(f"✅ Success! Encoded {len(base64_img)} characters")
else:
    print("❌ Failed")