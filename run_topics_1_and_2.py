import asyncio
import json
import logging
from app.services.topic1_service import Topic1Service
from app.services.topic2_service import Topic2Service

# Configure basic logging to see progression in stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


async def run_full_audit(url: str):
    print("=" * 60)
    print(f"RUNNING UNIFIED AUDIT FOR: {url}")
    print("=" * 60)

    # Instantiate services
    topic1 = Topic1Service()
    topic2 = Topic2Service()

    # Run Topic 1 & Topic 2 concurrently
    print("\nExecuting Topic 1 (Accessibility & Cookies) and Topic 2 concurrently...")
    t1_result, t2_result = await asyncio.gather(
        topic1.execute_audit(url),
        topic2.execute_audit(url),
        return_exceptions=True
    )

    combined_output = {
        "target_url": url,
        "topic_1_accessibility_privacy": t1_result if not isinstance(t1_result, Exception) else {"error": str(t1_result)},
        "topic_2_results": t2_result if not isinstance(t2_result, Exception) else {"error": str(t2_result)},
    }

    print("\n" + "=" * 60)
    print("UNIFIED AUDIT COMPLETE")
    print("=" * 60)
    
    # Save unified JSON
    output_filename = "topics_1_and_2_report.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(combined_output, f, indent=2)
        
    print(f"\nComplete results saved to '{output_filename}'")


if __name__ == "__main__":
    target = "https://www.bowlerhat.co.uk"
    asyncio.run(run_full_audit(target))