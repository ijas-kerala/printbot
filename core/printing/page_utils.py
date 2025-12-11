from typing import List, Set

def parse_page_range(range_str: str, total_pages: int) -> List[int]:
    """
    Parses a page range string into a list of specific 0-indexed page numbers.
    
    Args:
        range_str (str): The string input, e.g. "1-5, 8, 10-12" or "all" or ""
        total_pages (int): The total number of pages in the document.
        
    Returns:
        List[int]: A sorted list of unique 0-indexed page numbers to print.
                   Returns [0, 1, ... total_pages-1] if input is empty or 'all'.
                   Ignores out-of-range pages.
    """
    if not range_str or not range_str.strip() or range_str.lower() == "all":
        return list(range(total_pages))
    
    pages: Set[int] = set()
    parts = range_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        try:
            if '-' in part:
                # Range: "1-5"
                start_str, end_str = part.split('-', 1)
                start = int(start_str)
                end = int(end_str)
                
                # Handle "min-max" logic if user typed backwards like "5-1" -> "1-5"
                if start > end:
                    start, end = end, start
                
                # Apply bounds immediately
                # User input is 1-indexed, we convert to 0-indexed for internal use later? 
                # Actually, standard print ranges are 1-based. Let's assume 1-based input.
                # We will output 1-based for now, OR 0-based? 
                # The prompt example said: "1,3-5" -> [1,3,4,5]. This implies 1-based.
                # Let's Stick to 1-based in, 0-based out for pypdf consumption? 
                # Wait, the prompt output example was [1,3,4,5...]. 
                # Let's return 0-based indices for pypdf, but the logic should handle 1-based input.
                
                for i in range(start, end + 1):
                    if 1 <= i <= total_pages:
                        pages.add(i - 1) # 0-indexed
            else:
                # Single page: "8"
                page = int(part)
                if 1 <= page <= total_pages:
                    pages.add(page - 1) # 0-indexed
                    
        except ValueError:
            # Ignore malformed parts like "a-b" or "xyz"
            continue
            
    sorted_pages = sorted(list(pages))
    
    # Fail-safe: If result is empty (e.g. all inputs were invalid), return ALL pages?
    # Or return empty list? Returning all pages might be safer for "user made a typo but paid".
    # But strictly, if I ask for page 100 in a 10 page doc, I get nothing.
    # Let's return empty if the explicit range was invalid but syntactically not "all".
    # User requirement: "all settings... must be printed exactly". 
    # If I say "1-5" and it's a 3 page doc, I expect 1,2,3.
    # If I say "50-60" and it's a 3 page doc, I expect nothing? Or error?
    # Let's stick to the logic: ignore out of bounds.
    
    return sorted_pages
