import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient as AsyncDocumentIntelligenceClient
from dotenv import load_dotenv
import os
import time
import json
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

MAX_WAIT_TIME = 300  # Maximum wait time in seconds (5 minutes)

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

async def analyze_file_via_doci_async(file_path, output_path, client):
    """
    Analyze a document using Azure Document Intelligence asynchronously
    """
    try:
        # Check if we have a progress file
        progress_file = output_path + '.progress'
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                progress_data = json.load(f)
                print(f"Resuming previous analysis from {progress_data['timestamp']}")
                if os.path.exists(output_path):
                    print(f"Output file already exists, skipping: {output_path}")
                    return
        
        with open(file_path, "rb") as f:
            document_content = f.read()
            
        print(f"File size: {len(document_content)} bytes")
        start_time = time.time()
            
        async with client:
            try:
                # Save progress
                with open(progress_file, 'w') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'status': 'started',
                        'file_size': len(document_content)
                    }, f)
                
                print(f"Starting analysis for {file_path}")
                poller = await client.begin_analyze_document(
                    "prebuilt-layout",
                    document_content,
                    content_type="application/pdf",
                    output_content_format="markdown",
                    pages="1-"
                )
                
                print(f"Analysis started for {file_path}")
                
                # Wait for the operation to complete with timeout
                timeout = start_time + MAX_WAIT_TIME
                while time.time() < timeout:
                    await asyncio.sleep(5)
                    try:
                        result = await poller
                        break
                    except Exception as e:
                        if "operation is not complete" in str(e):
                            elapsed_time = time.time() - start_time
                            print(f"Processing... Time elapsed: {elapsed_time:.1f} seconds")
                            if elapsed_time > MAX_WAIT_TIME:
                                print(f"Operation timed out after {MAX_WAIT_TIME} seconds")
                                raise TimeoutError(f"Operation timed out after {MAX_WAIT_TIME} seconds")
                            continue
                        raise
                
                print(f"Analysis completed for {file_path}")
                print(f"Number of pages processed: {len(result.pages) if hasattr(result, 'pages') else 'Unknown'}")
                
                # Save the markdown content with UTF-8 encoding
                with open(output_path, "w", encoding="utf-8", errors="ignore") as f:
                    if result.content:
                        f.write(result.content)
                        print(f"Results saved to {output_path} ({len(result.content)} characters)")
                        
                        # Print first few lines as preview
                        preview_lines = result.content.split('\n')[:10]
                        print("\nPreview of first few lines:")
                        for line in preview_lines:
                            if line.strip():
                                print(line)
                    else:
                        print("Warning: No content returned from the analysis")
                
                # Update progress
                with open(progress_file, 'w') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'status': 'completed',
                        'file_size': len(document_content),
                        'output_size': len(result.content) if result.content else 0
                    }, f)
                
            except Exception as api_error:
                print(f"API Error details: {str(api_error)}")
                raise
                
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        raise

async def process_documents_async(input_folder, output_folder):
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT').rstrip('/')  # Remove trailing slash
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    if not endpoint or not key:
        raise ValueError("Azure Document Intelligence credentials not found in environment variables")
    
    print(f"Using Document Intelligence endpoint: {endpoint}")
    
    # Create async client
    client = AsyncDocumentIntelligenceClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key),
        api_version="2024-11-30"
    )
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Process each file
    tasks = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.pdf', '.docx')):
            input_path = os.path.abspath(os.path.join(input_folder, filename))
            output_path = os.path.abspath(os.path.join(
                output_folder, 
                filename.rsplit('.', 1)[0] + '.md'
            ))
            
            print(f"\nProcessing file {filename}")
            print(f"Input path: {input_path}")
            print(f"Output path: {output_path}")
            
            task = analyze_file_via_doci_async(input_path, output_path, client)
            tasks.append(task)
    
    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # First test the connection
    if not test_connection():
        print("Failed to connect to Azure Document Intelligence service. Please check your credentials and endpoint.")
        exit(1)
        
    # Configure your input and output folders
    input_folder = os.getenv('INPUT_FOLDER', '/Users/hieunguyennhu/Downloads/pvngraphrag/docs/original_files')
    output_folder = os.getenv('OUTPUT_FOLDER', '/Users/hieunguyennhu/Downloads/pvngraphrag/docs/input')
    
    # Run the async process
    asyncio.run(process_documents_async(input_folder, output_folder))