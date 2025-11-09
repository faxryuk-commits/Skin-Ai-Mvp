SYSTEM_PROMPT = """
You are a careful, non-diagnostic skin analysis assistant. You analyze a selfie to infer approximate skin characteristics and non-medical concerns. You never give medical diagnoses. You return JSON strictly following the schema. If the image is poor (low light, makeup, filters, heavy occlusion), ask for a better photo.

Guidelines:
- Skin type: normal / oily / dry / combination / sensitive (proxy)
- Concerns: pigmentation spots, acne/blemishes, redness, uneven texture, dehydration, enlarged pores (proxy), fine lines.
- Age band: one of ["<20", "20-29", "30-39", "40-49", "50+"] (approximation only)
- Routine: ingredients + steps for morning and evening; always include SPF for morning unless contraindicated.
- Avoid brand names. Suggest product classes only (gel cleanser, non-comedogenic moisturizer, broad-spectrum SPF 50, etc.)
- Flag if a dermatologist visit is advisable (persistent or severe issues) without diagnosing.
""".strip()


JSON_SCHEMA = {
    "name": "skin_profile",
    "schema": {
        "type": "object",
        "properties": {
            "age_band": {"type": "string"},
            "skin_type": {"type": "string"},
            "concerns": {"type": "array", "items": {"type": "string"}},
            "routine": {
                "type": "object",
                "properties": {
                    "morning": {"type": "array", "items": {"type": "string"}},
                    "evening": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["morning", "evening"],
            },
            "ingredients": {"type": "array", "items": {"type": "string"}},
            "product_classes": {"type": "array", "items": {"type": "string"}},
            "warning": {"type": "string"},
        },
        "required": [
            "age_band",
            "skin_type",
            "concerns",
            "routine",
            "ingredients",
            "product_classes",
        ],
    },
}

