import os
import sys
from utils.file_parser import FileParser


def process_file(file_path):
    """Process a single file and generate documentation"""
    try:
        print(f"\n\033[1mProcessing file: {file_path}\033[0m")
        parser = FileParser(file_path)
        parser.analyze_file()
        print(f"\033[92m✓ Successfully processed {file_path}\033[0m")
        return True
    except ValueError as e:
        print(f"\033[93m⚠️ Skipping unsupported file: {file_path} - {str(e)}\033[0m")
        return False
    except Exception as e:
        print(f"\033[91m✗ Error processing {file_path}: {str(e)}\033[0m")
        return False


def scan_and_process_directory(directory="examples"):
    """Scan a directory and process all supported language files"""
    supported_extensions = {'.py', '.js', '.cpp', '.hpp', '.cc', '.cxx', '.go', '.rs'}
    stats = {
        'total': 0,
        'processed': 0,
        'skipped': 0,
        'errors': 0
    }

    print(f"\n\033[1m🔍 Scanning directory: {directory}\033[0m")

    for filename in sorted(os.listdir(directory)):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            stats['total'] += 1
            _, ext = os.path.splitext(filename)

            if ext.lower() in supported_extensions:
                success = process_file(file_path)
                if success:
                    stats['processed'] += 1
                else:
                    stats['errors'] += 1
            else:
                print(f"\033[93m⚠️ Skipping unsupported file type: {filename}\033[0m")
                stats['skipped'] += 1

    # Print summary
    print("\n\033[1m📊 Processing Summary:\033[0m")
    print(f"  Total files found:    {stats['total']}")
    print(f"  \033[92mSuccessfully processed: {stats['processed']}\033[0m")
    print(f"  \033[93mSkipped (unsupported):  {stats['skipped']}\033[0m")
    print(f"  \033[91mErrors encountered:     {stats['errors']}\033[0m")

    return stats['processed'] > 0


if __name__ == "__main__":
    # Add utils directory to Python path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Process all files in examples directory
    success = scan_and_process_directory("examples")

    # Exit with appropriate status code
    sys.exit(0 if success else 1)