"""
TCP server implementation for the MCP server.
"""

import asyncio
import logging
from typing import AsyncIterator, Tuple, Optional

logger = logging.getLogger("mcp_k8s_server")

class TcpReadStream:
    """
    Read stream for TCP connections.
    """
    
    def __init__(self, reader: asyncio.StreamReader):
        """
        Initialize the TCP read stream.
        
        Args:
            reader: The asyncio StreamReader.
        """
        self.reader = reader
    
    async def read(self, n: int = -1) -> bytes:
        """
        Read data from the stream.
        
        Args:
            n: Number of bytes to read. -1 means read until EOF.
            
        Returns:
            The data read.
        """
        return await self.reader.read(n)
    
    async def readline(self) -> bytes:
        """
        Read a line from the stream.
        
        Returns:
            The line read.
        """
        return await self.reader.readline()


class TcpWriteStream:
    """
    Write stream for TCP connections.
    """
    
    def __init__(self, writer: asyncio.StreamWriter):
        """
        Initialize the TCP write stream.
        
        Args:
            writer: The asyncio StreamWriter.
        """
        self.writer = writer
    
    async def write(self, data: bytes) -> None:
        """
        Write data to the stream.
        
        Args:
            data: The data to write.
        """
        self.writer.write(data)
        await self.writer.drain()
    
    async def close(self) -> None:
        """
        Close the stream.
        """
        self.writer.close()
        await self.writer.wait_closed()


class TcpServer:
    """
    TCP server for MCP communication.
    """
    
    def __init__(self, host: str, port: int):
        """
        Initialize the TCP server.
        
        Args:
            host: The host to bind to.
            port: The port to bind to.
        """
        self.host = host
        self.port = port
        self.server = None
        self.client_reader = None
        self.client_writer = None
    
    async def __aenter__(self) -> Tuple[TcpReadStream, TcpWriteStream]:
        """
        Start the server and wait for a client connection.
        
        Returns:
            A tuple of (read_stream, write_stream).
        """
        # Start the server
        self.server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        
        # Create a future to wait for a client connection
        self.client_connected = asyncio.Future()
        
        # Start serving
        asyncio.create_task(self.server.serve_forever())
        
        logger.info(f"TCP server started on {self.host}:{self.port}")
        
        # Wait for a client to connect
        await self.client_connected
        
        # Return the streams
        return (
            TcpReadStream(self.client_reader),
            TcpWriteStream(self.client_writer)
        )
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close the server.
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("TCP server closed")
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """
        Handle a client connection.
        
        Args:
            reader: The client's StreamReader.
            writer: The client's StreamWriter.
        """
        # Store the client's reader and writer
        self.client_reader = reader
        self.client_writer = writer
        
        # Set the future to indicate that a client has connected
        if not self.client_connected.done():
            self.client_connected.set_result(True)
        
        # Keep the connection open until the server is closed
        try:
            while not reader.at_eof():
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            writer.close()


class TcpServerContextManager:
    """
    Async context manager for TCP server.
    """
    
    def __init__(self, host: str, port: int):
        """
        Initialize the TCP server context manager.
        
        Args:
            host: The host to bind to.
            port: The port to bind to.
        """
        self.server = TcpServer(host, port)
    
    async def __aenter__(self) -> Tuple[TcpReadStream, TcpWriteStream]:
        """
        Enter the context manager.
        
        Returns:
            A tuple of (read_stream, write_stream).
        """
        return await self.server.__aenter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager.
        """
        await self.server.__aexit__(exc_type, exc_val, exc_tb)


def tcp_server(host: str, port: int) -> TcpServerContextManager:
    """
    Create a TCP server for MCP communication.
    
    Args:
        host: The host to bind to.
        port: The port to bind to.
        
    Returns:
        An async context manager that yields (read_stream, write_stream).
    """
    return TcpServerContextManager(host, port)
