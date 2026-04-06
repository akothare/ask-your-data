class ResponseFormatter:

    @staticmethod
    def format(user_query, data):

        if not data or len(data) == 0:
            return {
                "type": "text",
                "content": "No data found"
            }

        # 🔹 If multiple rows → create readable summary
        summary_lines = []

        # Try to detect customer-order structure
        if "CUSTOMER_NAME" in data[0]:

            customer_map = {}

            for row in data:
                name = row.get("CUSTOMER_NAME")

                if name not in customer_map:
                    customer_map[name] = []

                customer_map[name].append(row)

            # Build per-customer summary
            for name, orders in customer_map.items():

                total = sum(o.get("AMOUNT", 0) for o in orders)

                status_counts = {}
                for o in orders:
                    status = o.get("STATUS", "").lower()
                    status_counts[status] = status_counts.get(status, 0) + 1

                status_text = ", ".join([
                    f"{count} {status}"
                    for status, count in status_counts.items()
                ])

                line = f"{name} placed {len(orders)} order(s) totaling {round(total, 2)} ({status_text})"

                summary_lines.append(line)

        else:
            # Generic fallback
            summary_lines.append(f"Returned {len(data)} records.")

        summary = "Here’s what I found:\n\n" + "\n\n".join(summary_lines)

        return {
            "type": "mixed",
            "summary": summary,
            "data": data
        }
