"""Document parsing for multiple formats."""

from typing import Dict, List, Any
from pathlib import Path
import re


class DocumentParser:
    """Parse documents in various formats."""
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse a document and extract text content."""
        path = Path(file_path)
        file_type = path.suffix.lower()
        
        if file_type == '.pdf':
            return self._parse_pdf(file_path)
        elif file_type == '.docx':
            return self._parse_docx(file_path)
        elif file_type == '.xlsx':
            return self._parse_xlsx(file_path)
        elif file_type == '.pptx':
            return self._parse_pptx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF document."""
        # For demo: simple text extraction
        # In production: use PyPDF2, pdfplumber, or similar
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pages = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    pages.append({
                        "page_number": i + 1,
                        "text": text,
                        "metadata": {}
                    })
                return {
                    "pages": pages,
                    "total_pages": len(pages),
                    "metadata": {}
                }
        except ImportError:
            # Fallback for demo without PyPDF2
            return self._parse_demo_pdf(file_path)
    
    def _parse_demo_pdf(self, file_path: str) -> Dict[str, Any]:
        """Demo parser that creates synthetic content based on filename."""
        filename = Path(file_path).name
        
        # Create synthetic content for demo
        content = f"""
        Document: {filename}
        
        This is a sample document for the Questionnaire Agent demo.
        
        Investment Strategy:
        The fund focuses on growth equity investments in technology companies.
        Target sectors include software, fintech, and healthcare technology.
        
        Fund Structure:
        The fund is structured as a limited partnership with a 10-year term.
        Management fee is 2% on committed capital during investment period.
        
        Performance:
        Historical IRR of 25% across previous funds.
        Portfolio includes 15 active investments with strong growth trajectories.
        
        Team:
        Led by experienced investment professionals with 15+ years in private equity.
        Dedicated sector specialists for key verticals.
        """
        
        return {
            "pages": [
                {
                    "page_number": 1,
                    "text": content,
                    "metadata": {"source": filename}
                }
            ],
            "total_pages": 1,
            "metadata": {"filename": filename}
        }
    
    def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        """Parse DOCX document."""
        # For demo: return synthetic content
        return self._parse_demo_pdf(file_path)
    
    def _parse_xlsx(self, file_path: str) -> Dict[str, Any]:
        """Parse XLSX spreadsheet."""
        # For demo: return synthetic content
        return self._parse_demo_pdf(file_path)
    
    def _parse_pptx(self, file_path: str) -> Dict[str, Any]:
        """Parse PPTX presentation."""
        # For demo: return synthetic content
        return self._parse_demo_pdf(file_path)
    
    def parse_questionnaire(self, file_path: str) -> Dict[str, Any]:
        """Parse questionnaire to extract sections and questions."""
        # Parse the document
        parsed = self.parse(file_path)
        
        # Extract structure (for demo, create sample structure)
        sections = self._extract_questionnaire_structure(parsed)
        
        return {
            "sections": sections,
            "total_sections": len(sections),
            "total_questions": sum(len(s["questions"]) for s in sections)
        }
    
    def _extract_questionnaire_structure(self, parsed_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sections and questions from parsed questionnaire."""
        # For demo: create sample questionnaire structure
        sections = [
            {
                "title": "Investment Strategy & Objectives",
                "order": 1,
                "questions": [
                    {"text": "What is the fund's primary investment strategy?", "order": 1},
                    {"text": "What are the target sectors and geographies?", "order": 2},
                    {"text": "What is the typical investment size and ownership percentage?", "order": 3},
                ]
            },
            {
                "title": "Fund Structure & Terms",
                "order": 2,
                "questions": [
                    {"text": "What is the fund size and target capital raise?", "order": 1},
                    {"text": "What are the management fees and carried interest terms?", "order": 2},
                    {"text": "What is the fund term and investment period?", "order": 3},
                ]
            },
            {
                "title": "Team & Organization",
                "order": 3,
                "questions": [
                    {"text": "Who are the key investment professionals and their backgrounds?", "order": 1},
                    {"text": "What is the organizational structure and decision-making process?", "order": 2},
                    {"text": "How is the team compensated and incentivized?", "order": 3},
                ]
            },
            {
                "title": "Track Record & Performance",
                "order": 4,
                "questions": [
                    {"text": "What is the historical performance across previous funds?", "order": 1},
                    {"text": "What are the realized vs. unrealized returns?", "order": 2},
                    {"text": "Can you provide case studies of successful investments?", "order": 3},
                ]
            },
            {
                "title": "Operations & Compliance",
                "order": 5,
                "questions": [
                    {"text": "What are the key operational policies and procedures?", "order": 1},
                    {"text": "How is compliance managed and monitored?", "order": 2},
                    {"text": "What are the ESG considerations and policies?", "order": 3},
                ]
            }
        ]
        
        return sections


# Global parser instance
document_parser = DocumentParser()
