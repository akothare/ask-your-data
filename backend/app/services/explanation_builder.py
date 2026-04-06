class ExplanationBuilder:

    @staticmethod
    def build(summary, steps):

        response = []

        if summary:
            response.append("Here’s what I found:")
            response.append(summary)

        if steps:
            response.append("\nHow I got this:")

            for step in steps:
                response.append(f"• {step}")

        return "\n".join(response)
