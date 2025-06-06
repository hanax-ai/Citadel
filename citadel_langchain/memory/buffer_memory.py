
"""
Buffer memory for Project Citadel LangChain integration.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from langchain.memory import ConversationBufferMemory as LangChainBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from citadel_core.logging import get_logger
from citadel_llm.gateway import OllamaGateway

from .base_memory import BaseMemory


class BufferMemory(BaseMemory):
    """
    Buffer memory for storing recent interactions.
    
    This memory component stores the most recent interactions in a buffer.
    """
    
    def __init__(
        self,
        memory: Optional[LangChainBufferMemory] = None,
        ollama_gateway: Optional[OllamaGateway] = None,
        model_name: str = "mistral:latest",
        memory_key: str = "history",
        input_key: str = "input",
        output_key: str = "output",
        return_messages: bool = True,
        human_prefix: str = "Human",
        ai_prefix: str = "AI",
        max_token_limit: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the buffer memory.
        
        Args:
            memory: LangChain buffer memory to use. If None, a new one will be created.
            ollama_gateway: OllamaGateway instance to use. If None, a new one will be created.
            model_name: Name of the model to use.
            memory_key: Key to use for storing memory in the chain.
            input_key: Key to use for storing inputs in the memory.
            output_key: Key to use for storing outputs in the memory.
            return_messages: Whether to return messages or a string.
            human_prefix: Prefix for human messages.
            ai_prefix: Prefix for AI messages.
            max_token_limit: Maximum number of tokens to store in the buffer.
            logger: Logger instance.
        """
        super().__init__(
            memory=memory,
            ollama_gateway=ollama_gateway,
            model_name=model_name,
            memory_key=memory_key,
            input_key=input_key,
            output_key=output_key,
            return_messages=return_messages,
            logger=logger,
        )
        
        self.human_prefix = human_prefix
        self.ai_prefix = ai_prefix
        self.max_token_limit = max_token_limit
        
        # Create the LangChain buffer memory if not provided
        if not self._memory:
            self._memory = LangChainBufferMemory(
                memory_key=memory_key,
                input_key=input_key,
                output_key=output_key,
                return_messages=return_messages,
                human_prefix=human_prefix,
                ai_prefix=ai_prefix,
                max_token_limit=max_token_limit,
            )
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load memory variables.
        
        Args:
            inputs: Input values.
            
        Returns:
            Dictionary of memory variables.
        """
        return self._memory.load_memory_variables(inputs)
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Save the context.
        
        Args:
            inputs: Input values.
            outputs: Output values.
        """
        self._memory.save_context(inputs, outputs)
    
    def clear(self) -> None:
        """
        Clear the memory.
        """
        self._memory.clear()
    
    @property
    def buffer(self) -> Union[List[BaseMessage], str]:
        """
        Get the buffer.
        
        Returns:
            Buffer as a list of messages or a string.
        """
        return self._memory.buffer
    
    @property
    def buffer_as_messages(self) -> List[BaseMessage]:
        """
        Get the buffer as a list of messages.
        
        Returns:
            Buffer as a list of messages.
        """
        return self._memory.buffer_as_messages
    
    @property
    def buffer_as_str(self) -> str:
        """
        Get the buffer as a string.
        
        Returns:
            Buffer as a string.
        """
        return self._memory.buffer_as_str
    
    def to_graph_node(self) -> Dict[str, Any]:
        """
        Convert the memory to a graph node.
        
        Returns:
            Dictionary representation of the memory as a graph node.
        """
        node = super().to_graph_node()
        node.update({
            "human_prefix": self.human_prefix,
            "ai_prefix": self.ai_prefix,
            "max_token_limit": self.max_token_limit,
        })
        return node
