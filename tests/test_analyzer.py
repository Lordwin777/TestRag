import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.code_analyzer import CodeAnalyzer

SAMPLE_CODE = """def calculate_discount(price, discount):
    if price < 0:
        return "Invalid price"
    if discount < 0 or discount > 100:
        return "Invalid discount"
    final_price = price - (price * discount / 100)
    return final_price
"""

def test():
    analysis = CodeAnalyzer.analyze(SAMPLE_CODE, "Python")
    print("Language:", analysis["language"])
    print("Functions:", analysis["functions"])
    print("Conditions:", analysis["conditions"])
    print("Boundary Comparisons:", analysis["boundary_comparisons"])
    query = CodeAnalyzer.create_retrieval_query(analysis, "All")
    print("Generated Query:\n", query)

if __name__ == "__main__":
    test()
