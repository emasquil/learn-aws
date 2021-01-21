from typing import Dict, Union

import torch


def to_result_dict(logits: torch.Tensor) -> Dict[str, Union[str, float]]:
    """
    Takes the model's output and generates a dictionary with the result to be send as
    response form the API endpoint.

    Arguments:
        logits {torch.Tensor} -- The logits that came out of the model.

    Returns:
        Dict[str, Union[str, float]] -- Result dict following this format:
            {
                "label": "cat" | "dog,
                "confidence": ...
            }
    """
    ps = torch.exp(logits)
    topconf, topclass = ps.topk(1, dim=1)

    result_class = "dog" if topclass.item() == 1 else "cat"

    return {"label": result_class, "confidence": topconf.item()}
