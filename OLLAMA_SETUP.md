# 🦙 Ollama Setup Guide for Windows

## **Quick Start (Recommended)**

### **1. Download Ollama**
- Go to: https://ollama.ai/
- Click "Download for Windows"
- Run the installer as Administrator

### **2. Install and Start Ollama**
```bash
# After installation, Ollama should start automatically
# If not, open Command Prompt as Administrator and run:
ollama serve
```

### **3. Pull the Llama2 Model**
```bash
# Open a new Command Prompt and run:
ollama pull llama2
```

### **4. Test Ollama**
```bash
# Test if Ollama is working:
ollama run llama2 "Hello, how are you?"
```

## **Alternative: Use WSL2 (Windows Subsystem for Linux)**

If you prefer using Linux commands:

### **1. Install WSL2**
```powershell
# Run in PowerShell as Administrator:
wsl --install
```

### **2. Install Ollama in WSL2**
```bash
# In WSL2 terminal:
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

### **3. Pull Model**
```bash
ollama pull llama2
```

## **Verify Installation**

### **Check Ollama Status**
```bash
# Should show running service
ollama list
```

### **Test API Endpoint**
```bash
# Test if Ollama API is responding
curl http://localhost:11434/api/tags
```

## **Troubleshooting**

### **Common Issues:**

1. **Port 11434 already in use**
   - Check if another service is using the port
   - Restart Ollama: `ollama serve`

2. **Permission denied**
   - Run Command Prompt as Administrator
   - Check Windows Defender settings

3. **Model download fails**
   - Check internet connection
   - Try: `ollama pull llama2:7b` (smaller model)

### **Alternative Models (if llama2 is too large):**
```bash
# Smaller, faster models:
ollama pull llama2:7b
ollama pull mistral:7b
ollama pull codellama:7b
```

## **Integration with Your Flask App**

Once Ollama is running:

1. **Start your Flask app:**
   ```bash
   python app.py
   ```

2. **Check the logs** - you should see:
   ```
   INFO: Attempting to initialize Ollama LLM...
   INFO: Ollama LLM initialized successfully
   INFO: RAG chain initialized successfully with ollama
   ```

3. **Test the health endpoint:**
   ```
   http://localhost:8080/health
   ```

## **Performance Tips**

- **Use smaller models** for faster responses
- **Keep Ollama running** in background
- **Monitor memory usage** - models can use 4-8GB RAM
- **Use SSD storage** for faster model loading

## **Next Steps**

After Ollama is working:
1. Test your chatbot with medical questions
2. Monitor response quality
3. Consider fine-tuning prompts for medical domain
4. Add more medical models if needed

## **Support**

- **Ollama Documentation:** https://ollama.ai/docs
- **GitHub Issues:** https://github.com/ollama/ollama/issues
- **Community Discord:** https://discord.gg/ollama 