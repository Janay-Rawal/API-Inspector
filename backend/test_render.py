import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.parser import fallback_html_scan
print(fallback_html_scan("https://dummyjson.com"))