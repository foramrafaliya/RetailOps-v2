from flask import Flask, request, jsonify
import uuid
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reviewservice")

# Simple in-memory storage — NO database needed
reviews_db = {
    "OLJCESPC7Z": [
        {"id": "r1", "user": "alice", "rating": 5, "comment": "Great sunglasses!", "created_at": "2025-01-01"},
        {"id": "r2", "user": "bob", "rating": 4, "comment": "Good quality", "created_at": "2025-01-02"}
    ],
    "66VCHSJNUP": [
        {"id": "r3", "user": "charlie", "rating": 3, "comment": "Decent tank top", "created_at": "2025-01-03"}
    ],
    "1YMWWN1N4O": [
        {"id": "r4", "user": "diana", "rating": 5, "comment": "Beautiful watch!", "created_at": "2025-01-04"},
        {"id": "r5", "user": "eve", "rating": 4, "comment": "Worth the price", "created_at": "2025-01-05"},
        {"id": "r6", "user": "frank", "rating": 5, "comment": "Perfect gift", "created_at": "2025-01-06"}
    ]
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "reviewservice"}), 200

@app.route("/", methods=["GET"])
def home():
    """Simple HTML page to view reviews in browser."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Review Service</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            h1 { color: #333; }
            .product { 
                background: white; 
                padding: 20px; 
                margin: 15px 0; 
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .product h2 { color: #2196F3; margin-top: 0; }
            .review { 
                background: #f9f9f9; 
                padding: 10px 15px; 
                margin: 8px 0; 
                border-left: 3px solid #2196F3;
                border-radius: 4px;
            }
            .stars { color: #FFD700; font-size: 18px; }
            .user { font-weight: bold; color: #555; }
            .avg { 
                font-size: 24px; 
                color: #4CAF50; 
                font-weight: bold; 
            }
            .header {
                background: #2196F3;
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .endpoints {
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
            }
            code {
                background: #e8e8e8;
                padding: 2px 6px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⭐ Review Service</h1>
            <p>Microservice for Product Reviews & Ratings</p>
        </div>
    """ 

    # Show all products with reviews
    for product_id, reviews in reviews_db.items():
        avg = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0
        stars = "⭐" * round(avg)
        
        html += f"""
        <div class="product">
            <h2>Product: {product_id}</h2>
            <p class="avg">Average Rating: {avg}/5 {stars}</p>
            <p>Total Reviews: {len(reviews)}</p>
        """
        
        for review in reviews:
            review_stars = "⭐" * review["rating"]
            html += f"""
            <div class="review">
                <span class="user">{review["user"]}</span>
                <span class="stars"> {review_stars}</span>
                <p>{review["comment"]}</p>
            </div>
            """
        
        html += "</div>"

    html += """
        <div class="endpoints">
            <h3>📡 API Endpoints:</h3>
            <ul>
                <li><code>GET /health</code> — Health check</li>
                <li><code>GET /reviews/{product_id}</code> — Get reviews</li>
                <li><code>GET /reviews/{product_id}/summary</code> — Get rating summary</li>
                <li><code>POST /reviews</code> — Add a review</li>
            </ul>
        </div>

        <div class="endpoints">
            <h3>🔗 Try these links:</h3>
            <ul>
                <li><a href="/health">/health</a></li>
                <li><a href="/reviews/OLJCESPC7Z">/reviews/OLJCESPC7Z</a></li>
                <li><a href="/reviews/1YMWWN1N4O">/reviews/1YMWWN1N4O</a></li>
                <li><a href="/reviews/OLJCESPC7Z/summary">/reviews/OLJCESPC7Z/summary</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html


@app.route("/ready", methods=["GET"])
def ready():
    return jsonify({"status": "ready"}), 200


@app.route("/reviews/<product_id>", methods=["GET"])
def get_reviews(product_id):
    """Get all reviews for a product."""
    product_reviews = reviews_db.get(product_id, [])
    avg_rating = 0
    if product_reviews:
        avg_rating = round(sum(r["rating"] for r in product_reviews) / len(product_reviews), 1)

    return jsonify({
        "product_id": product_id,
        "total_reviews": len(product_reviews),
        "average_rating": avg_rating,
        "reviews": product_reviews
    }), 200


@app.route("/reviews", methods=["POST"])
def add_review():
    """Add a review."""
    data = request.get_json()

    for field in ["product_id", "user", "rating", "comment"]:
        if field not in data:
            return jsonify({"error": f"Missing: {field}"}), 400

    if not (1 <= data["rating"] <= 5):
        return jsonify({"error": "Rating must be 1-5"}), 400

    review = {
        "id": str(uuid.uuid4())[:8],
        "user": data["user"],
        "rating": data["rating"],
        "comment": data["comment"],
        "created_at": datetime.utcnow().isoformat()
    }

    reviews_db.setdefault(data["product_id"], []).append(review)
    logger.info(f"Review added for {data['product_id']} by {data['user']}")

    return jsonify({"message": "Review added", "review": review}), 201


@app.route("/reviews/<product_id>/summary", methods=["GET"])
def review_summary(product_id):
    """Get rating summary — Order Service calls this."""
    product_reviews = reviews_db.get(product_id, [])
    avg = 0
    if product_reviews:
        avg = round(sum(r["rating"] for r in product_reviews) / len(product_reviews), 1)

    return jsonify({
        "product_id": product_id,
        "average_rating": avg,
        "total_reviews": len(product_reviews)
    }), 200


if __name__ == "__main__":
    logger.info("Review Service starting on port 8085")
    app.run(host="0.0.0.0", port=8085)