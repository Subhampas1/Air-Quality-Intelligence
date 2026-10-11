Proceed with the Air Quality Intelligence & Pollution Risk Analysis Platform implementation plan, with the following mandatory corrections:

1. Before coding, inspect the actual CSV files and verify their schemas, row counts, date coverage, missing values, duplicates, AQI categories, and city-name consistency. Do not assume the proposed inspection figures are correct without checking.

2. Do not directly merge station-level records into city-day observations. First create a verified one-row-per-city metadata lookup, and use it only where city mappings are reliable. Ensure the join cannot multiply observation rows. If matching is ambiguous, omit the metadata rather than inventing a match.

3. Apply AQI category boundaries consistently. Calculate risk percentages only from valid AQI observations and show their denominators. Describe risk tiers as project-defined analytical indicators, not official regulatory warnings.

4. Make all KPIs, charts, rankings, insights, and recommendations derive from the current data and selected filters. Include observation counts and relevant caveats. Never hardcode findings or claim causation from correlation.

5. Prioritize a clean, minimal, professional interface. Keep each page focused on its primary purpose; place secondary tables and technical details in expanders rather than overcrowding the screen.

6. Implement the four pages and the required files: air_quality_app.py, requirements.txt, README.md, and project_report.docx. Keep the original CSV files unchanged.

7. Test the app with the actual datasets, including empty filters, missing values, single-city selections, and date filtering. Run the application and fix runtime errors wherever the environment allows.

8. Generate the report using actual implementation details and verified findings. Clearly mark any screenshot placeholders and incomplete tests. After the app runs, capture genuine dashboard screenshots and update the report and README.

9. Do not claim implementation, testing, screenshot capture, or report completion until each has actually occurred.

Start by completing data inspection and presenting a concise implementation summary. Then implement and test the project in the workspace. Create the files directly rather than merely printing code in the chat.