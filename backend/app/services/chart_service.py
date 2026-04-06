class ChartService:

    @staticmethod
    def analyze(data):

        if not data or len(data) == 0:
            return None

        sample = data[0]

        columns = list(sample.keys())

        numeric_cols = []
        date_cols = []
        text_cols = []

        for col, val in sample.items():
            if isinstance(val, (int, float)):
                numeric_cols.append(col)
            elif "DATE" in col.upper() or "TIME" in col.upper():
                date_cols.append(col)
            else:
                text_cols.append(col)

        # 🎯 Heuristic
        if date_cols and numeric_cols:
            return {
                "type": "line",
                "x": date_cols[0],
                "y": numeric_cols[0]
            }

        if text_cols and numeric_cols:
            return {
                "type": "bar",
                "x": text_cols[0],
                "y": numeric_cols[0]
            }

        return None
