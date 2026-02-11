"""
Comprehensive Test Suite for Product Listing Generator
Tests all utility functions and components.

Run with:
    python test.py

Or run specific test:
    python test.py TestImageProcessor
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io
import base64

# Import the utilities to test
from product_listing_utils import (
    ProductData,
    ListingData,
    ImageProcessor,
    JSONParser,
    PromptGenerator,
    APIHandler,
    FileHandler,
    validate_product_data,
    validate_listing_data,
    merge_dicts,
    filter_dict,
    clean_text,
    truncate_text,
    format_price,
    calculate_statistics,
    batch_items,
    progress_tracker
)


# ============================================================================
# TEST: VALIDATION FUNCTIONS
# ============================================================================

class TestValidation(unittest.TestCase):
    """Test validation functions."""

    def test_validate_product_data_valid(self):
        """Test validation with valid product data."""
        product = {
            "id": 1,
            "name": "Test Product",
            "price": 99.99,
            "category": "Electronics",
            "image_path": "test.jpg"
        }
        is_valid, error = validate_product_data(product)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_product_data_missing_field(self):
        """Test validation with missing required field."""
        product = {
            "id": 1,
            "name": "Test Product",
            "price": 99.99,
            # Missing category and image_path
        }
        is_valid, error = validate_product_data(product)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)

    def test_validate_product_data_negative_price(self):
        """Test validation with negative price."""
        product = {
            "id": 1,
            "name": "Test Product",
            "price": -10.00,
            "category": "Electronics",
            "image_path": "test.jpg"
        }
        is_valid, error = validate_product_data(product)
        self.assertFalse(is_valid)
        self.assertIn("negative", error.lower())

    def test_validate_product_data_empty_name(self):
        """Test validation with empty name."""
        product = {
            "id": 1,
            "name": "",
            "price": 99.99,
            "category": "Electronics",
            "image_path": "test.jpg"
        }
        is_valid, error = validate_product_data(product)
        self.assertFalse(is_valid)

    def test_validate_listing_data_valid(self):
        """Test listing validation with valid data."""
        listing = {
            "title": "Great Product",
            "description": "This is a detailed description that is more than 50 characters long.",
            "features": ["Feature 1", "Feature 2"],
            "keywords": "product, great"
        }
        is_valid, error = validate_listing_data(listing)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_listing_data_short_description(self):
        """Test listing validation with short description."""
        listing = {
            "title": "Great Product",
            "description": "Too short",
            "features": ["Feature 1"],
            "keywords": "product"
        }
        is_valid, error = validate_listing_data(listing)
        self.assertFalse(is_valid)
        self.assertIn("50", error)


# ============================================================================
# TEST: IMAGE PROCESSOR
# ============================================================================

class TestImageProcessor(unittest.TestCase):
    """Test image processing functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test image
        self.test_image = Image.new('RGB', (100, 100), color='red')
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_resize_image_larger(self):
        """Test resizing a larger image."""
        large_image = Image.new('RGB', (1000, 1000), color='blue')
        resized = ImageProcessor.resize_image(large_image, (512, 512))

        self.assertLessEqual(resized.size[0], 512)
        self.assertLessEqual(resized.size[1], 512)

    def test_resize_image_smaller(self):
        """Test that smaller images are not upscaled."""
        small_image = Image.new('RGB', (100, 100), color='green')
        resized = ImageProcessor.resize_image(small_image, (512, 512))

        self.assertEqual(resized.size, (100, 100))

    def test_convert_to_rgb(self):
        """Test RGB conversion."""
        # Create RGBA image
        rgba_image = Image.new('RGBA', (100, 100), color='red')
        rgb_image = ImageProcessor.convert_to_rgb(rgba_image)

        self.assertEqual(rgb_image.mode, 'RGB')

    def test_image_to_base64(self):
        """Test base64 encoding."""
        base64_str = ImageProcessor.image_to_base64(self.test_image)

        self.assertIsInstance(base64_str, str)
        self.assertGreater(len(base64_str), 0)

        # Verify it's valid base64
        try:
            base64.b64decode(base64_str)
            valid_base64 = True
        except Exception:
            valid_base64 = False

        self.assertTrue(valid_base64)

    def test_load_image_from_file(self):
        """Test loading image from file."""
        # Save test image
        image_path = Path(self.temp_dir) / "test.jpg"
        self.test_image.save(image_path)

        # Load it back
        loaded = ImageProcessor.load_image_from_file(str(image_path))

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.size, self.test_image.size)

    def test_load_image_from_file_not_found(self):
        """Test loading non-existent file."""
        loaded = ImageProcessor.load_image_from_file("nonexistent.jpg")
        self.assertIsNone(loaded)

    @patch('requests.get')
    def test_load_image_from_url(self, mock_get):
        """Test loading image from URL."""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200

        # Create image bytes
        img_buffer = io.BytesIO()
        self.test_image.save(img_buffer, format='JPEG')
        mock_response.content = img_buffer.getvalue()

        mock_get.return_value = mock_response

        # Test
        loaded = ImageProcessor.load_image_from_url("http://example.com/image.jpg")

        self.assertIsNotNone(loaded)
        mock_get.assert_called_once()


# ============================================================================
# TEST: JSON PARSER
# ============================================================================

class TestJSONParser(unittest.TestCase):
    """Test JSON parsing functions."""

    def test_parse_json_valid(self):
        """Test parsing valid JSON."""
        json_str = '{"title": "Test", "value": 123}'
        result = JSONParser.parse_json(json_str)

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test')
        self.assertEqual(result['value'], 123)

    def test_parse_json_invalid(self):
        """Test parsing invalid JSON."""
        json_str = '{title: "Test"}'  # Missing quotes
        result = JSONParser.parse_json(json_str)

        self.assertIsNone(result)

    def test_extract_from_markdown_with_json_tag(self):
        """Test extracting JSON from markdown with json tag."""
        text = '''```json
        {
            "title": "Product",
            "description": "Great product"
        }
        ```'''

        extracted = JSONParser.extract_from_markdown(text)
        self.assertIsNotNone(extracted)
        self.assertIn("title", extracted)

    def test_extract_from_markdown_without_tag(self):
        """Test extracting JSON from markdown without json tag."""
        text = '''```
        {
            "title": "Product",
            "description": "Great product"
        }
        ```'''

        extracted = JSONParser.extract_from_markdown(text)
        self.assertIsNotNone(extracted)

    def test_smart_parse_direct_json(self):
        """Test smart parse with direct JSON."""
        text = '{"title": "Test"}'
        result = JSONParser.smart_parse(text)

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test')

    def test_smart_parse_markdown_wrapped(self):
        """Test smart parse with markdown-wrapped JSON."""
        text = '```json\n{"title": "Test"}\n```'
        result = JSONParser.smart_parse(text)

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Test')

    def test_extract_fields(self):
        """Test field extraction."""
        data = {
            "title": "Product",
            "description": "Great",
            "price": 99.99,
            "extra": "field"
        }

        extracted = JSONParser.extract_fields(
            data,
            ['title', 'description', 'missing'],
            default_value="N/A"
        )

        self.assertEqual(extracted['title'], 'Product')
        self.assertEqual(extracted['description'], 'Great')
        self.assertEqual(extracted['missing'], 'N/A')
        self.assertNotIn('extra', extracted)


# ============================================================================
# TEST: PROMPT GENERATOR
# ============================================================================

class TestPromptGenerator(unittest.TestCase):
    """Test prompt generation functions."""

    def test_create_basic_prompt(self):
        """Test basic prompt creation."""
        prompt = PromptGenerator.create_basic_prompt(
            "Test Product",
            99.99,
            "Electronics"
        )

        self.assertIn("Test Product", prompt)
        self.assertIn("99.99", prompt)
        self.assertIn("Electronics", prompt)
        self.assertIn("JSON", prompt)

    def test_create_detailed_prompt(self):
        """Test detailed prompt creation."""
        prompt = PromptGenerator.create_detailed_prompt(
            "Headphones",
            129.99,
            "Audio",
            additional_info="Noise cancelling",
            include_seo=True,
            word_count=150
        )

        self.assertIn("Headphones", prompt)
        self.assertIn("129.99", prompt)
        self.assertIn("Audio", prompt)
        self.assertIn("Noise cancelling", prompt)
        self.assertIn("keywords", prompt)
        self.assertIn("150", prompt)

    def test_create_detailed_prompt_no_seo(self):
        """Test detailed prompt without SEO."""
        prompt = PromptGenerator.create_detailed_prompt(
            "Product",
            50.00,
            "Category",
            include_seo=False
        )

        self.assertNotIn("keywords", prompt)

    def test_create_custom_prompt(self):
        """Test custom prompt from template."""
        template = "Product: {name}, Price: {price}, Category: {category}"
        variables = {
            "name": "Widget",
            "price": "$19.99",
            "category": "Gadgets"
        }

        prompt = PromptGenerator.create_custom_prompt(template, variables)

        self.assertEqual(prompt, "Product: Widget, Price: $19.99, Category: Gadgets")

    def test_create_custom_prompt_missing_variable(self):
        """Test custom prompt with missing variable."""
        template = "Product: {name}, Price: {price}"
        variables = {"name": "Widget"}  # Missing price

        prompt = PromptGenerator.create_custom_prompt(template, variables)

        # Should return original template when variable is missing
        self.assertEqual(prompt, template)


# ============================================================================
# TEST: API HANDLER
# ============================================================================

class TestAPIHandler(unittest.TestCase):
    """Test API handling functions."""

    def test_create_vision_message(self):
        """Test vision message creation."""
        prompt = "Describe this image"
        image_base64 = "base64encodedstring"

        messages = APIHandler.create_vision_message(prompt, image_base64)

        self.assertIsInstance(messages, list)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['role'], 'user')
        self.assertIn('content', messages[0])

    def test_parse_api_response(self):
        """Test API response parsing."""
        # Create mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test content"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.total_tokens = 100
        mock_response.model = "gpt-4o-mini"

        parsed = APIHandler.parse_api_response(mock_response)

        self.assertEqual(parsed['content'], "Test content")
        self.assertEqual(parsed['tokens_used'], 100)
        self.assertEqual(parsed['model'], "gpt-4o-mini")
        self.assertEqual(parsed['finish_reason'], "stop")

    def test_calculate_cost(self):
        """Test cost calculation."""
        cost = APIHandler.calculate_cost(10000, "gpt-4o-mini")

        self.assertIsInstance(cost, float)
        self.assertGreater(cost, 0)

    def test_calculate_cost_different_models(self):
        """Test cost calculation for different models."""
        tokens = 10000

        cost_mini = APIHandler.calculate_cost(tokens, "gpt-4o-mini")
        cost_4o = APIHandler.calculate_cost(tokens, "gpt-4o")
        cost_4 = APIHandler.calculate_cost(tokens, "gpt-4")

        # More expensive models should cost more
        self.assertLess(cost_mini, cost_4o)
        self.assertLess(cost_4o, cost_4)


# ============================================================================
# TEST: FILE HANDLER
# ============================================================================

class TestFileHandler(unittest.TestCase):
    """Test file handling functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ensure_directory(self):
        """Test directory creation."""
        new_dir = Path(self.temp_dir) / "new_folder"

        result = FileHandler.ensure_directory(str(new_dir))

        self.assertTrue(result.exists())
        self.assertTrue(result.is_dir())

    def test_save_and_load_json(self):
        """Test JSON save and load."""
        data = {"test": "data", "number": 42}
        filepath = Path(self.temp_dir) / "test.json"

        # Save
        success = FileHandler.save_json(data, str(filepath))
        self.assertTrue(success)
        self.assertTrue(filepath.exists())

        # Load
        loaded = FileHandler.load_json(str(filepath))
        self.assertEqual(loaded, data)

    def test_save_and_load_text(self):
        """Test text save and load."""
        text = "This is test content\nWith multiple lines"
        filepath = Path(self.temp_dir) / "test.txt"

        # Save
        success = FileHandler.save_text(text, str(filepath))
        self.assertTrue(success)
        self.assertTrue(filepath.exists())

        # Load
        loaded = FileHandler.load_text(str(filepath))
        self.assertEqual(loaded, text)

    def test_list_files(self):
        """Test file listing."""
        # Create some test files
        (Path(self.temp_dir) / "file1.json").touch()
        (Path(self.temp_dir) / "file2.json").touch()
        (Path(self.temp_dir) / "file3.txt").touch()

        # List JSON files
        json_files = FileHandler.list_files(self.temp_dir, "*.json")

        self.assertEqual(len(json_files), 2)

    def test_list_files_recursive(self):
        """Test recursive file listing."""
        # Create nested structure
        subdir = Path(self.temp_dir) / "subdir"
        subdir.mkdir()
        (Path(self.temp_dir) / "file1.json").touch()
        (subdir / "file2.json").touch()

        # List recursively
        json_files = FileHandler.list_files(self.temp_dir, "*.json", recursive=True)

        self.assertEqual(len(json_files), 2)


# ============================================================================
# TEST: UTILITY FUNCTIONS
# ============================================================================

class TestUtilityFunctions(unittest.TestCase):
    """Test general utility functions."""

    def test_merge_dicts(self):
        """Test dictionary merging."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        dict3 = {"e": 5}

        merged = merge_dicts(dict1, dict2, dict3)

        self.assertEqual(len(merged), 5)
        self.assertEqual(merged['a'], 1)
        self.assertEqual(merged['e'], 5)

    def test_merge_dicts_overlap(self):
        """Test dictionary merging with overlapping keys."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}

        merged = merge_dicts(dict1, dict2)

        # Later dict should win
        self.assertEqual(merged['b'], 3)

    def test_filter_dict(self):
        """Test dictionary filtering."""
        data = {"a": 1, "b": 2, "c": 3, "d": 4}
        filtered = filter_dict(data, ["a", "c", "e"])

        self.assertEqual(len(filtered), 2)
        self.assertIn("a", filtered)
        self.assertIn("c", filtered)
        self.assertNotIn("b", filtered)

    def test_clean_text(self):
        """Test text cleaning."""
        text = "  This   has    extra   spaces  "
        cleaned = clean_text(text)

        self.assertEqual(cleaned, "This has extra spaces")

    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that needs to be truncated"
        truncated = truncate_text(text, 20)

        self.assertEqual(len(truncated), 20)
        self.assertTrue(truncated.endswith("..."))

    def test_truncate_text_short(self):
        """Test truncating text shorter than max length."""
        text = "Short"
        truncated = truncate_text(text, 20)

        self.assertEqual(truncated, "Short")

    def test_format_price(self):
        """Test price formatting."""
        formatted = format_price(99.99)
        self.assertEqual(formatted, "$99.99")

        formatted_euro = format_price(99.99, "€")
        self.assertEqual(formatted_euro, "€99.99")

    def test_calculate_statistics(self):
        """Test statistics calculation."""
        numbers = [1, 2, 3, 4, 5]
        stats = calculate_statistics(numbers)

        self.assertEqual(stats['count'], 5)
        self.assertEqual(stats['sum'], 15)
        self.assertEqual(stats['mean'], 3.0)
        self.assertEqual(stats['min'], 1)
        self.assertEqual(stats['max'], 5)

    def test_calculate_statistics_empty(self):
        """Test statistics with empty list."""
        stats = calculate_statistics([])
        self.assertEqual(stats, {})

    def test_batch_items(self):
        """Test item batching."""
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        batches = batch_items(items, 3)

        self.assertEqual(len(batches), 4)
        self.assertEqual(batches[0], [1, 2, 3])
        self.assertEqual(batches[-1], [10])

    def test_progress_tracker(self):
        """Test progress tracking."""
        progress = progress_tracker(5, 10, "Processing: ")

        self.assertIn("5/10", progress)
        self.assertIn("50.0%", progress)
        self.assertIn("Processing:", progress)


# ============================================================================
# TEST: DATA MODELS
# ============================================================================

class TestDataModels(unittest.TestCase):
    """Test data model classes."""

    def test_product_data_creation(self):
        """Test ProductData creation."""
        product = ProductData(
            id=1,
            name="Test",
            price=99.99,
            category="Electronics",
            image_path="test.jpg"
        )

        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "Test")
        self.assertEqual(product.price, 99.99)

    def test_listing_data_creation(self):
        """Test ListingData creation."""
        listing = ListingData(
            title="Great Product",
            description="A wonderful product",
            features=["Feature 1", "Feature 2"],
            keywords="great, product"
        )

        self.assertEqual(listing.title, "Great Product")
        self.assertIsInstance(listing.features, list)
        self.assertEqual(len(listing.features), 2)


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_tests(verbosity=2):
    """
    Run all tests.

    Args:
        verbosity: Test output verbosity (0-2)
    """
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestValidation,
        TestImageProcessor,
        TestJSONParser,
        TestPromptGenerator,
        TestAPIHandler,
        TestFileHandler,
        TestUtilityFunctions,
        TestDataModels
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped)}")
    print("=" * 70)

    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    # Run tests
    success = run_tests(verbosity=2)

    # Exit with appropriate code
    sys.exit(0 if success else 1)
