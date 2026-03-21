"""
Demo Script - Run Vector LangGraph Pipeline
Shows how to execute the pipeline programmatically without FastAPI
"""

import asyncio
from graph import vector_pipeline
from graph_state import VectorAgentState


async def main():
    """
    Run a test execution of the Vector pipeline
    """
    print("\n" + "=" * 80)
    print("VECTOR LANGGRAPH PIPELINE - DEMO RUN")
    print("=" * 80)

    # Create initial state from a simulated GitHub webhook
    initial_state = VectorAgentState(
        webhook_id="demo-webhook-001",
        repo_name="api-service",
        repo_url="https://github.com/company/api-service",
        commit_sha="abc123def456789",
        commit_message="Add email validation to user endpoints"
    )

    # Execute the pipeline
    print("\n[STARTING EXECUTION]")
    print(f"Webhook ID: {initial_state.webhook_id}")
    print(f"Repository: {initial_state.repo_name}")
    print(f"Commit: {initial_state.commit_sha}")
    print(f"Message: {initial_state.commit_message}")

    try:
        # Invoke the compiled graph
        final_state_dict = vector_pipeline.invoke(initial_state.dict())

        # Convert back to state object
        final_state = VectorAgentState(**final_state_dict)

        # Display results
        print("\n" + "=" * 80)
        print("PIPELINE EXECUTION RESULTS")
        print("=" * 80)

        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {final_state.total_tests_run}")
        print(f"   Passed: {final_state.tests_passed} ✓")
        print(f"   Failed: {final_state.tests_failed} ✗")
        print(f"   Success Rate: {(final_state.tests_passed/final_state.total_tests_run*100):.1f}%")

        print(f"\n🔗 Analyzed Endpoints:")
        for endpoint in final_state.analyzed_endpoints:
            print(f"   • {endpoint['method']} {endpoint['path']}")

        if final_state.failure_analysis:
            print(f"\n⚠️  Failure Analysis ({len(final_state.failure_analysis)} issues):")
            for failure in final_state.failure_analysis:
                print(f"\n   [{failure['severity']}] {failure['test_name']}")
                print(f"       Error: {failure['error']}")
                print(f"       Fix: {failure['suggested_fix']}")

        print(f"\n📄 Generated Reports:")
        print(f"   Markdown: {len(final_state.report_markdown)} characters")
        print(f"   JSON: {len(str(final_state.report_json))} characters")

        print(f"\n✅ Pipeline Status: {final_state.status}")

        # Print markdown report sample
        print("\n" + "-" * 80)
        print("MARKDOWN REPORT (First 1000 chars):")
        print("-" * 80)
        print(final_state.report_markdown[:1000] + "...")

        return final_state

    except Exception as e:
        print(f"\n❌ Pipeline execution failed:")
        print(f"   Error: {str(e)}")
        raise


if __name__ == "__main__":
    # Run the async pipeline
    final_state = asyncio.run(main())

    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
