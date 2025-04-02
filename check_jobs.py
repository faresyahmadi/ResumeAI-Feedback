from services.supabase_service import SupabaseService

def check_jobs():
    service = SupabaseService()
    
    # Get all documents
    print("\nFetching all documents...")
    all_docs = service.get_documents()
    print(f"Total documents found: {len(all_docs)}")
    
    # Get job descriptions specifically
    print("\nFetching job descriptions...")
    job_descriptions = service.get_job_descriptions()
    print(f"Job descriptions found: {len(job_descriptions)}")
    
    # Print details of each job description
    print("\nJob Description Details:")
    for job in job_descriptions:
        print("\n---")
        print(f"Title: {job.get('metadata', {}).get('title', 'No title')}")
        print(f"Content length: {len(job.get('content', ''))} characters")
        print(f"First 200 chars of content: {job.get('content', '')[:200]}...")
        print("---")

if __name__ == "__main__":
    check_jobs() 