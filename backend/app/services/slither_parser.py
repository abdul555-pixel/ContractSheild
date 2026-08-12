from app.models.finding import Finding


def parse_slither_output(raw_json: dict) -> list[Finding]:
    findings = []

    detectors = raw_json.get(
        "results",
        {}
    ).get(
        "detectors",
        []
    )

    for detector in detectors:

        # Pull the function name and line numbers from elements.
        # Some contract-level findings may not have a function element.
        function_name = "unknown"
        line_numbers = []

        elements = detector.get(
            "elements",
            []
        )

        for element in elements:

            if element.get("type") == "function":

                function_name = element.get(
                    "name",
                    "unknown"
                )

                line_numbers = element.get(
                    "source_mapping",
                    {}
                ).get(
                    "lines",
                    []
                )

                break

        finding = Finding(
            title=detector.get(
                "check",
                "Unknown Issue"
            ),
            description=detector.get(
                "description",
                ""
            ),
            severity=detector.get(
                "impact",
                "Unknown"
            ),
            function_name=function_name,
            line_numbers=line_numbers,
        )

        findings.append(finding)

    return findings