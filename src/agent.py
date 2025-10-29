import json
import requests
from uuid import uuid4
from datetime import datetime, timezone, timedelta
import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent,
)
from uagents import Agent, Context, Protocol

import mcp
from mcp.client.streamable_http import streamablehttp_client

import os
from dotenv import load_dotenv

load_dotenv()

ASI1_API_KEY = os.getenv("ASI1_API_KEY")
ASI1_BASE_URL = "https://api.asi1.ai/v1"

SMITHERY_API_KEY = os.getenv("SMITHERY_API_KEY")
SMITHERY_PROFILE = os.getenv("SMITHERY_PROFILE")

ASI1_HEADERS = {
    "Authorization": f"Bearer {ASI1_API_KEY}" if ASI1_API_KEY else "",
    "Content-Type": "application/json",
}


class MarinadeFinanceMCPClient:
    def __init__(self):
        self.session: Optional[mcp.ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.all_tools = []
        self.default_timeout = timedelta(seconds=30)
        self.server_url = f"https://server.smithery.ai/@leandrogavidia/marinade-finance-mcp-server/mcp?api_key={SMITHERY_API_KEY}&profile={SMITHERY_PROFILE}"

    async def connect_to_server(self, ctx: Context):
        """Connect to the Marinade Finance MCP server and collect its tools"""
        try:
            ctx.logger.info(
                f"Connecting to Marinade Finance MCP server: {self.server_url}"
            )

            read_stream, write_stream, _ = await self.exit_stack.enter_async_context(
                streamablehttp_client(self.server_url)
            )

            self.session = await self.exit_stack.enter_async_context(
                mcp.ClientSession(read_stream, write_stream)
            )

            await self.session.initialize()
            tools_result = await self.session.list_tools()
            self.all_tools = tools_result.tools

            ctx.logger.info(f"Successfully connected to Marinade Finance MCP server")
            ctx.logger.info(
                f"Available tools: {', '.join([t.name for t in self.all_tools])}"
            )

        except Exception as e:
            ctx.logger.error(
                f"Error connecting to Marinade Finance MCP server: {str(e)}"
            )
            raise

    async def process_query_with_mcp(self, query: str, ctx: Context) -> str:
        """Process query using MCP tools when available, otherwise fallback to ASI1 API"""
        try:
            if self.session and self.all_tools:

                selected_tool = self._select_appropriate_tool(query, ctx)

                if selected_tool:
                    try:
                        ctx.logger.info(f"Using MCP tool: {selected_tool.name}")

                        params = self._prepare_tool_parameters(
                            selected_tool.name, query
                        )

                        result = await asyncio.wait_for(
                            self.session.call_tool(selected_tool.name, params),
                            timeout=self.default_timeout.total_seconds(),
                        )

                        mcp_context = self._format_mcp_context(result.content)
                        return await self.process_query_with_context(
                            query, mcp_context, ctx
                        )

                    except asyncio.TimeoutError:
                        ctx.logger.warning(
                            "MCP server timeout, falling back to ASI1 API"
                        )
                    except Exception as e:
                        ctx.logger.warning(
                            f"MCP tool error: {str(e)}, falling back to ASI1 API"
                        )

            return await self.process_query_with_asi1(query, ctx)

        except Exception as e:
            ctx.logger.error(f"Error in process_query_with_mcp: {str(e)}")
            return f"An error occurred: {str(e)}"

    def _select_appropriate_tool(self, query: str, ctx: Context):
        """Select the most appropriate MCP tool based on the query content"""
        if not self.all_tools:
            return None

        query_lower = query.lower()

        state_keywords = [
            "price",
            "current",
            "state",
            "balance",
            "amount",
            "value",
            "rewards",
            "rate",
            "apy",
            "apr",
            "stake",
            "unstake",
            "msol",
            "how much",
            "what is the",
            "current price",
            "latest",
        ]

        doc_keywords = [
            "how to",
            "guide",
            "tutorial",
            "documentation",
            "docs",
            "api",
            "sdk",
            "integration",
            "example",
            "code",
            "implement",
            "explain",
            "what is",
            "how does",
            "feature",
            "function",
        ]

        if any(keyword in query_lower for keyword in state_keywords):
            for tool in self.all_tools:
                if tool.name == "get_marinade_state":
                    ctx.logger.info(
                        f"Selected get_marinade_state for query: {query[:50]}..."
                    )
                    return tool

        if any(keyword in query_lower for keyword in doc_keywords):
            for tool in self.all_tools:
                if tool.name == "search_documentation":
                    ctx.logger.info(
                        f"Selected search_documentation for query: {query[:50]}..."
                    )
                    return tool

        for tool in self.all_tools:
            if tool.name == "search_documentation":
                ctx.logger.info(
                    f"Default to search_documentation for query: {query[:50]}..."
                )
                return tool

        return self.all_tools[0] if self.all_tools else None

    def _prepare_tool_parameters(self, tool_name: str, query: str) -> dict:
        """Prepare parameters for the selected MCP tool"""
        if tool_name == "search_documentation":
            return {"query": query}
        elif tool_name == "get_marinade_state":
            return {}
        else:

            return {"query": query}

    def _format_mcp_context(self, content) -> str:
        """Format MCP response content as context for the LLM"""
        try:
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                context_items = []
                for item in content:
                    if hasattr(item, "text") and hasattr(item, "type"):
                        text_content = item.text
                        context_items.append(text_content)
                    else:
                        context_items.append(str(item))

                return "\n\n".join(context_items)
            else:
                return str(content)
        except Exception as e:
            if isinstance(content, list):
                return "\n".join([str(item) for item in content])
            else:
                return str(content)

    async def process_query_with_context(
        self, query: str, context: str, ctx: Context
    ) -> str:
        """Process query using ASI1 API with MCP context"""
        try:
            user_message = {"role": "user", "content": query}
            system_message = {
                "role": "system",
                "content": (
                    "You are a helpful assistant specialized in answering questions about Marinade Finance. "
                    "Marinade Finance is a liquid staking protocol on Solana that allows users to stake SOL "
                    "and receive mSOL tokens in return, maintaining liquidity while earning staking rewards.\n\n"
                    "Use the following context from Marinade Finance documentation to provide accurate and helpful answers. "
                    "Format your response in a clear, conversational way that's easy for users to understand:\n\n"
                    f"CONTEXT:\n{context}\n\n"
                    "Based on this context, provide a comprehensive answer to the user's question. "
                    "If the context doesn't contain enough information to fully answer the question, "
                    "you can supplement with your general knowledge about Marinade Finance, but prioritize the provided context."
                ),
            }

            payload = {
                "model": "asi1-mini",
                "messages": [system_message, user_message],
                "temperature": 0.2,
                "max_tokens": 4096,
            }

            resp = requests.post(
                f"{ASI1_BASE_URL}/chat/completions",
                headers=ASI1_HEADERS,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            response_json = resp.json()
            model_msg = response_json["choices"][0]["message"]

            return model_msg["content"]

        except Exception as e:
            ctx.logger.error(f"Error processing query with context: {e}")
            return f"An error occurred: {e}"

    async def process_query_with_asi1(self, query: str, ctx: Context) -> str:
        """Process query using ASI1 API as fallback"""
        try:
            user_message = {"role": "user", "content": query}
            system_message = {
                "role": "system",
                "content": (
                    "You are a helpful assistant specialized in answering questions about Marinade Finance. "
                    "Marinade Finance is a liquid staking protocol on Solana that allows users to stake SOL "
                    "and receive mSOL tokens in return, maintaining liquidity while earning staking rewards."
                ),
            }

            payload = {
                "model": "asi1-mini",
                "messages": [system_message, user_message],
                "temperature": 0.2,
                "max_tokens": 4096,
            }

            resp = requests.post(
                f"{ASI1_BASE_URL}/chat/completions",
                headers=ASI1_HEADERS,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            response_json = resp.json()
            model_msg = response_json["choices"][0]["message"]

            return model_msg["content"]

        except Exception as e:
            ctx.logger.error(f"Error processing query with ASI1: {e}")
            return f"An error occurred: {e}"

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


def _text_msg(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


agent = Agent(name="marinade-finance-agent", port=8001, mailbox=True)
chat_proto = Protocol(spec=chat_protocol_spec)
mcp_client = MarinadeFinanceMCPClient()


@agent.on_event("startup")
async def _startup(ctx: Context):
    ctx.logger.info("🚀 Starting Marinade Finance Agent")


@chat_proto.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    try:
        ack = ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id
        )
        await ctx.send(sender, ack)

        if not mcp_client.session:
            try:
                await mcp_client.connect_to_server(ctx)
            except Exception as e:
                ctx.logger.warning(
                    f"Failed to connect to MCP server: {e}, will use ASI1 API only"
                )

        for item in msg.content:
            if isinstance(item, StartSessionContent):
                ctx.logger.info(f"Got a start session message from {sender}")
                continue
            elif isinstance(item, TextContent):
                ctx.logger.info(f"Got a message from {sender}: {item.text}")
                result = await mcp_client.process_query_with_mcp(item.text, ctx)

                response_text = (
                    result if isinstance(result, str) else json.dumps(result)
                )
                await ctx.send(sender, _text_msg(response_text))
            else:
                ctx.logger.info(f"Got unexpected content from {sender}")
    except Exception as e:
        ctx.logger.error(f"Error handling chat message: {str(e)}")
        await ctx.send(sender, _text_msg(f"An error occurred: {str(e)}"))


@chat_proto.on_message(model=ChatAcknowledgement)
async def handle_chat_acknowledgement(
    ctx: Context, sender: str, msg: ChatAcknowledgement
):
    ctx.logger.info(
        f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}"
    )
    if msg.metadata:
        ctx.logger.info(f"Metadata: {msg.metadata}")


agent.include(chat_proto)

if __name__ == "__main__":
    try:
        agent.run()
    except Exception as e:
        print(f"Error running agent: {str(e)}")
    finally:
        asyncio.run(mcp_client.cleanup())
