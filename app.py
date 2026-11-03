import json
import tempfile
from pathlib import Path

import streamlit as st
import pandas as pd

from cad_assistant.step_analysis import analyze_step
from cad_assistant.dxf_analysis import analyze_dxf
from cad_assistant.drafting import build_drafting_recommendations

st.set_page_config(page_title="CAD Drafting Assistant", page_icon="📐", layout="wide")
st.title("CAD Drafting Assistant")
st.caption("STEP geometry analysis + reference DXF drafting analysis")

st.info(
    "MVP 0.1: this version analyses STEP geometry and DXF drafting conventions, "
    "then recommends views and dimensions. It does not yet create a production-ready "
    "dimensioned drawing. Generated dimensions must be checked by an engineer."
)

with st.sidebar:
    st.header("Drawing settings")
    sheet = st.selectbox("Sheet size", ["A3", "A4", "A2", "A1"], index=0)
    projection = st.radio("Projection method", ["First angle", "Third angle"], horizontal=False)
    units = st.selectbox("Expected model units", ["mm", "inch"], index=0)
    st.markdown("---")
    st.caption("DXF is supported directly. DWG is not read natively in this MVP.")

left, right = st.columns(2)
with left:
    st.subheader("1. New 3D part")
    step_file = st.file_uploader("Upload STEP file", type=["step", "stp"], key="step")
with right:
    st.subheader("2. Previous reference drawing")
    dxf_file = st.file_uploader("Upload reference DXF", type=["dxf"], key="dxf")

if step_file and dxf_file:
    with st.spinner("Analysing STEP geometry and reference DXF..."):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            step_path = tmp / step_file.name
            dxf_path = tmp / dxf_file.name
            step_path.write_bytes(step_file.getvalue())
            dxf_path.write_bytes(dxf_file.getvalue())

            try:
                step_result = analyze_step(step_path, expected_units=units)
            except Exception as exc:
                st.error(f"Could not analyse STEP file: {exc}")
                st.stop()

            try:
                dxf_result = analyze_dxf(dxf_path)
            except Exception as exc:
                st.error(f"Could not analyse DXF file: {exc}")
                st.stop()

    recommendations = build_drafting_recommendations(
        step_result, dxf_result, sheet=sheet, projection=projection
    )

    st.success("Analysis completed.")
    st.header("3. Part geometry")
    bb = step_result["bounding_box"]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Length", f'{bb["x"]:.2f} {units}')
    m2.metric("Width", f'{bb["y"]:.2f} {units}')
    m3.metric("Height", f'{bb["z"]:.2f} {units}')
    m4.metric("Solid count", step_result["solid_count"])

    st.write("**Detected geometry**")
    st.json({
        "faces_by_type": step_result["faces_by_type"],
        "cylindrical_faces": step_result["cylindrical_faces"][:30],
        "circular_edges": step_result["circular_edges"][:30],
    })

    st.header("4. Reference drawing analysis")
    dx1, dx2, dx3 = st.columns(3)
    dx1.metric("Entities", dxf_result["entity_count"])
    dx2.metric("Dimensions", len(dxf_result["dimensions"]))
    dx3.metric("Layers", len(dxf_result["layers"]))
    st.write("**Layer summary**")
    if dxf_result["layer_summary"]:
        st.dataframe(pd.DataFrame(dxf_result["layer_summary"]), use_container_width=True)
    st.write("**Extracted dimension annotations**")
    if dxf_result["dimensions"]:
        st.dataframe(pd.DataFrame(dxf_result["dimensions"]), use_container_width=True)
    else:
        st.warning("No DIMENSION entities were found. The reference may use exploded dimensions or plain text.")

    st.header("5. Drafting recommendations")
    st.write(f'**Suggested sheet:** {sheet}  |  **Projection:** {projection}')
    st.write("**Recommended views**")
    st.dataframe(pd.DataFrame(recommendations["views"]), use_container_width=True)
    st.write("**Dimensioning checklist**")
    for item in recommendations["dimension_checklist"]:
        st.write(f"- {item}")

    st.warning(
        "View selection is currently heuristic, based on the STEP bounding box and "
        "reference DXF entities. It does not yet identify semantic front orientation, "
        "hidden edges, datum strategy or manufacturing intent."
    )

    bundle = {
        "step_analysis": step_result,
        "reference_dxf_analysis": dxf_result,
        "drafting_recommendations": recommendations,
    }
    st.download_button(
        "Download analysis JSON",
        data=json.dumps(bundle, indent=2),
        file_name="cad_drafting_analysis.json",
        mime="application/json",
        use_container_width=True,
    )
else:
    st.markdown("Upload both files to begin. You can use a STEP model exported from SolidWorks and a reference DXF.")
    st.markdown("""
    **Recommended test files**
    - A simple plate with a few holes, exported as STEP.
    - A similar, approved plate drawing saved as DXF.
    """)
