"""Adapt WoundCare+ research inference to the existing nurse assessment API."""

import cv2

from woundcare_inference import CascadeConfig, classify_image, infer_segmentation_cascade


REVIEW_MESSAGE = "研究模型結果僅供護理師核對；影像分類不能判定臨床 Grade、感染或處置，請依實際檢查記錄。"


def analyze_image(image, classifier, segmenter, config: CascadeConfig):
    try:
        result = infer_segmentation_cascade(image, segmenter, classifier, config)
    except Exception:
        label, confidence = classify_image(classifier, image, config)
        result = {"label": label, "class_confidence": confidence, "crop_box": None,
                  "fallback_used": True, "low_confidence": confidence is None or confidence < config.classifier_confidence}

    box = result.get("crop_box")
    confidence = result.get("class_confidence")
    reliable_roi = box is not None and not result.get("fallback_used")
    reliable_class = result.get("label") and not result.get("low_confidence")
    annotated = image.copy()
    if reliable_roi:
        cv2.rectangle(annotated, (box["x1"], box["y1"]), (box["x2"], box["y2"]), (24, 160, 147), 3)
    label = result.get("label") if reliable_roi and reliable_class else None
    advice = (f"研究分類提示：{label}。" if label else "無可靠定位或分類結果。") + REVIEW_MESSAGE
    return {
        "ai_grade": "待人工判讀",
        "ai_confidence": float(confidence) if label and confidence is not None else 0.0,
        "ai_advice": advice,
        "annotated": annotated,
        "requires_human_review": True,
        "research_class": label,
    }
