from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import re

# Initialize embeddings based on available keys
if os.getenv("GEMINI_API_KEY") and not os.getenv("GEMINI_API_KEY").startswith("AQ."):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GEMINI_API_KEY"))
elif os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-your-openai-key-here":
    embeddings = OpenAIEmbeddings()
else:
    # Fallback to a mock embedding if no external API keys are present
    class MockEmbeddings:
        def embed_documents(self, texts):
            return [[0.0] * 768 for _ in texts]
        def embed_query(self, text):
            return [0.0] * 768
    embeddings = MockEmbeddings()

# Restaurant Knowledge Base extracted directly from the uploaded PDF dataset
knowledge_base = [
    # 1. Ocean View Diner
    Document(
        page_content=(
            "Ocean View Diner. Cuisine: Coastal Indian and seafood. Address: 18 Marina Crescent, Chennai (fictional). "
            "Opening hours: Daily, 11:00 AM - 10:30 PM. "
            "Policies: Price level medium; dress code: smart casual, beachwear is discouraged. "
            "Reservations recommended for parties of 6+; cancel at least 2 hours ahead (24 hours for groups of 8+). "
            "Dietary: Vegetarian and pescatarian options available; ask staff about allergens."
        ),
        metadata={"restaurant": "Ocean View Diner", "topic": "Overview and Policies"}
    ),
    Document(
        page_content=(
            "Ocean View Diner Menu and Dietary Notes: "
            "• Coastal fish curry (320): fish in coconut curry. "
            "• Paneer pepper fry (240): vegetarian, contains dairy. "
            "• Lemon rice (150): vegetarian. "
            "• Grilled prawns (390): contains shellfish. "
            "• Tender coconut pudding (170): contains coconut and dairy."
        ),
        metadata={"restaurant": "Ocean View Diner", "topic": "Menu and Dietary"}
    ),
    Document(
        page_content=(
            "Ocean View Diner FAQs: "
            "• Dress code: Smart casual; beachwear is discouraged. "
            "• Vegetarian food: Yes, including paneer pepper fry and lemon rice. "
            "• Cancellation policy: Cancel at least 2 hours ahead, or 24 hours ahead for groups of 8+."
        ),
        metadata={"restaurant": "Ocean View Diner", "topic": "FAQs"}
    ),

    # 2. Cedar & Spice
    Document(
        page_content=(
            "Cedar & Spice. Cuisine: North Indian and Mughlai. Address: 42 Garden Avenue, Chennai (fictional). "
            "Opening hours: Tuesday to Sunday, 12:00-3:30 PM and 6:30-11:00 PM; closed on Mondays. "
            "Policies: Price level high; dress code: casual or smart casual. Bookings accepted for 1-10 guests; cancel 3 hours ahead. "
            "Dietary: Vegan or gluten-free preparation is not guaranteed due to shared kitchen."
        ),
        metadata={"restaurant": "Cedar & Spice", "topic": "Overview and Policies"}
    ),
    Document(
        page_content=(
            "Cedar & Spice Menu and Dietary Notes: "
            "• Paneer tikka (280): vegetarian, contains dairy. "
            "• Chicken biryani (360). "
            "• Dal makhani (260): vegetarian, contains dairy. "
            "• Tandoori roti (45): contains gluten. "
            "• Kesar kulfi (120): contains dairy, may contain nuts."
        ),
        metadata={"restaurant": "Cedar & Spice", "topic": "Menu and Dietary"}
    ),
    Document(
        page_content=(
            "Cedar & Spice FAQs: "
            "• Open Monday? No, closed on Mondays. Open Tuesday through Sunday. "
            "• Vegetarian dishes: Yes, paneer tikka and dal makhani. "
            "• Gluten-free guarantee? No, shared kitchen means cross-contact cannot be ruled out. "
            "• Cancellation: Cancel at least 3 hours ahead."
        ),
        metadata={"restaurant": "Cedar & Spice", "topic": "FAQs"}
    ),

    # 3. Green Fork Kitchen
    Document(
        page_content=(
            "Green Fork Kitchen. Cuisine: Vegetarian and plant-forward. Address: 7 Lakeview Road, Chennai (fictional). "
            "Opening hours: Monday to Saturday, 9:00 AM - 9:00 PM; Sunday, 9:00 AM - 5:00 PM (closes 5:00 PM on Sundays). "
            "Policies: Price level medium; dress code: casual; walk-ins welcome; reservations recommended for 5+ guests; cancel 1 hour ahead. "
            "Dietary: Vegan-labelled dishes available; shared preparation areas are used."
        ),
        metadata={"restaurant": "Green Fork Kitchen", "topic": "Overview and Policies"}
    ),
    Document(
        page_content=(
            "Green Fork Kitchen Menu and Dietary Notes: "
            "• Millet Buddha bowl (260): vegan. "
            "• Mushroom masala wrap (220): contains gluten. "
            "• Avocado toast (240): contains gluten. "
            "• Coconut chia pudding (180): vegan. "
            "• Filter coffee (70): milk available separately."
        ),
        metadata={"restaurant": "Green Fork Kitchen", "topic": "Menu and Dietary"}
    ),
    Document(
        page_content=(
            "Green Fork Kitchen FAQs: "
            "• Vegan food: Yes, including millet Buddha bowl and coconut chia pudding. "
            "• Walk-ins: Yes, walk-ins are welcome subject to availability. "
            "• Sunday closing time: 5:00 PM on Sundays. "
            "• Cancellation: Cancel 1 hour ahead."
        ),
        metadata={"restaurant": "Green Fork Kitchen", "topic": "FAQs"}
    ),

    # 4. Little Lantern Café
    Document(
        page_content=(
            "Little Lantern Café. Cuisine: Café food, sandwiches, and desserts. Address: 11 Banyan Street, Chennai (fictional). "
            "Opening hours: Daily, 8:00 AM - 9:00 PM. "
            "Policies: Price level low; dress code: casual; normally no reservations for parties of 1-4 (walk-ins only); larger groups can request a table; group bookings should cancel 1 hour ahead. "
            "Dietary: Dairy-free drinks may be available on request."
        ),
        metadata={"restaurant": "Little Lantern Café", "topic": "Overview and Policies"}
    ),
    Document(
        page_content=(
            "Little Lantern Café Menu and Dietary Notes: "
            "• Grilled vegetable sandwich (160): contains gluten and dairy. "
            "• Peanut butter toast (130): contains peanuts and gluten. "
            "• Cold coffee (150): contains dairy unless substituted. "
            "• Banana oat muffin (110): may contain gluten. "
            "• Iced lemon tea (100): typically dairy-free."
        ),
        metadata={"restaurant": "Little Lantern Café", "topic": "Menu and Dietary"}
    ),
    Document(
        page_content=(
            "Little Lantern Café FAQs: "
            "• Opening time: 8:00 AM daily. "
            "• Table for two: Walk-ins only, no normal reservations for 1-4 people. "
            "• Dairy-free drinks: Ask staff about available substitutes."
        ),
        metadata={"restaurant": "Little Lantern Café", "topic": "FAQs"}
    ),

    # 5. Sakura Bento House
    Document(
        page_content=(
            "Sakura Bento House. Cuisine: Japanese-inspired bowls and sushi. Address: 29 Orchid Lane, Chennai (fictional). "
            "Opening hours: Wednesday to Monday, 12:00 PM - 10:00 PM; closed on Tuesday. "
            "Policies: Price level high; dress code: smart casual; reservations accepted for 1-6 guests; cancel 4 hours ahead. "
            "Dietary: Soy, sesame, fish, shellfish, and gluten may be present."
        ),
        metadata={"restaurant": "Sakura Bento House", "topic": "Overview and Policies"}
    ),
    Document(
        page_content=(
            "Sakura Bento House Menu and Dietary Notes: "
            "• Teriyaki chicken bowl (340): sauce may contain soy and gluten. "
            "• Vegetable maki roll (260). "
            "• Miso soup (140): commonly contains soy. "
            "• Sesame tofu bowl (290): contains soy and sesame. "
            "• Matcha cheesecake (210): contains dairy and gluten."
        ),
        metadata={"restaurant": "Sakura Bento House", "topic": "Menu and Dietary"}
    ),
    Document(
        page_content=(
            "Sakura Bento House FAQs: "
            "• Open Tuesday? No, closed on Tuesdays. "
            "• Vegetarian options: Vegetable maki roll and sesame tofu bowl. "
            "• Allergen-free guarantee: No, ask staff due to shared kitchen. "
            "• Cancellation: Cancel 4 hours ahead."
        ),
        metadata={"restaurant": "Sakura Bento House", "topic": "FAQs"}
    ),

    # 6. Brick Oven Social
    Document(
        page_content=(
            "Brick Oven Social. Cuisine: Pizza, pasta, and Italian-inspired food. Address: 5 Station Square, Chennai (fictional). "
            "Opening hours: Daily, 12:00 PM - 11:00 PM. "
            "Policies: Price level medium; dress code: casual; reservations accepted for 1-12 guests; cancel 2 hours ahead. "
            "Dietary: Gluten-free bases depend on availability and cross-contact may occur."
        ),
        metadata={"restaurant": "Brick Oven Social", "topic": "Overview and Policies"}
    ),
    Document(
        page_content=(
            "Brick Oven Social Menu and Dietary Notes: "
            "• Margherita pizza (290): contains dairy and gluten. "
            "• Roasted vegetable pizza (340): vegetarian, contains dairy and gluten. "
            "• Penne arrabbiata (270): contains gluten. "
            "• Garlic bread (140): contains gluten and dairy. "
            "• Tiramisu cup (190): contains dairy and may contain egg."
        ),
        metadata={"restaurant": "Brick Oven Social", "topic": "Menu and Dietary"}
    ),
    Document(
        page_content=(
            "Brick Oven Social FAQs: "
            "• Table for ten: Yes, reservations available up to 12 guests subject to availability. "
            "• Vegetarian pizza: Margherita pizza and roasted vegetable pizza. "
            "• Gluten-free base always available? No, depends on availability. "
            "• Cancellation: Cancel 2 hours ahead."
        ),
        metadata={"restaurant": "Brick Oven Social", "topic": "FAQs"}
    ),

    # 7. Pepper Tree Breakfast Club
    Document(
        page_content=(
            "Pepper Tree Breakfast Club. Cuisine: Breakfast, South Indian, and brunch. Address: 63 Sunrise Road, Chennai (fictional). "
            "Opening hours: Daily, 7:00 AM - 2:00 PM (closes 2:00 PM daily). "
            "Policies: Price level low; dress code: casual; walk-ins welcome; reservations accepted for 6+ guests; cancel group bookings 1 hour ahead. "
            "Dietary: Ask staff about dairy, gluten, peanuts, and other allergens."
        ),
        metadata={"restaurant": "Pepper Tree Breakfast Club", "topic": "Overview and Policies"}
    ),
    Document(
        page_content=(
            "Pepper Tree Breakfast Club Menu and Dietary Notes: "
            "• Idli with sambar (90): usually vegetarian. "
            "• Masala dosa (130): may contain dairy. "
            "• Pongal (110): commonly made with ghee. "
            "• Puri bhaji (140): contains gluten. "
            "• Fresh fruit bowl (160): seasonal availability."
        ),
        metadata={"restaurant": "Pepper Tree Breakfast Club", "topic": "Menu and Dietary"}
    ),
    Document(
        page_content=(
            "Pepper Tree Breakfast Club FAQs: "
            "• Closing time: 2:00 PM daily. Opens at 7:00 AM. "
            "• Table for eight: Yes, reservations accepted for 6+ guests subject to availability. "
            "• South Indian breakfast: Idli, dosa, and pongal are all available. "
            "• Cancellation: Cancel group bookings 1 hour ahead."
        ),
        metadata={"restaurant": "Pepper Tree Breakfast Club", "topic": "FAQs"}
    ),

    # 8. The Copper Kettle
    Document(
        page_content=(
            "The Copper Kettle. Cuisine: Continental and comfort food. Address: 14 Hilltop Boulevard, Chennai (fictional). "
            "Opening hours: Monday to Saturday, 11:30 AM - 10:00 PM; Sunday, 12:00 PM - 9:00 PM. "
            "Policies: Price level high; dress code: smart casual recommended for dinner, casual at lunch; reservations accepted for 1-8 guests; cancel 3 hours ahead. "
            "Dietary: Vegan substitutions may be possible but are not guaranteed."
        ),
        metadata={"restaurant": "The Copper Kettle", "topic": "Overview and Policies"}
    ),
    Document(
        page_content=(
            "The Copper Kettle Menu and Dietary Notes: "
            "• Creamy mushroom soup (190): contains dairy. "
            "• Herb grilled chicken (390). "
            "• Baked mac and cheese (310): contains dairy and gluten. "
            "• Roasted vegetable platter (280): vegetarian. "
            "• Apple crumble (180): contains gluten and may contain dairy."
        ),
        metadata={"restaurant": "The Copper Kettle", "topic": "Menu and Dietary"}
    ),
    Document(
        page_content=(
            "The Copper Kettle FAQs: "
            "• Dress code: Smart casual recommended for dinner; casual at lunch. "
            "• Vegetarian food: Roasted vegetable platter. "
            "• Booking for nine? Standard limit is eight; please contact the restaurant directly for larger parties. "
            "• Cancellation: Cancel 3 hours ahead."
        ),
        metadata={"restaurant": "The Copper Kettle", "topic": "FAQs"}
    )
]

# Create the vector store
vector_store = InMemoryVectorStore.from_documents(knowledge_base, embeddings)

def search_knowledge_base(query: str, k: int = 3) -> list[Document]:
    """
    Searches the knowledge base using vector similarity or keyword relevance with metadata filtering.
    """
    query_lower = query.lower()

    # Detect which restaurant is being queried
    target_restaurant = None
    for doc in knowledge_base:
        rest = doc.metadata.get("restaurant")
        if rest and rest.lower() in query_lower:
            target_restaurant = rest
            break

    # If partial restaurant words used
    if not target_restaurant:
        if "ocean" in query_lower or "diner" in query_lower:
            target_restaurant = "Ocean View Diner"
        elif "cedar" in query_lower or "spice" in query_lower:
            target_restaurant = "Cedar & Spice"
        elif "green" in query_lower or "fork" in query_lower:
            target_restaurant = "Green Fork Kitchen"
        elif "lantern" in query_lower or "cafe" in query_lower:
            target_restaurant = "Little Lantern Café"
        elif "sakura" in query_lower or "bento" in query_lower or "sushi" in query_lower:
            target_restaurant = "Sakura Bento House"
        elif "brick" in query_lower or "oven" in query_lower or "pizza" in query_lower:
            target_restaurant = "Brick Oven Social"
        elif "pepper" in query_lower or "breakfast" in query_lower or "dosa" in query_lower or "idli" in query_lower:
            target_restaurant = "Pepper Tree Breakfast Club"
        elif "copper" in query_lower or "kettle" in query_lower:
            target_restaurant = "The Copper Kettle"

    # Try vector similarity if active embeddings
    if not isinstance(embeddings, MockEmbeddings):
        try:
            results = vector_store.similarity_search(query, k=k)
            if results:
                if target_restaurant:
                    filtered = [d for d in results if d.metadata.get("restaurant") == target_restaurant]
                    if filtered:
                        return filtered
                return results
        except Exception:
            pass

    # Keyword relevance scoring with metadata boosting
    scored_docs = []
    keywords = [re.sub(r'[^\w]', '', w) for w in query_lower.split() if len(w) > 2]

    for doc in knowledge_base:
        score = 0
        doc_lower = doc.page_content.lower()
        doc_rest = doc.metadata.get("restaurant", "")

        # High priority to restaurant metadata match
        if target_restaurant and doc_rest == target_restaurant:
            score += 25
        elif target_restaurant and doc_rest != target_restaurant:
            score -= 15  # Penalize non-matching restaurants

        for kw in keywords:
            if kw in doc_lower:
                score += 3
            if kw in doc.metadata.get("topic", "").lower():
                score += 4

        if score > 0:
            scored_docs.append((score, doc))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    if scored_docs:
        return [doc for _, doc in scored_docs[:k]]

    return knowledge_base[:1]
