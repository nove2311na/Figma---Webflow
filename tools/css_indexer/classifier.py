class CSSClassifier:
    def __init__(self):
        pass

    @staticmethod
    def classify_class(class_name):
        """
        Classifies a CSS class name into Client-First categories.
        """
        if class_name.startswith("fs-styleguide_") or class_name.startswith("fs-styleguide"):
            return "styleguide-only"
        elif class_name.startswith("w-"):
            return "native"
        elif class_name.startswith("padding-") or class_name.startswith("margin-") or class_name.startswith("spacer-"):
            return "spacing"
        elif class_name.startswith("gap-"):
            return "gap"
        elif class_name.startswith("grid-"):
            return "grid"
        elif class_name.startswith("flex-"):
            return "flex"
        elif class_name.startswith("heading-style-") or class_name.startswith("text-size-") or class_name.startswith("text-weight-") or class_name.startswith("text-style-"):
            return "typography"
        elif class_name.startswith("text-color-") or class_name.startswith("background-color-") or class_name.startswith("border-color-"):
            return "color"
        elif any(comp in class_name for comp in ["button", "form", "nav", "card", "section", "header", "footer", "menu", "input", "dropdown"]):
            return "components"
        else:
            return "custom"
