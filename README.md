# CAD Drafting Assistant — MVP 0.1

A local Streamlit application that analyses:
- STEP geometry using CadQuery / OpenCascade
- Reference DXF entities, layers, dimension entities, text and dimension styles using ezdxf

It produces a preliminary drafting recommendation and a downloadable JSON analysis.

## Important limitations

This MVP does **not** yet generate a finished dimensioned drawing. It does not infer manufacturing intent, datum strategy, hidden-line visibility, or a reliable semantic front orientation. All recommendations require engineering review.

DWG is not directly supported. Save/export the reference drawing as DXF from the CAD application. LibreDWG may be evaluated later as an optional open-source DWG conversion route, subject to format/version compatibility.

## Windows setup

A Conda environment is recommended for CadQuery:

```bash
conda create -n cad-drafting python=3.11 -y
conda activate cad-drafting
conda install -c conda-forge cadquery ezdxf streamlit pandas -y
```

Alternatively, install the packages in `requirements.txt` in a compatible Python environment.

Run:

```bash
streamlit run app.py
```

## Test inputs

Use:
1. A STEP file of a simple plate.
2. A DXF of a similar approved plate drawing.

## Next development milestones

1. Validate geometry extraction against real sample files.
2. Parse reference drawing layout and dimensioning patterns more deeply.
3. Generate principal views using a CAD drawing engine.
4. Add geometry-derived dimensions and dimension placement.
5. Export editable DXF and PDF.
6. Add review/approval controls and regression tests.

## Privacy

Files are processed by the local application process. Do not expose the Streamlit server publicly without authentication and appropriate network controls.
