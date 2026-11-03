from pathlib import Path
import ezdxf


def analyze_dxf(path: Path) -> dict:
    doc = ezdxf.readfile(str(path))
    msp = doc.modelspace()

    counts = {}
    layer_counts = {}
    dimensions = []
    texts = []

    for entity in msp:
        typ = entity.dxftype()
        layer = entity.dxf.layer if entity.dxf.hasattr("layer") else "0"
        counts[typ] = counts.get(typ, 0) + 1
        layer_counts[layer] = layer_counts.get(layer, 0) + 1

        if typ == "DIMENSION":
            try:
                measurement = entity.get_measurement()
            except Exception:
                measurement = None
            dimensions.append({
                "dimension_type": entity.dxf.get("dimtype", "unknown"),
                "measurement": round(float(measurement), 4) if measurement is not None else None,
                "text_override": entity.dxf.get("text", ""),
                "layer": layer,
                "style": entity.dxf.get(" dimstyle", entity.dxf.get("dimstyle", "Standard")),
            })
        elif typ in ("TEXT", "MTEXT"):
            try:
                content = entity.dxf.text if typ == "TEXT" else entity.text
                if content.strip():
                    texts.append({"type": typ, "text": content[:250], "layer": layer})
            except Exception:
                pass

    layers = []
    for layer in doc.layers:
        layers.append({
            "name": layer.dxf.name,
            "color_index": layer.dxf.get("color", 7),
            "linetype": layer.dxf.get("linetype", "Continuous"),
        })

    layer_summary = [
        {"layer": name, "entity_count": count}
        for name, count in sorted(layer_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "file_name": Path(path).name,
        "entity_count": sum(counts.values()),
        "entity_types": counts,
        "layers": layers,
        "layer_summary": layer_summary,
        "dimensions": dimensions,
        "texts": texts[:200],
        "dimension_styles": [style.dxf.name for style in doc.dimstyles],
        "units_code": doc.header.get("$INSUNITS", 0),
    }
