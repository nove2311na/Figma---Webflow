import os
import sys
import argparse

# Add root folder to sys.path to resolve tools imports
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.append(root_dir)

from css_indexer.contract_builder import ContractBuilder

def main():
    parser = argparse.ArgumentParser(description="Client-First CSS Contract Indexer CLI")
    parser.add_argument("--normalize", required=True, help="Path to normalize.css")
    parser.add_argument("--webflow", required=True, help="Path to webflow.css")
    parser.add_argument("--client-first", required=True, help="Path to client-first CSS file")
    parser.add_argument("--out", required=True, help="Output directory for generated JSON contracts")
    
    args = parser.parse_args()
    
    # Note: argparse converts dashes in variable names to underscores, so args.client_first works
    if not os.path.exists(args.normalize):
        print(f"Error: normalize.css not found at {args.normalize}")
        sys.exit(1)
    if not os.path.exists(args.webflow):
        print(f"Error: webflow.css not found at {args.webflow}")
        sys.exit(1)
    if not os.path.exists(args.client_first):
        print(f"Error: client-first CSS not found at {args.client_first}")
        sys.exit(1)
        
    print("Starting CSS indexing...")
    builder = ContractBuilder(args.normalize, args.webflow, args.client_first)
    builder.build(args.out)
    print("CSS indexing complete.")

if __name__ == "__main__":
    main()
