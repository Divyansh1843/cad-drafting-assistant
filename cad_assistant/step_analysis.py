from pathlib import Path
import cadquery as cq


def analyze_step(path: Path, expected_units: str = "mm") -> dict:
    """Read STEP with CadQuery/OCP and return basic, non-semantic geometry data."""
    wp = cq.importers.importStep(str(path))
    shape = wp.val()
    if shape is None or shape.isNull():
        raise ValueError("The STEP file did not contain a readable solid or compound.")

    bb = shape.BoundingBox()
    scale = 25.4 if expected_units == "inch" else 1.0

    faces_by_type = {}
    cylindrical_faces = []
    circular_edges = []

    for face in shape.Faces():
        typ = face.geomType()
        faces_by_type[typ] = faces_by_type.get(typ, 0) + 1
        if typ == "CYLINDER":
            try:
                cyl = face._geomAdaptor().Cylinder()
                cylindrical_faces.append({
                    "radius_model_units": round(float(cyl.Radius()) / scale, 5),
                    "diameter_model_units": round(2 * float(cyl.Radius()) / scale, 5),
                    "area_model_units2": round(float(face.Area()) / (scale * scale), 5),
                })
            except Exception:
                cylindrical_faces.append({"note": "Cylindrical face detected; parameters unavailable"})

    for edge in shape.Edges():
        try:
            if edge.geomType() == "CIRCLE":
                circle = edge._geomAdaptor().Circle()
                circular_edges.append({
                    "radius_model_units": round(float(circle.Radius()) / scale, 5),
                    "diameter_model_units": round(2 * float(circle.Radius()) / scale, 5),
                })
        except Exception:
            pass

    return {
        "file_name": Path(path).name,
        "expected_units": expected_units,
        "solid_count": len(shape.Solids()),
        "face_count": len(shape.Faces()),
        "edge_count": len(shape.Edges()),
        "bounding_box": {
            "x": round(float(bb.xlen) / scale, 4),
            "y": round(float(bb.ylen) / scale, 4),
            "z": round(float(bb.zlen) / scale, 4),
        },
        "faces_by_type": faces_by_type,
        "cylindrical_faces": cylindrical_faces,
        "circular_edges": circular_edges,
        "volume_model_units3": round(float(shape.Volume()) / (scale ** 3), 4),
    }
