from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import re
import logging
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session support

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load Excel data
try:
    excel_path = os.path.join(os.path.dirname(__file__), "MandatesData.xlsx")
    df = pd.read_excel(excel_path)
    df["Mandate ID"] = df["Mandate ID"].astype(int)
    logging.info(f"✅ Excel loaded: {len(df)} records")
    logging.info(f"Columns: {df.columns.tolist()}")
    logging.info(f"Sample data:\n{df.head()}")
except Exception as e:
    logging.error(f"❌ Error loading Excel file: {e}")
    df = pd.DataFrame()


def get_mandate_info(text):
    try:
        match = re.search(r'\b\d{2}[\s-]?\d{3}\b', text)
        if match:
            mandate_id = int(re.sub(r'\D', '', match.group()))
            session['last_mandate_id'] = mandate_id
        else:
            mandate_id = session.get('last_mandate_id')
            if not mandate_id:
                return "⚠️ Please provide a valid Mandate ID (e.g., 'Who is the analyst for mandate 82669?')."

        result = df[df["Mandate ID"] == mandate_id]
        if result.empty:
            return f"❌ No data found for Mandate ID {mandate_id}."

        record = result.iloc[0]
        text_lower = text.lower()

        if "analyst" in text_lower:
            return f"<p><strong>Mandate ID:</strong> {mandate_id}</p><p><strong>Analyst:</strong> {record.get('Analyst', 'N/A')}</p>"
        if "chairperson" in text_lower or "cp" in text_lower:
            return f"<p><strong>Mandate ID:</strong> {mandate_id}</p><p><strong>Chairperson:</strong> {record.get('Chairperson', 'N/A')}</p>"
        if "rating type" in text_lower:
            return f"<p><strong>Mandate ID:</strong> {mandate_id}</p><p><strong>Rating Type:</strong> {record.get('Rating Type', 'N/A')}</p>"
        if "rating action" in text_lower:
            return f"<p><strong>Mandate ID:</strong> {mandate_id}</p><p><strong>Rating Action:</strong> {record.get('RatingAction', 'N/A')}</p>"
        if "rating" in text_lower and "rating type" not in text_lower and "rating action" not in text_lower:
            return f"<p><strong>Mandate ID:</strong> {mandate_id}</p><p><strong>Rating:</strong> {record.get('Rating', 'N/A')}</p>"
        if "status" in text_lower:
            return f"<p><strong>Mandate ID:</strong> {mandate_id}</p><p><strong>Status:</strong> {record.get('Mandate Status', 'N/A')}</p>"
        if "published" in text_lower:
            published_date = record.get('Published Date')
            published_date_str = published_date.strftime('%Y-%m-%d') if pd.notnull(published_date) else "N/A"
            return f"<p><strong>Mandate ID:</strong> {mandate_id}</p><p><strong>Published Date:</strong> {published_date_str}</p>"
        if "issue size" in text_lower:
            return f"<p><strong>Mandate ID:</strong> {mandate_id}</p><p><strong>Issue Size:</strong> {record.get('Issue Size', 'N/A')} Cr</p>"

        # Default - return full details
        published_date = record.get('Published Date')
        published_date_str = published_date.strftime('%Y-%m-%d') if pd.notnull(published_date) else "N/A"
        return f"""
        <p><strong>Mandate ID:</strong> {mandate_id}</p>
        <p><strong>Analyst:</strong> {record.get('Analyst', 'N/A')}</p>
        <p><strong>Chairperson:</strong> {record.get('Chairperson', 'N/A')}</p>
        <p><strong>Rating Type:</strong> {record.get('Rating Type', 'N/A')}</p>
        <p><strong>Rating:</strong> {record.get('Rating', 'N/A')}</p>
        <p><strong>Status:</strong> {record.get('Mandate Status', 'N/A')}</p>
        <p><strong>Rating Action:</strong> {record.get('RatingAction', 'N/A')}</p>
        <p><strong>Published Date:</strong> {published_date_str}</p>
        <p><strong>Issue Size:</strong> {record.get('Issue Size', 'N/A')} Cr</p>
        """

    except Exception as e:
        logging.error(f"⚠️ Error in get_mandate_info: {e}")
        return "⚠️ Something went wrong. Please try again."


@app.route("/")
def index():
    try:
        return render_template("index.html")
    except Exception as e:
        logging.error(f"Template load error: {e}")
        return "❌ Template not found. Make sure 'index.html' is in the 'templates' folder."


@app.route("/ask", methods=["POST"])
def ask():
    user_text = request.json.get("message", "")
    reply = get_mandate_info(user_text)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    # For Render or other PaaS, bind to 0.0.0.0 and use PORT env var
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
