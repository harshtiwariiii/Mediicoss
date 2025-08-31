from flask import Flask, render_template, jsonify, request
from src.helpers import Download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompts import system_prompt
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)


load_dotenv()

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


embeddings = Download_embeddings()

index_name = "medical-chatbot" 
# Embed each chunk and upsert the embeddings into your Pinecone index.
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)




retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})

# Initialize LLM with fallback options
def initialize_llm():
    """Initialize LLM with fallback options"""
    try:
        # Try Ollama first
        from langchain_community.llms import Ollama
        logger.info("Attempting to initialize Ollama LLM...")
        llm = Ollama(model="llama2", base_url="http://localhost:11434")
        # Test the connection
        test_response = llm.invoke("Hello")
        logger.info(f"Ollama LLM initialized successfully. Test response: {test_response[:50]}...")
        return llm, "ollama"
    except Exception as e:
        logger.warning(f"Ollama initialization failed: {e}")
        
        try:
            # Try HuggingFace as fallback
            from langchain_community.llms import HuggingFaceHub
            logger.info("Attempting to initialize HuggingFace LLM...")
            llm = HuggingFaceHub(
                repo_id="google/flan-t5-base",
                model_kwargs={"temperature": 0.5, "max_length": 512}
            )
            logger.info("HuggingFace LLM initialized successfully")
            return llm, "huggingface"
        except Exception as e2:
            logger.warning(f"HuggingFace initialization failed: {e2}")
            
            # Return None for fallback to simple responses
            logger.info("Falling back to simple response system")
            return None, "simple"

# Initialize LLM
llm, llm_type = initialize_llm()

# Initialize RAG chain if LLM is available
rag_chain = None
if llm is not None:
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        logger.info(f"RAG chain initialized successfully with {llm_type}")
    except Exception as e:
        logger.error(f"Failed to initialize RAG chain: {e}")
        rag_chain = None

# Enhanced response system that handles all types of messages automatically
def get_smart_response(user_message):
    """Smart response system that handles all types of messages automatically"""
    user_message_lower = user_message.lower().strip()
    
    # Greetings and casual conversation
    greetings = {
        'hi': "Hello! 👋 I'm Mediicoss, your medical information assistant. How can I help you today? Feel free to ask me about any medical topics, symptoms, or health questions!",
        'hello': "Hi there! 😊 Welcome to Mediicoss. I'm here to provide you with reliable medical information and answer your health-related questions. What would you like to know?",
        'hey': "Hey! 👋 Great to see you! I'm your medical information buddy. Ask me anything about health, medicine, or wellness - I'm here to help!",
        'good morning': "Good morning! ☀️ I hope you're having a healthy start to your day. How can I assist you with medical information today?",
        'good afternoon': "Good afternoon! 🌤️ Welcome to Mediicoss. I'm ready to help you with any medical questions or health information you need.",
        'good evening': "Good evening! 🌙 I'm here to help you with medical information even in the evening. What health topic would you like to explore?",
        'how are you': "I'm doing great, thank you for asking! 😊 I'm ready to help you with any medical information you need. What's on your mind regarding health or wellness?",
        'what can you do': "I'm Mediicoss, your medical information assistant! 🏥 I can help you with:\n\n• <strong>Medical conditions</strong> - diabetes, heart disease, cancer, etc.\n• <strong>Symptoms</strong> - understanding what they might mean\n• <strong>Prevention</strong> - tips for staying healthy\n• <strong>Medical procedures</strong> - what to expect\n• <strong>Wellness advice</strong> - nutrition, exercise, sleep\n\n<strong>Important:</strong> I provide educational information only. For personal medical advice, always consult healthcare professionals.\n\nWhat specific topic would you like to learn about?"
    }
    
    # Check for greetings first
    for greeting, response in greetings.items():
        if greeting in user_message_lower:
            return response
    
    # Medical topic responses
    medical_responses = {
        'diabetes': "Diabetes is a chronic health condition that affects how your body turns food into energy. There are two main types: Type 1 and Type 2. Common symptoms include increased thirst, frequent urination, and fatigue. <strong>Remember:</strong> This is general information only. Always consult a healthcare provider for personal medical advice.",
        
        'heart': "Heart disease refers to various conditions affecting the heart and blood vessels. Common types include coronary artery disease, heart failure, and arrhythmias. Risk factors include high blood pressure, high cholesterol, smoking, and diabetes. <strong>Important:</strong> If you experience chest pain, shortness of breath, or other concerning symptoms, seek immediate medical attention.",
        
        'flu': "Influenza (flu) is a contagious respiratory illness caused by influenza viruses. Symptoms typically include fever, cough, sore throat, muscle aches, and fatigue. The flu can be prevented with annual vaccination and good hygiene practices. <strong>Note:</strong> If you have severe symptoms or are at high risk for complications, contact your healthcare provider.",
        
        'immune': "The immune system is your body's defense mechanism against infections and diseases. It consists of white blood cells, antibodies, and other components that work together to protect you. A healthy lifestyle with proper nutrition, exercise, and sleep helps maintain a strong immune system. <strong>Disclaimer:</strong> This is educational information, not medical advice.",
        
        'cancer': "Cancer is a group of diseases characterized by uncontrolled cell growth. There are many types of cancer, each with different causes, symptoms, and treatments. Early detection through regular screenings is crucial. <strong>Important:</strong> If you notice unusual symptoms or changes in your body, consult a healthcare provider immediately.",
        
        'blood pressure': "💓 <strong>Blood Pressure</strong> is the force of blood pushing against artery walls.\n\n• <strong>Normal:</strong> Below 120/80 mmHg\n• <strong>Elevated:</strong> 120-129/<80 mmHg\n• <strong>High:</strong> 130/80 mmHg or higher\n\nHigh blood pressure can lead to heart disease, stroke, and kidney problems.\n\n<strong>Management:</strong> Healthy diet, regular exercise, stress management, and medication if prescribed.",
        
        'headache': "🤕 <strong>Headaches</strong> can have various causes:\n\n• Tension headaches (most common)\n• Migraines\n• Cluster headaches\n• Sinus headaches\n\nCommon triggers: stress, lack of sleep, dehydration, eye strain, certain foods.\n\n<strong>When to worry:</strong> Severe, sudden headaches or those with fever, confusion, or neck stiffness require immediate medical attention.",
        
        'fever': "🌡️ <strong>Fever</strong> is a temporary increase in body temperature, usually a sign of infection.\n\n• <strong>Low-grade:</strong> 100.4°F (38°C) to 101.3°F (38.5°C)\n• <strong>High:</strong> Above 103°F (39.4°C)\n\nTreatment: Rest, fluids, over-the-counter fever reducers.\n\n<strong>Seek medical help if:</strong> Fever above 103°F, lasts more than 3 days, or accompanied by severe symptoms.",
        
        'pain': "😣 <strong>Pain</strong> is your body's way of signaling that something is wrong.\n\nTypes:\n• Acute pain (sudden, short-term)\n• Chronic pain (long-lasting)\n• Nociceptive pain (tissue damage)\n• Neuropathic pain (nerve damage)\n\n<strong>Important:</strong> Don't ignore severe or persistent pain. Consult a healthcare provider for proper diagnosis and treatment.",
        
        'sleep': "😴 <strong>Sleep</strong> is essential for physical and mental health.\n\nAdults need 7-9 hours per night. Poor sleep can lead to:\n• Weakened immune system\n• Weight gain\n• Heart disease\n• Depression\n\nTips for better sleep: Stick to a schedule, create a relaxing bedtime routine, avoid screens before bed, keep your bedroom cool and dark.",
        
        'exercise': "💪 <strong>Exercise</strong> is crucial for overall health and well-being.\n\nBenefits:\n• Strengthens heart and muscles\n• Improves mood and energy\n• Helps maintain healthy weight\n• Reduces risk of chronic diseases\n\nRecommendation: 150 minutes of moderate exercise or 75 minutes of vigorous exercise per week, plus strength training twice weekly.",
        
        'nutrition': "🥗 <strong>Good Nutrition</strong> is the foundation of health.\n\nKey components:\n• Fruits and vegetables\n• Whole grains\n• Lean proteins\n• Healthy fats\n• Adequate hydration\n\nA balanced diet helps prevent chronic diseases, maintains healthy weight, and provides energy for daily activities.",
        
        'stress': "😰 <strong>Stress</strong> is your body's response to challenges and demands.\n\nChronic stress can lead to:\n• High blood pressure\n• Heart disease\n• Depression\n• Weakened immune system\n\nManagement techniques: Exercise, meditation, deep breathing, adequate sleep, time management, and seeking support when needed."
    }
    
    # Check for medical topics
    for topic, response in medical_responses.items():
        if topic in user_message_lower:
            return response
    
    # Enhanced response logic for various types of questions
    return "Thank you for your question about medical topics. I'm designed to provide general medical information and education. For specific medical concerns, diagnosis, or treatment recommendations, please consult with a qualified healthcare professional. Is there a particular medical topic you'd like to learn more about?"



@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/health")
def health():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "llm_type": llm_type if 'llm_type' in locals() else "unknown",
        "rag_chain": "available" if rag_chain is not None else "unavailable",
        "pinecone": "connected" if 'docsearch' in locals() else "disconnected"
    }
    return jsonify(status)

@app.route("/status")
def status():
    """Detailed status endpoint"""
    status = {
        "llm_type": llm_type if 'llm_type' in locals() else "unknown",
        "rag_chain_available": rag_chain is not None,
        "pinecone_connected": 'docsearch' in locals(),
        "embeddings_model": "sentence-transformers/all-MiniLM-L6-v2",
        "vector_index": "medical-chatbot"
    }
    return jsonify(status)



@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    logger.info(f"Received chat message: {msg}")
    
    try:
        if rag_chain is not None:
            # Use RAG chain for intelligent responses
            logger.info("Using RAG chain for response")
            response = rag_chain.invoke({"input": msg})
            answer = response.get("answer", "I'm sorry, I couldn't generate a response.")
            logger.info(f"RAG response generated successfully")
            return answer
        else:
            # Fallback to simple response system
            logger.info("Using simple response system")
            answer = get_smart_response(msg)
            return answer
            
    except Exception as e:
        logger.error(f"Error in chat function: {e}")
        # Fallback to simple response on error
        answer = get_smart_response(msg)
        return answer



if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 8080, debug= True)
