"""End-to-end browser qualification for PySRMKit + Next.js dashboard integration."""

from __future__ import annotations

from pathlib import Path

import pytest
from examples.run_stack import run_integration_stack


@pytest.mark.integration
def test_nextjs_suppliers_browser_journey() -> None:
    dashboard_root = (
        Path(__file__).resolve().parent.parent.parent / "resources" / "nextjs-acme-dashboard"
    )
    if not (dashboard_root / "app").is_dir():
        pytest.skip("Next.js Acme Dashboard is not present in workspace")

    from playwright.sync_api import expect, sync_playwright

    with run_integration_stack(api_port=8000, dashboard_port=3000) as urls:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            page = context.new_page()

            # 1. Login
            page.goto(f"{urls['dashboard_url']}/login", wait_until="networkidle")
            page.fill("input#email", "user@nextmail.com")
            page.fill("input#password", "123456")
            page.click("button:has-text('Log in')")

            # 2. Assert redirect to dashboard
            page.wait_for_url("**/dashboard")
            assert "/dashboard" in page.url

            # 3. Navigate to Suppliers page
            page.click("a[href='/dashboard/suppliers']")
            page.wait_for_url("**/dashboard/suppliers")

            # 4. Verify supplier network header and all 8 demo suppliers
            page.wait_for_selector("h1:has-text('Supplier network')")
            desktop_table = page.locator("table")
            expect(desktop_table).to_be_visible()

            supplier_names = [
                "Asteria Components SAS",
                "Boreal Freight AB",
                "Cobalt Cloud GmbH",
                "Delta Packaging BV",
                "Eira Consulting Ltd",
                "Faro Energia SA",
                "Gaia Materials SRL",
                "Helios Data Oy",
            ]
            for name in supplier_names:
                expect(desktop_table.get_by_text(name)).to_be_visible()

            expect(desktop_table.locator("tbody tr")).to_have_count(8)

            # A4-04: the dashboard intentionally uses the legacy HTTP route.
            # Its search includes vendor codes and country; the new canonical
            # route only matches legal/trading names. Verify both contracts
            # against the real API service, not an in-process mocked route.
            legacy_vendor = page.request.get(
                f"{urls['api_url']}/suppliers?query=SUP-008"
            )
            canonical_vendor = page.request.get(
                f"{urls['api_url']}/suppliers/search?query=SUP-008"
            )
            legacy_country = page.request.get(
                f"{urls['api_url']}/suppliers?query=FI"
            )
            canonical_country = page.request.get(
                f"{urls['api_url']}/suppliers/search?query=FI"
            )
            assert legacy_vendor.status == canonical_vendor.status == 200
            assert legacy_country.status == canonical_country.status == 200
            assert [item["legal_name"] for item in legacy_vendor.json()["items"]] == [
                "Helios Data Oy"
            ]
            assert canonical_vendor.json()["total"] == 0
            assert [item["legal_name"] for item in legacy_country.json()["items"]] == [
                "Helios Data Oy"
            ]
            assert canonical_country.json()["total"] == 0

            # The browser search must retain legacy vendor-code matching.
            search_input = page.locator("input[placeholder*='Search suppliers']")
            search_input.fill("SUP-008")
            page.wait_for_url(lambda u: "query=SUP-008" in u)
            expect(desktop_table.locator("tbody tr")).to_have_count(1)
            expect(desktop_table.get_by_text("Helios Data Oy")).to_be_visible()

            # Clear before running the preexisting name-search journey.
            search_input.fill("")
            page.wait_for_url(lambda u: "query=" not in u)
            expect(desktop_table.locator("tbody tr")).to_have_count(8)

            # 5. Search filtering (debounced 300ms)
            search_input = page.locator("input[placeholder*='Search suppliers']")
            search_input.fill("Asteria")
            page.wait_for_url(lambda u: "query=Asteria" in u)

            expect(desktop_table.get_by_text("Asteria Components SAS")).to_be_visible()
            expect(desktop_table.get_by_text("Helios Data Oy")).to_have_count(0)
            expect(desktop_table.locator("tbody tr")).to_have_count(1)

            # 6. Clear search
            search_input.fill("")
            page.wait_for_url(lambda u: "query=" not in u)

            expect(desktop_table.get_by_text("Helios Data Oy")).to_be_visible()
            expect(desktop_table.locator("tbody tr")).to_have_count(8)

            # 7. Refresh action
            refresh_btn = page.get_by_role("button", name="Reload suppliers")
            expect(refresh_btn).to_be_visible()
            refresh_btn.click()
            expect(desktop_table.get_by_text("Asteria Components SAS")).to_be_visible()
            expect(desktop_table.locator("tbody tr")).to_have_count(8)

            browser.close()
