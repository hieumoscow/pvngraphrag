import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient as AsyncDocumentIntelligenceClient
from dotenv import load_dotenv
import os
import time
import json
from datetime import datetime
from PyPDF2 import PdfReader
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Configuration constants
DEFAULT_PAGE_BATCH_SIZE = 5  # Number of pages to process in one batch
DEFAULT_CONCURRENT_FILES = 3  # Number of files to process concurrently
MAX_WAIT_TIME = 300  # Maximum time to wait for a batch to complete (in seconds)

def test_connection():
    """Test the connection to Azure Document Intelligence service"""
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT').rstrip('/')  # Remove trailing slash
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    if not endpoint or not key:
        raise ValueError("Azure Document Intelligence credentials not found in environment variables")
    
    print(f"Testing connection to endpoint: {endpoint}")
    
    try:
        # Create synchronous client for testing
        client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key),
            api_version="2024-11-30"
        )
        
        print("Successfully connected to the service")
        return True
            
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        print("Error type:", type(e).__name__)
        print("Error details:", str(e))
        return False

async def analyze_file_via_doci_async(file_path, output_path, client, page_batch_size=DEFAULT_PAGE_BATCH_SIZE):
    """
    Analyze a document using Azure Document Intelligence asynchronously
    Args:
        file_path: Path to the PDF file
        output_path: Path to save the output markdown
        client: Azure Document Intelligence client
        page_batch_size: Number of pages to process in one batch
    """
    filename = os.path.basename(file_path)
    try:
        with open(file_path, "rb") as f:
            document_content = f.read()
            
        print(f"\n[{filename}] File size: {len(document_content)} bytes")
        start_time = time.time()
        
        # Detect total pages using PyPDF2
        pdf_reader = PdfReader(BytesIO(document_content))
        total_pages = len(pdf_reader.pages)
        print(f"[{filename}] Detected {total_pages} pages in PDF")
        
        all_content = []
        
        try:
            print(f"[{filename}] Starting analysis...")
            
            # Track processed pages
            processed_pages = set()
            failed_pages = set()
            
            # Process pages in batches
            current_page = 1
            while current_page <= total_pages:
                end_page = min(current_page + page_batch_size - 1, total_pages)
                page_range = f"{current_page}-{end_page}"
                
                print(f"[{filename}] Processing pages {page_range}")
                try:
                    poller = await client.begin_analyze_document(
                        "prebuilt-layout",
                        document_content,
                        content_type="application/pdf",
                        output_content_format="markdown",
                        pages=page_range
                    )
                    
                    # Wait for the batch to complete with timeout
                    batch_timeout = time.time() + MAX_WAIT_TIME
                    result = None
                    while time.time() < batch_timeout:
                        await asyncio.sleep(5)
                        try:
                            result = await poller.result()
                            break
                        except Exception as e:
                            if "operation is not complete" in str(e):
                                elapsed_time = time.time() - start_time
                                print(f"[{filename}] Processing... Time elapsed: {elapsed_time:.1f} seconds")
                                if elapsed_time > MAX_WAIT_TIME:
                                    raise TimeoutError(f"Operation timed out after {MAX_WAIT_TIME} seconds")
                                continue
                            raise
                    
                    if result and result.content:
                        all_content.append(result.content)
                        processed_pages.update(range(current_page, end_page + 1))
                        print(f"[{filename}] Successfully processed pages {page_range}")
                    else:
                        print(f"[{filename}] No content returned for pages {page_range}")
                        failed_pages.update(range(current_page, end_page + 1))
                        
                except Exception as e:
                    print(f"[{filename}] Error processing pages {page_range}: {str(e)}")
                    failed_pages.update(range(current_page, end_page + 1))
                    await asyncio.sleep(5)
                
                # Move to next batch
                current_page = end_page + 1
                # Add a small delay between batches
                await asyncio.sleep(2)
            
            # Report processing status
            print(f"\n[{filename}] Processing Summary:")
            print(f"Total pages in PDF: {total_pages}")
            print(f"Successfully processed pages: {sorted(list(processed_pages))}")
            if failed_pages:
                print(f"Failed to process pages: {sorted(list(failed_pages))}")
                
                # Retry failed pages individually
                print(f"\n[{filename}] Retrying failed pages individually...")
                for page in sorted(failed_pages):
                    try:
                        print(f"[{filename}] Retrying page {page}")
                        poller = await client.begin_analyze_document(
                            "prebuilt-layout",
                            document_content,
                            content_type="application/pdf",
                            output_content_format="markdown",
                            pages=str(page)
                        )
                        
                        # Wait for single page with extended timeout
                        single_page_timeout = time.time() + MAX_WAIT_TIME * 2
                        while time.time() < single_page_timeout:
                            await asyncio.sleep(5)
                            try:
                                result = await poller.result()
                                if result and result.content:
                                    all_content.append(result.content)
                                    processed_pages.add(page)
                                    print(f"[{filename}] Successfully processed page {page}")
                                    break
                            except Exception as e:
                                if "operation is not complete" not in str(e):
                                    raise
                                elapsed_time = time.time() - start_time
                                print(f"[{filename}] Still processing... Time elapsed: {elapsed_time:.1f} seconds")
                                continue
                        
                        # Add delay between retries
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"[{filename}] Failed to process page {page}: {str(e)}")
            
            # Combine all content
            combined_content = "\n<!-- PageBreak -->\n".join(all_content)
            
            # Clean up and post-process the markdown content
            if combined_content:
                content = combined_content
                
                # Remove duplicate headers that appear at page breaks
                content = content.replace('<!-- PageBreak -->\n\n\n<figure>\n\nPETROVIETNAM\n\n</figure>', '<!-- PageBreak -->')
                
                # Clean up page footers and improve table formatting
                lines = content.split('\n')
                cleaned_lines = []
                skip_next = False
                in_table = False
                last_was_page_marker = False
                
                for i, line in enumerate(lines):
                    if skip_next:
                        skip_next = False
                        continue
                    
                    line = line.strip()
                    
                    # Skip empty page numbers and consecutive page markers
                    if line.startswith('<!-- PageNumber='):
                        if last_was_page_marker:
                            continue
                        last_was_page_marker = True
                    else:
                        last_was_page_marker = False
                        
                    # Handle tables
                    if '|' in line and not line.startswith('<!--'):
                        if not in_table:
                            in_table = True
                            # Add table marker if not present
                            if cleaned_lines and not cleaned_lines[-1].startswith('|'):
                                cleaned_lines.append('')
                        
                    elif in_table and not '|' in line:
                        in_table = False
                        if line:
                            cleaned_lines.append('')
                    
                    # Skip duplicate page footers
                    if line.startswith('<!-- PageFooter='):
                        if i + 1 < len(lines) and lines[i + 1].strip().startswith('<!-- PageFooter='):
                            skip_next = True
                            continue
                    
                    # Add extra newline before headers
                    if line.startswith('#') and cleaned_lines and not cleaned_lines[-1] == '':
                        cleaned_lines.append('')
                    
                    # Only add non-empty lines or specific markers
                    if line or line.startswith('<!-- PageBreak -->'):
                        cleaned_lines.append(line)
                    
                    # Add extra newline after headers
                    if line.startswith('#'):
                        cleaned_lines.append('')
                
                # Remove consecutive blank lines
                final_lines = []
                last_was_blank = False
                for line in cleaned_lines:
                    if not line:
                        if not last_was_blank:
                            final_lines.append(line)
                        last_was_blank = True
                    else:
                        final_lines.append(line)
                        last_was_blank = False
                
                content = '\n'.join(final_lines)
                
                # Save the cleaned content
                with open(output_path, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(content)
                    print(f"[{filename}] Results saved to {output_path} ({len(content)} characters)")
                    
                    # Print first few lines as preview
                    preview_lines = content.split('\n')[:10]
                    print("\n[{filename}] Preview of first few lines:")
                    for line in preview_lines:
                        if line.strip():
                            print(line)
            else:
                print(f"[{filename}] Warning: No content returned from the analysis")
        
        except Exception as api_error:
            print(f"[{filename}] API Error details: {str(api_error)}")
            raise
            
    except Exception as e:
        print(f"[{filename}] Error processing {file_path}: {str(e)}")
        raise

class ProcessingProgress:
    def __init__(self, total_files):
        self.total_files = total_files
        self.completed_files = 0
        self.failed_files = 0
        self.lock = asyncio.Lock()
    
    async def mark_completed(self, filename):
        async with self.lock:
            self.completed_files += 1
            print(f"\n[Progress] {self.completed_files}/{self.total_files} files completed - {filename} finished successfully")
    
    async def mark_failed(self, filename, error):
        async with self.lock:
            self.failed_files += 1
            print(f"\n[Progress] {self.completed_files}/{self.total_files} files completed - {filename} failed: {error}")

async def process_file_with_progress(input_path, output_path, client, progress_tracker, page_batch_size=DEFAULT_PAGE_BATCH_SIZE):
    filename = os.path.basename(input_path)
    try:
        await analyze_file_via_doci_async(input_path, output_path, client, page_batch_size=page_batch_size)
        await progress_tracker.mark_completed(filename)
    except Exception as e:
        await progress_tracker.mark_failed(filename, str(e))
        raise

async def process_documents_async(input_folder, output_folder, page_batch_size=DEFAULT_PAGE_BATCH_SIZE, concurrent_files=DEFAULT_CONCURRENT_FILES):
    """
    Process all PDF documents in the input folder asynchronously
    Args:
        input_folder: Folder containing PDF files
        output_folder: Folder to save markdown output
        page_batch_size: Number of pages to process in one batch
        concurrent_files: Number of files to process concurrently
    """
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT').rstrip('/')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    print(f"Using Document Intelligence endpoint: {endpoint}")
    print(f"Configuration: {concurrent_files} concurrent files, {page_batch_size} pages per batch\n")

    # Create async client
    client = AsyncDocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        api_version="2024-11-30"
    )

    # Get list of PDF files
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files to process:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    print()
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Initialize progress tracker
    progress = ProcessingProgress(len(pdf_files))

    async with client:
        # Process files in batches of concurrent_files
        for i in range(0, len(pdf_files), concurrent_files):
            batch_files = pdf_files[i:i + concurrent_files]
            tasks = []
            
            for pdf_file in batch_files:
                input_path = os.path.abspath(os.path.join(input_folder, pdf_file))
                output_path = os.path.abspath(os.path.join(
                    output_folder, 
                    pdf_file.rsplit('.', 1)[0] + '.md'
                ))
                
                task = process_file_with_progress(
                    input_path, 
                    output_path, 
                    client, 
                    progress,
                    page_batch_size=page_batch_size
                )
                tasks.append(task)
            
            # Process current batch of files concurrently
            try:
                await asyncio.gather(*tasks)
                if i + concurrent_files < len(pdf_files):
                    print(f"\nMoving to next batch of files...")
            except Exception as e:
                print(f"\nError during batch processing: {str(e)}")
                # Continue with next batch even if current batch has errors
                continue
        
        print(f"\nProcessing complete!")
        print(f"Successfully processed: {progress.completed_files}/{progress.total_files}")
        if progress.failed_files > 0:
            print(f"Failed to process: {progress.failed_files} files")

if __name__ == "__main__":
    # First test the connection
    if not test_connection():
        print("Failed to connect to Azure Document Intelligence service. Please check your credentials and endpoint.")
        exit(1)

    # Get input and output folders
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, "docs", "original_files")
    output_folder = os.path.join(script_dir, "docs", "input")
    
    # Get batch sizes from environment variables or use defaults
    page_batch_size = int(os.getenv('PAGE_BATCH_SIZE', DEFAULT_PAGE_BATCH_SIZE))
    concurrent_files = int(os.getenv('CONCURRENT_FILES', DEFAULT_CONCURRENT_FILES))

    # Run the async processing
    asyncio.run(process_documents_async(
        input_folder, 
        output_folder,
        page_batch_size=page_batch_size,
        concurrent_files=concurrent_files
    ))
    # Get batch sizes from environment variables or use defaults
    page_batch_size = int(os.getenv('PAGE_BATCH_SIZE', DEFAULT_PAGE_BATCH_SIZE))
    concurrent_files = int(os.getenv('CONCURRENT_FILES', DEFAULT_CONCURRENT_FILES))

    # Run the async processing
    asyncio.run(process_documents_async(
        input_folder, 
        output_folder,
        page_batch_size=page_batch_size,
        concurrent_files=concurrent_files
    ))