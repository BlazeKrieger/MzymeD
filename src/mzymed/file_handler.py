"""
File upload and validation module for enzyme and substrate sequences.
"""

import os
from typing import Dict, Tuple, Optional
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


class FileUploader:
    """Handle file uploads and sequence validation."""
    
    SUPPORTED_FORMATS = ['fasta', 'pdb', 'cif', 'genbank']
    
    def __init__(self, upload_dir: str = "uploads"):
        """
        Initialize file uploader.
        
        Args:
            upload_dir: Directory to save uploaded files
        """
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def save_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(file_content)
        return filepath
    
    def validate_sequence_file(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate if file contains valid sequence data.
        
        Args:
            filepath: Path to sequence file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Try to detect format from extension
            ext = filepath.split('.')[-1].lower()
            if ext in ['fa', 'fasta']:
                format_type = 'fasta'
            elif ext in ['gb', 'genbank']:
                format_type = 'genbank'
            elif ext == 'pdb':
                return True, "PDB file detected"
            elif ext == 'cif':
                return True, "CIF file detected"
            else:
                return False, f"Unsupported file format: {ext}"
            
            # Try to parse the file
            records = list(SeqIO.parse(filepath, format_type))
            if len(records) == 0:
                return False, "No sequences found in file"
            
            return True, f"Found {len(records)} sequence(s)"
            
        except Exception as e:
            return False, f"Error validating file: {str(e)}"
    
    def load_sequence(self, filepath: str) -> Optional[SeqRecord]:
        """
        Load sequence from file.
        
        Args:
            filepath: Path to sequence file
            
        Returns:
            SeqRecord object or None if failed
        """
        try:
            ext = filepath.split('.')[-1].lower()
            if ext in ['fa', 'fasta']:
                format_type = 'fasta'
            elif ext in ['gb', 'genbank']:
                format_type = 'genbank'
            else:
                return None
            
            records = list(SeqIO.parse(filepath, format_type))
            return records[0] if records else None
            
        except Exception as e:
            print(f"Error loading sequence: {e}")
            return None
    
    def create_fasta_from_sequence(self, sequence: str, seq_id: str, 
                                   description: str = "") -> str:
        """
        Create FASTA file from sequence string.
        
        Args:
            sequence: Amino acid or nucleotide sequence
            seq_id: Sequence identifier
            description: Sequence description
            
        Returns:
            Path to created FASTA file
        """
        record = SeqRecord(
            Seq(sequence),
            id=seq_id,
            description=description
        )
        
        filepath = os.path.join(self.upload_dir, f"{seq_id}.fasta")
        SeqIO.write(record, filepath, "fasta")
        return filepath
