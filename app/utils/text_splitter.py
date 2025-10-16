from typing import List
import tiktoken

class TextSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, encoding_name: str = "cl100k_base"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks based on token count."""
        if not text or not text.strip():
            return []
        
        tokens = self.encoding.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            start = end - self.chunk_overlap
        
        return chunks
    
    def split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs, respecting chunk size."""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            tokens = self.encoding.encode(current_chunk + "\n\n" + para if current_chunk else para)
            
            if len(tokens) <= self.chunk_size:
                current_chunk = current_chunk + "\n\n" + para if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                if len(self.encoding.encode(para)) > self.chunk_size:
                    para_chunks = self.split_text(para)
                    chunks.extend(para_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks