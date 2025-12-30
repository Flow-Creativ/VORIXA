from flask import Flask, render_template, request, jsonify
from datetime import datetime
from datetime import datetime
from scraper.api import search_maps

app = Flask(__name__)

# No local storage configuration needed

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    keyword = request.form.get('keyword')
    try:
        max_results = int(request.form.get('max_results', 10))
    except:
        max_results = 10

    if not keyword:
        return jsonify({"status": "danger", "message": "Keyword is required"})

    data = []
    
    try:
        data = search_maps(keyword, max_results=max_results)
            
        if not data:
            return jsonify({"message": "No results found. Try again or check your parameters.", "status": "warning", "results": []})

        # Return JSON direct to client. Client generates the Excel file.
        return jsonify({
            "message": f"Success! Found {len(data)} results.", 
            "status": "success",
            "results": data
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"message": f"Error: {str(e)}", "status": "danger"})

if __name__ == '__main__':
    import os
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
