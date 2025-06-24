import sys
import os

# Assuming the 'engines' directory is in the same directory as this script.
# Adjust if necessary, e.g., if run_test.py is in an 'examples' subdirectory.
sys.path.insert(0, os.path.dirname(__file__))

from engines import arxiv # Import from the new 'engines' directory

def main():
    print("Testing arxiv engine...")

    # --- Test request function ---
    query = "black hole"
    # Mock params that the arxiv.request function expects
    # pageno is essential for arxiv
    mock_request_params = {
        'pageno': 1,
        # other params like 'time_range', 'language', 'region' can be added if the engine uses them.
        # For arxiv, pageno is the main one from its original structure.
    }

    print(f"  Query: {query}")
    print(f"  Initial mock_request_params: {mock_request_params}")

    try:
        # Call the engine's request function
        # The function is expected to modify mock_request_params, typically adding 'url' and 'headers'.
        # It might also add 'cookies' if the engine needs them.
        returned_params = arxiv.request(query, mock_request_params)

        # The convention is often that the passed-in dict is modified directly,
        # but some engines might return a new dict or the modified one.
        # We'll assume returned_params is the one to use.

        print(f"  Params after arxiv.request call: {returned_params}")

        if 'url' not in returned_params:
            print("  ERROR: 'url' not found in params returned by request function.")
            return
        else:
            print(f"  Generated URL: {returned_params['url']}")

        # If headers are expected (arxiv doesn't explicitly set them in its request from what we saw)
        # if 'headers' in returned_params:
        # print(f"  Generated Headers: {returned_params['headers']}")

    except Exception as e:
        print(f"  ERROR during arxiv.request call: {e}")
        return

    # --- Test response function ---
    # Mock a response object that arxiv.response expects.
    # arxiv.py expects resp.content to be a byte string of XML.
    # We'll use a very minimal mock XML structure.

    # A simplified example of what Arxiv might return for one entry
    mock_xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2301.00001v1</id>
    <updated>2023-01-01T15:00:00Z</updated>
    <published>2023-01-01T15:00:00Z</published>
    <title>A Mock Paper on Black Holes</title>
    <summary>This is a brief summary of the mock paper about black holes and their amazing properties.</summary>
    <author><name>Dr. Mock Tester</name></author>
    <arxiv:doi>10.0000/mockdoi.2023.001</arxiv:doi>
    <link title="pdf" href="http://arxiv.org/pdf/2301.00001v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category term="astro-ph.HE" scheme="http://arxiv.org/schemas/atom"/>
    <category term="astro-ph.HE" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>
"""

    class MockResponse:
        def __init__(self, content, status_code=200, text=None):
            self.content = content # bytes
            self.status_code = status_code
            self.text = text if text is not None else content.decode('utf-8', errors='replace') # str

        def json(self): # If an engine expects JSON
            import json
            return json.loads(self.text)

    mock_resp = MockResponse(content=mock_xml_content)

    print(f"\n  Mocking response for arxiv.response function...")
    try:
        results = arxiv.response(mock_resp)
        print(f"  Results from arxiv.response: ")
        if results:
            for i, res_dict in enumerate(results):
                print(f"    Result {i+1}:")
                for key, value in res_dict.items():
                    # Truncate long values for display
                    display_value = str(value)
                    if len(display_value) > 70:
                        display_value = display_value[:67] + "..."
                    print(f"      {key}: {display_value}")
        else:
            print("    No results returned or results list is empty.")

    except Exception as e:
        print(f"  ERROR during arxiv.response call: {e}")
        # import traceback
        # traceback.print_exc() # For more detailed error during development

    print("\nTest complete.")

if __name__ == "__main__":
    main()
