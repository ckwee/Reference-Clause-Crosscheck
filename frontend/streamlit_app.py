import csv
import io
import os
import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Reference Clause Crosscheck", layout="wide")

st.title("Reference Clause Crosscheck")
st.caption("Upload Acts, Regulations, SOPs, policies, standards, or other reference documents, then check each valid complaint statement against the exact relevant clauses.")

with st.sidebar:
    st.header("Settings")
    backend_url = st.text_input("Backend URL", BACKEND_URL)
    st.markdown("---")
    st.warning(
        "AI clause matching is decision support only. Verify every source, clause reference, "
        "quoted clause, and conclusion against the original documents."
    )

tab_check, tab_history = st.tabs(["New clause check", "History"])


def build_clause_rows(checks):
    rows = []
    for check in checks:
        matches = check.get("reference_matches", []) or []
        if not matches:
            rows.append({
                "Complaint statement": check.get("statement_name", ""),
                "Source type": "",
                "Source document": "",
                "Clause reference": "",
                "Match status": "Not addressed",
                "Clause text": "",
                "Explanation": check.get("conclusion", ""),
                "Items to verify": "; ".join(check.get("items_to_verify", [])),
            })
        for match in matches:
            rows.append({
                "Complaint statement": check.get("statement_name", ""),
                "Source type": match.get("source_type", ""),
                "Source document": match.get("source_name", ""),
                "Clause reference": match.get("clause_reference", ""),
                "Match status": match.get("match_status", ""),
                "Clause text": match.get("clause_text", ""),
                "Explanation": match.get("match_explanation", ""),
                "Items to verify": "; ".join(check.get("items_to_verify", [])),
            })
    return rows


def rows_to_csv(rows):
    output = io.StringIO()
    fieldnames = [
        "Complaint statement",
        "Source type",
        "Source document",
        "Clause reference",
        "Match status",
        "Clause text",
        "Explanation",
        "Items to verify",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def show_clause_matches(matches):
    st.markdown("#### Reference matches")
    if not matches:
        st.info("No reference match returned for this statement.")
        return
    for match in matches:
        with st.container(border=True):
            source_type = match.get("source_type", "Reference")
            source_name = match.get("source_name", "Source not returned")
            reference = match.get("clause_reference", "Clause reference not returned")
            st.markdown(f"**{source_type}: {source_name}**")
            st.markdown(f"**{reference}**")
            st.markdown(f"**Status:** {match.get('match_status', 'Not specified')}")
            st.markdown(match.get("match_explanation", ""))
            clause_text = match.get("clause_text", "")
            if clause_text:
                st.markdown("**Exact clause or requirement text**")
                st.code(clause_text, language="text")


with tab_check:
    review_title = st.text_input("Review title", "Untitled reference clause crosscheck")

    reference_files = st.file_uploader(
        "Reference documents",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="reference_files",
    )
    statement_files = st.file_uploader(
        "Valid complaint statements",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="statement_files",
    )

    if st.button("Check clauses", type="primary"):
        if not reference_files:
            st.error("Please upload at least one reference document, such as an Act, Regulation, SOP, policy, or standard.")
            st.stop()
        if not statement_files:
            st.error("Please upload at least one valid complaint statement.")
            st.stop()

        files = []
        files.extend(
            ("reference_files", (file.name, file.getvalue()))
            for file in reference_files
        )
        files.extend(
            ("complaint_statements", (file.name, file.getvalue()))
            for file in statement_files
        )

        with st.spinner("Checking complaint statements against reference clauses and requirements..."):
            response = requests.post(
                f"{backend_url}/check_files",
                data={"review_title": review_title},
                files=files,
                timeout=600,
            )

        if response.status_code != 200:
            st.error(response.text)
            st.stop()

        result = response.json()
        checks = result["checks"]
        rows = build_clause_rows(checks)

        st.success(f"Clause check complete. Saved run #{result['run_id']}.")

        st.download_button(
            label="Download clause crosscheck CSV",
            data=rows_to_csv(rows),
            file_name=f"reference_clause_crosscheck_run_{result['run_id']}.csv",
            mime="text/csv",
            key=f"download_current_reference_clause_crosscheck_csv_{result['run_id']}",
        )

        with st.expander("Extracted reference clauses and requirements"):
            st.json(result["reference_clauses"])

        for check in checks:
            with st.expander(check.get("statement_name", "Complaint statement"), expanded=True):
                statement_text = check.get("complaint_statement", "")
                if statement_text:
                    st.markdown("**Complaint statement**")
                    st.write(statement_text)
                st.markdown("**Conclusion**")
                st.write(check.get("conclusion", ""))

                show_clause_matches(check.get("reference_matches", []))

                items = check.get("items_to_verify", [])
                if items:
                    st.markdown("#### Items to verify")
                    for item in items:
                        st.markdown(f"- {item}")

with tab_history:
    if st.button("Refresh history"):
        st.rerun()

    response = requests.get(f"{backend_url}/reference_check_runs", timeout=30)

    if response.status_code != 200:
        st.error("Could not load history. Check that the backend is running.")
        st.stop()

    runs = response.json()

    if not runs:
        st.info("No saved clause checks yet.")
        st.stop()

    selected = st.selectbox(
        "Saved clause checks",
        runs,
        format_func=lambda run: (
            f"#{run['id']} - {run['review_title']} "
            f"({run['statement_count']} statements, {run['created_at']})"
        ),
    )

    detail = requests.get(
        f"{backend_url}/reference_check_runs/{selected['id']}",
        timeout=30,
    )

    if detail.status_code != 200:
        st.error("Could not load the selected run.")
        st.stop()

    run = detail.json()
    checks = run["checks"]
    rows = build_clause_rows(checks)

    st.subheader(run["review_title"])
    st.caption(f"Created: {run['created_at']}")
    st.caption(f"Reference documents: {run['reference_names']}")

    st.download_button(
        label="Download selected clause crosscheck CSV",
        data=rows_to_csv(rows),
        file_name=f"reference_clause_crosscheck_run_{run['id']}.csv",
        mime="text/csv",
        key=f"download_history_reference_clause_crosscheck_csv_{run['id']}",
    )

    for check in checks:
        with st.expander(check.get("statement_name", "Complaint statement")):
            st.write(check.get("conclusion", ""))
            show_clause_matches(check.get("reference_matches", []))
            items = check.get("items_to_verify", [])
            if items:
                st.markdown("#### Items to verify")
                for item in items:
                    st.markdown(f"- {item}")
