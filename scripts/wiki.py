import requests
import sys

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

if len(sys.argv) < 2:
    command = "random"
    print("Use 'random', 'backlinks', 'search' <query>, 'links' <page_title>, or 'find' <query>")
else:
    command = sys.argv[1].lower()
    limit = 10
if command == "random":
    try:
        response = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/random/summary",
            headers=HEADERS,
            timeout=5
        )
        response.raise_for_status()
        
        article = response.json()
        print()
        print(article["title"])
        print()
        print(article["extract"])
     
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Wikipedia API may be slow.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {response.status_code} - {e}")
        sys.exit(1)
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Invalid JSON response from Wikipedia API")
        print(f"Response: {response.text[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
elif command == "backlinks":
    if len(sys.argv) < 4:
        print("Usage: wiki backlinks <limit> <page_title>")
        sys.exit(1)
    
    try:
        limit = int(sys.argv[2])
        page_title = " ".join(sys.argv[3:]) 
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "backlinks",
                "bltitle": page_title,
                "blnamespace": 0,
                "bllimit": limit,
                "format": "json"
            },
            headers=HEADERS,
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        backlinks = data.get("query", {}).get("backlinks", [])
        
        if not backlinks:
            print(f"No backlinks found for '{page_title}'")
            sys.exit(0)
        
        print(f"Pages linking to '{page_title}':")
        for i, link in enumerate(backlinks[:limit], start=1):
            print(f"{i}. {link['title']}")
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Wikipedia API may be slow.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {response.status_code} - {e}")
        sys.exit(1)
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Invalid JSON response from Wikipedia API")
        print(f"Response: {response.text[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

elif command == "search":
    if len(sys.argv) < 3:
        print("Usage: wiki search <query>")
        sys.exit(1)
    
    try:
        query = " ".join(sys.argv[2:])
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json"
            },
            headers=HEADERS,
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        results = data["query"]["search"]
        
        if not results:
            print("No results found")
            sys.exit(0)
        
        print(f"Results for '{query}':")
        for i, result in enumerate(results[:limit], start=1):
            print(f"{i}. {result['title']}")
            
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Wikipedia API may be slow.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {response.status_code} - {e}")
        sys.exit(1)
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Invalid JSON response from Wikipedia API")
        print(f"Response: {response.text[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
elif command == "links":
    if len(sys.argv) < 4:
        print("Usage: wiki links <limit> <page_title>")
        sys.exit(1)
    
    try:
        limit = int(sys.argv[2])
        query = " ".join(sys.argv[3:])
        
        # Search for exact title first
        search_response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json"
            },
            headers=HEADERS,
            timeout=5
        )
        search_response.raise_for_status()
        
        search_data = search_response.json()
        results = search_data.get("query", {}).get("search", [])
        
        if not results:
            print(f"Page '{query}' not found")
            sys.exit(1)
        
        exact_title = results[0]["title"]
        
        # Fetch links from exact title
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "titles": exact_title,
                "prop": "links",
                "plnamespace": 0,
                "pllimit": limit,
                "format": "json"
            },
            headers=HEADERS,
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        page_data = list(pages.values())[0]
        links = page_data.get("links", [])
        
        if not links:
            print(f"No internal links found on '{exact_title}'")
            sys.exit(0)
        
        has_more = "continue" in data
        
        print(f"Links from '{exact_title}' ({len(links)} shown)")
        if has_more:
            print("(More links exist)")
        print()
        
        for i, link in enumerate(links, start=1):
            print(f"{i}. {link['title']}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
elif command == "find":
    if len(sys.argv) < 3:
        print("Usage: wiki find <search_query>")
        sys.exit(1)
    
    try:
        query = " ".join(sys.argv[2:])
        
        # First, search for the page
        search_response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json"
            },
            headers=HEADERS,
            timeout=5
        )
        search_response.raise_for_status()
        
        search_data = search_response.json()
        results = search_data.get("query", {}).get("search", [])
        
        if not results:
            print(f"No Wikipedia article found for '{query}'")
            sys.exit(1)
        
        # Get the first result's title
        top_result = results[0]["title"]
       
        # Fetch full article summary
        article_response = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{top_result}",
            headers=HEADERS,
            timeout=5
        )
        article_response.raise_for_status()
        
        article = article_response.json()
        
        print(f"Best match for '{query}':")
        print()
        print(article["title"])
        print()
        print(article["extract"])
        print()
        print(f"https://en.wikipedia.org/wiki/{top_result.replace(' ', '_')}")
        
    except requests.exceptions.Timeout:
        print("Error: Request timed out.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {search_response.status_code if 'search_response' in locals() else article_response.status_code}")
        sys.exit(1)
    except requests.exceptions.JSONDecodeError:
        print(f"Error: Invalid JSON response")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
else:
    print(f"Unknown command: {command}")
    print("Use 'random', 'backlinks', 'search' <query>, 'links' <page_title>, or 'find' <query>")
    sys.exit(1)