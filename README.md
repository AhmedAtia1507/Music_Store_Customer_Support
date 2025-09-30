# Music Store Customer Support System

A sophisticated AI-powered customer support system for music stores, built with LangGraph, Streamlit, and multi-agent architecture. The system provides intelligent assistance for music catalog inquiries and customer invoice management.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-v0.4.5-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-v1.39.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎵 Features

### Multi-Agent Architecture
- **Music Catalog Agent**: Handles inquiries about artists, albums, tracks, and genres
- **Invoice Information Agent**: Manages customer invoice and billing queries  
- **Supervisor Agent**: Intelligently routes queries to appropriate specialized agents
- **Customer Verification**: Secure identity verification via phone/email
- **Preference Learning**: Remembers customer preferences and conversation history

### Core Capabilities
- 🎶 **Music Database**: Complete Chinook music database with 200+ artists and albums
- 📄 **Invoice Management**: Customer purchase history and billing information
- 🔐 **Customer Verification**: Secure authentication system
- 💭 **Memory System**: Persistent conversation context and preferences
- 🎯 **Personalized Recommendations**: AI-driven music suggestions
- 💬 **Interactive Chat**: Real-time conversational interface

### Technical Stack
- **Frontend**: Streamlit web application
- **Backend**: LangGraph multi-agent orchestration
- **LLM**: Groq API with multiple model options
- **Database**: SQLite with Chinook music database
- **Memory**: Vector-based preference storage
- **State Management**: LangGraph checkpointing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API Key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AhmedAtia1507/Music_Store_Customer_Support.git
   cd Music_Store_Customer_Support
   ```

2. **Create virtual environment**
   ```bash
   python -m venv FinalProject_venv
   
   # Windows
   FinalProject_venv\Scripts\activate
   
   # macOS/Linux
   source FinalProject_venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run streamlit_app.py
   ```

The application will open at `http://localhost:8501`

## 🏗️ Architecture

### System Overview
![alt text](image.png)

### Project Structure
```
Music_Store_Customer_Support/
├── 📄 README.md                    # Project documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 streamlit_app.py            # Main Streamlit application
├── 📄 LICENSE                     # MIT license
├── 📄 Customers.db               # Customer database
├── 📁 Graph/                     # LangGraph components
│   ├── CustomerQueryGraph.py     # Main graph orchestrator
│   ├── CustomerVerification.py   # Customer authentication
│   └── CustomerPreferences.py    # Preference management
├── 📁 Databases/                 # Database modules
│   ├── MusicDatabase.py          # Chinook music database
│   └── CustomerDatabase.py       # Customer data management
└── 📁 Utils/                     # Utility modules
    └── GraphInnerState.py        # State management
```

## 🎯 Usage Examples

### Music Catalog Queries
```
User: "Show me some albums by The Rolling Stones"
Assistant: Albums by The Rolling Stones in our catalog

Hot Rocks, 1964‑1971 (Disc 1)
No Security
Voodoo Lounge
Let me know if you’d like more details on any of these, or if you’d like to add one to your cart!
```

### Customer Verification
```
User: "My phone is +55 (12) 3923-5555. What was my most recent purchase?"
Assistant: Your most recent purchase was on 2023‑10‑10.
- Invoice ID: invoice_4
- Amount: $50.25
- Processed by: Alice
If you need more details about this transaction or have any other questions, just let me know!
...
```

### Mixed Queries
```
User: "Show me AC/DC albums and my purchase history"
Assistant: 
- AC/DC albums available:
-- For Those About To Rock We Salute You
-- Let There Be Rock
- Your purchase history:
-- invoice_4 – 10 Oct 2023 – $50.25 – issued by Alice
-- invoice_1 – 01 Oct 2023 – $150.75 – issued by Alice
Let me know if you’d like to order any of these albums or need more details about your 
```

## ⚙️ Configuration

### Available Models
- `openai/gpt-oss-120b`
- `openai/gpt-oss-20b`
- `moonshotai/kimi-k2-instruct-0905`
- `meta-llama/llama-4-maverick-17b-128e-instruct`

## 🗄️ Database Schema

### Customer Database
```sql
-- Customers table
CREATE TABLE customers (
    id TEXT PRIMARY KEY,
    phone_number TEXT UNIQUE,
    email TEXT UNIQUE
);

-- Invoices table  
CREATE TABLE invoices (
    id TEXT PRIMARY KEY,
    customer_id TEXT,
    amount REAL,
    date TEXT,
    employee_name TEXT
);
```

### Music Database
Uses the complete [Chinook Database](https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql) with:
- 275 Albums
- 3,503 Tracks  
- 204 Artists
- 25 Genres
- Full relational structure

## 🤖 Agent Capabilities

### Music Catalog Agent
- Artist information lookup
- Album and track searches
- Genre-based filtering
- Music recommendations
- Availability checking

### Invoice Information Agent  
- Purchase history retrieval
- Invoice details and amounts
- Employee information
- Date-based sorting
- Customer-specific queries

### Supervisor Agent
- Intelligent query routing
- Multi-topic request handling
- Agent coordination
- Response compilation
- Context management

## 🧪 Testing

### Sample Customer Data
For testing purposes, use these credentials:
```
Phone: +55 (12) 3923-5555
Email: customer1@example.com

Phone: +55 (21) 99876-5432  
Email: customer2@example.com

Phone: +55 (11) 91234-5678
Email: customer3@example.com
```

### Development Setup
```bash
git clone https://github.com/AhmedAtia1507/Music_Store_Customer_Support.git
cd Music_Store_Customer_Support
pip install -r requirements.txt
```


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangGraph Team** - Multi-agent framework
- **Streamlit** - Web application framework  
- **Chinook Database** - Sample music data
- **Groq** - Fast inference API
- **LangChain** - AI application framework

## 📧 Contact

**Ahmed Atia Said**
- Email: ahmed.atia.said15@gmail.com
- GitHub: [@AhmedAtia1507](https://github.com/AhmedAtia1507)
- LinkedIn: [Ahmed Atia Said](https://www.linkedin.com/in/ahmed-atia-said-b8aa38135/)


---