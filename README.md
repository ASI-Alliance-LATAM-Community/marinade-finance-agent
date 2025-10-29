<div align="center">

<img src="./logo.png" alt="Marinade Finance Agent" width="140">

<p></p>

<h1>Marinade Finance Agent</h1>
</div>

An intelligent AI agent specialized in providing comprehensive information and assistance for Marinade Finance, the premier liquid staking protocol on Solana. This agent leverages advanced Model Context Protocol (MCP) integration to deliver real-time data, documentation insights, and expert guidance on liquid staking with mSOL.

The agent is designed to bridge the gap between complex DeFi protocols and user accessibility, making Marinade Finance's liquid staking features more approachable through conversational AI interactions. Whether you're a beginner exploring liquid staking or an advanced user seeking technical integration details, this agent provides tailored assistance with real-time protocol data.

## Purpose

This agent is designed to:
- Provide real-time access to Marinade Finance protocol state and data
- Simplify complex liquid staking concepts for users of all experience levels
- Offer comprehensive documentation search and guidance
- Bridge technical barriers between users and DeFi protocols
- Deliver accurate, up-to-date information about mSOL and staking rewards
- Facilitate seamless integration support for developers and partners

The agent combines the power of ASI1 AI models with specialized Marinade Finance MCP tools to deliver contextual, accurate, and helpful responses about liquid staking on Solana.

## Getting Started

### 1) Clone the repository

```bash
git clone https://github.com/ASI-Alliance-LATAM-Community/marinade-finance-agent.git
cd marinade-finance-agent
```

### 2) Set up the agent environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` file in the root directory and add your API keys:

```env
ASI1_API_KEY=your_asi1_api_key_here          # https://asi1.ai/chat
SMITHERY_API_KEY=your_smithery_api_key_here  # https://smithery.ai/
SMITHERY_PROFILE=your_smithery_profile_here  # https://smithery.ai/
```

### 4) Run the agent

```bash
cd src/
python3 agent.py
```

## Features

- **Real-time Protocol Data**: Access current Marinade Finance state, including staking rates, mSOL prices, and rewards
- **Documentation Search**: Comprehensive search through Marinade Finance documentation and guides
- **MCP Integration**: Advanced Model Context Protocol integration for seamless data access
- **Intelligent Query Processing**: Smart tool selection based on query context and intent
- **Multi-modal Responses**: Support for various content types and structured data presentation

## Project Structure

```
├── src/
│   └── agent.py                    # Main agent implementation with MCP client
├── requirements.txt               # Python dependencies
├── .env.example                  # Environment variables template
├── LICENSE.md                    # License information
└── README.md                     # This file
```

## Usage Examples

### Protocol State Queries

Get real-time information about Marinade Finance protocol:

```
"What is the current mSOL price?"
"Show me the current staking rewards rate"
"What's the total value locked in Marinade?"
"How much SOL is currently staked in the protocol?"
```

### Documentation and Learning

Search for guides and documentation:

```
"How to stake SOL with Marinade Finance?"
"Explain liquid staking and mSOL tokens"
"Show me the API documentation for developers"
"How to integrate Marinade SDK in my application?"
```

### Technical Integration Support

Get help with development and integration:

```
"What are the available SDK methods?"
"How to unstake mSOL programmatically?"
"Show me code examples for staking integration"
"What are the current fees for staking and unstaking?"
```

## Core Technologies

| Component | Purpose |
|-----------|---------|
| **ASI1 AI Model** | Natural language processing and intelligent responses |
| **Marinande Finance MCP Server (Model Context Protocol)** | Real-time protocol data and documentation access |
| **Smithery Integration** | Hosted MCP server for Marinade Finance data |
| **uAgents Framework** | Agent communication and chat protocol handling |

## Requirements

- Python 3.8+
- Virtual environment (recommended)
- ASI1 API key
- Smithery API key and profile
- Internet connection for real-time data access

## Dependencies

- `uagents` - Agent framework for communication protocols
- `uagents-core` - Core agent functionality and chat protocols
- `mcp` - Model Context Protocol client implementation
- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management

## API Integration

The agent integrates with multiple data sources:

- **Marinade Finance MCP Server**: Real-time protocol state and documentation
- **ASI1 AI API**: Advanced language processing and response generation
- **Smithery Platform**: Hosted MCP server infrastructure

## License

MIT License - See LICENSE.md file for details.

---

<p align="center">
  Built with ❤️ for the Solana and Marinade Finance community
  <br>
  <em>"Making liquid staking accessible through intelligent conversation"</em>
</p>