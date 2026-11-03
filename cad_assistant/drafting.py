def build_drafting_recommendations(step: dict, dxf: dict, sheet: str, projection: str) -> dict:
    bb = step["bounding_box"]
    axes = [("X", bb["x"]), ("Y", bb["y"]), ("Z", bb["z"])]
    axes.sort(key=lambda item: item[1], reverse=True)

    # Heuristic only: the largest projected face is usually a useful starting view.
    # The actual front orientation must be confirmed by the operator.
    views = [
        {"view": "Primary view (provisional)", "orientation": f"Looking along {axes[2][0]} axis",
         "reason": "Shows the two largest overall dimensions."},
        {"view": "Top view (provisional)", "orientation": f"Looking along {axes[1][0]} axis",
         "reason": "Shows another principal projection and assists thickness/feature location checks."},
        {"view": "Side view (provisional)", "orientation": f"Looking along {axes[0][0]} axis",
         "reason": "Shows the remaining principal projection."},
        {"view": "Isometric (optional)", "orientation": "Isometric",
         "reason": "Useful for visual identification; normally not a substitute for dimensioned orthographic views."},
    ]

    checklist = [
        "Verify overall X, Y and Z dimensions against the 3D model.",
        "Check plate thickness and show it in a suitable view.",
        "Locate every hole from unambiguous datums; avoid chained dimensions where possible.",
        "Use diameter callouts for holes and add counterbore/countersink details when present.",
        "Add centre marks/centre lines for circular features.",
        "Avoid duplicate dimensions and over-dimensioning.",
        "Confirm projection symbol, units, scale, material and tolerances.",
        "Check that all manufacturing-critical features are defined.",
    ]

    if dxf.get("dimensions"):
        checklist.append(
            f"Reference contains {len(dxf['dimensions'])} DIMENSION entities; inspect their style and arrangement before reusing conventions."
        )
    else:
        checklist.append("Reference has no native DIMENSION entities detected; inspect whether dimensions are exploded into lines and text.")

    return {
        "sheet": sheet,
        "projection": projection,
        "views": views,
        "dimension_checklist": checklist,
        "reference_dimension_count": len(dxf.get("dimensions", [])),
        "notes": [
            "View orientation is provisional and must be confirmed.",
            "Reference drawing dimensions must not be copied as values onto the new part.",
            "Dimension values must be derived from the STEP geometry in a later implementation stage."
        ],
    }
