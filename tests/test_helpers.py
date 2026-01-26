import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestImageGenerator:
    @staticmethod
    def create_test_image_with_numbers(output_path, numbers, size=(400, 200)):
        image = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        y_offset = 50
        for number in numbers:
            draw.text((50, y_offset), str(number), fill='black', font=font)
            y_offset += 50
        
        image.save(output_path)
        return output_path

    @staticmethod
    def create_test_image_with_text(output_path, text, size=(400, 200)):
        image = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 80), text, fill='black', font=font)
        image.save(output_path)
        return output_path

    @staticmethod
    def create_empty_image(output_path, size=(400, 200)):
        image = Image.new('RGB', size, color='white')
        image.save(output_path)
        return output_path


def create_test_images():
    test_dir = os.path.join(os.path.dirname(__file__), 'test_images')
    os.makedirs(test_dir, exist_ok=True)
    
    generator = TestImageGenerator()
    
    test_images = {
        'numbers_only.png': ['12.5', '34.2', '56.7'],
        'integers_only.png': ['10', '20', '30'],
        'mixed_numbers.png': ['10', '20.5', '30', '40.75'],
        'text_only.png': ['hello', 'world', 'test'],
        'mixed_content.png': ['10', 'hello', '20.5', 'world', '30'],
        'decimals.png': ['0.1', '0.2', '0.3'],
        'large_numbers.png': ['1000.5', '2000.25', '3000.75'],
        'empty.png': [],
    }
    
    created_paths = []
    for filename, content in test_images.items():
        output_path = os.path.join(test_dir, filename)
        if content:
            generator.create_test_image_with_numbers(output_path, content)
        else:
            generator.create_empty_image(output_path)
        created_paths.append(output_path)
    
    return created_paths


if __name__ == '__main__':
    paths = create_test_images()
    print(f"Created test images: {paths}")
