from pings.security_ping import check_security_headers
from parsers.semrush_parser import parse_semrush_csv
from engine.scorer import score_security, score_organic_search

print("--- TESTING SECTION 1 ---")
sec_data = check_security_headers("https://www.google.com")
sec_score = score_security(sec_data["has_ssl"], sec_data["https_enforced"])
print(f"Security Details: {sec_data}")
print(f"Section 1 Score: {sec_score} / 100\n")

print("--- TESTING SECTION 2 ---")
parsed_semrush = parse_semrush_csv("input_csvs/semrush_organic_export.csv")

# Simulated competitor benchmarks for testing
avg_comp_traffic = 2500
avg_comp_authority = 35

org_score = score_organic_search(
    page_1_keywords=parsed_semrush["page_1_keywords"],
    page_2_keywords=parsed_semrush["page_2_keywords"],
    serp_distribution=parsed_semrush["metrics"]["serp_distribution"],
    client_traffic=parsed_semrush["metrics"]["est_monthly_traffic"],
    avg_competitor_traffic=avg_comp_traffic,
    client_authority=parsed_semrush["metrics"]["domain_authority"],
    avg_competitor_authority=avg_comp_authority
)

print(f"SERP Distribution: {parsed_semrush['metrics']['serp_distribution']}")
print(f"Page 1 Keywords Found (vol >= 30): {len(parsed_semrush['page_1_keywords'])}")
print(f"Page 2 Keywords Found (vol >= 30): {len(parsed_semrush['page_2_keywords'])}")
print(f"Section 2 Score Result: {org_score}")
