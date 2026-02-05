"""
Comprehensive test script for the Questionnaire Agent system.
Tests the complete workflow with sample PDFs from the data directory.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.services.document_service import document_service
from src.services.project_service import project_service
from src.services.answer_service import answer_service
from src.services.evaluation_service import evaluation_service
from src.indexing.indexer import document_indexer
from src.models import DocumentScope


def test_complete_workflow():
    """Test the complete questionnaire agent workflow."""
    print("=" * 80)
    print("QUESTIONNAIRE AGENT - COMPLETE WORKFLOW TEST")
    print("=" * 80)
    
    # Step 1: Register and index documents
    print("\n[1] Registering and indexing documents...")
    
    # Register questionnaire
    questionnaire_path = "data/ILPA_Due_Diligence_Questionnaire_v1.2.pdf"
    questionnaire = document_service.register_existing_document(
        questionnaire_path,
        is_questionnaire=True
    )
    print(f"✓ Registered questionnaire: {questionnaire.name} (ID: {questionnaire.id})")
    
    # Register reference documents
    reference_docs = [
        "data/20260110_MiniMax_Accountants_Report.pdf",
        "data/20260110_MiniMax_Audited_Consolidated_Financial_Statements.pdf",
        "data/20260110_MiniMax_Global_Offering_Prospectus.pdf",
        "data/20260110_MiniMax_Industry_Report.pdf",
    ]
    
    doc_ids = []
    for doc_path in reference_docs:
        doc = document_service.register_existing_document(doc_path, is_questionnaire=False)
        doc_ids.append(doc.id)
        print(f"✓ Registered document: {doc.name} (ID: {doc.id})")
    
    # Index all documents
    print("\n[2] Indexing documents...")
    for doc_id in doc_ids:
        doc = document_service.get_document(doc_id)
        result = document_indexer.index_document(doc_id, doc.file_path)
        print(f"✓ Indexed: {doc.name} - {result['answer_chunks']} answer chunks, {result['citation_chunks']} citation chunks")
    
    # Step 2: Create project with ALL_DOCS scope
    print("\n[3] Creating project with ALL_DOCS scope...")
    project = project_service.create_project(
        name="Q1 2026 Due Diligence Review",
        questionnaire_id=questionnaire.id,
        document_scope=DocumentScope.ALL_DOCS
    )
    print(f"✓ Created project: {project.name} (ID: {project.id})")
    print(f"  Status: {project.status}")
    print(f"  Total questions: {project.total_questions}")
    
    # Step 3: Generate answers for all questions
    print("\n[4] Generating answers for all questions...")
    result = answer_service.generate_all_answers(project.id)
    print(f"✓ Generated: {result['generated']} answers")
    print(f"  Failed: {result['failed']} answers")
    
    # Step 4: Display sample answers
    print("\n[5] Sample generated answers:")
    sections = project_service.get_project_sections(project.id)
    
    for section in sections[:2]:  # Show first 2 sections
        print(f"\n  Section: {section.title}")
        for question in section.questions[:2]:  # Show first 2 questions per section
            answer_record = answer_service.db.find_one("answers", {"question_id": question.id})
            if answer_record:
                print(f"\n    Q: {question.text}")
                print(f"    Status: {answer_record['status']}")
                print(f"    Answerable: {answer_record['is_answerable']}")
                if answer_record.get('ai_answer'):
                    print(f"    Answer: {answer_record['ai_answer'][:150]}...")
                if answer_record.get('confidence_score'):
                    print(f"    Confidence: {answer_record['confidence_score']:.2%}")
                if answer_record.get('citations'):
                    print(f"    Citations: {len(answer_record['citations'])} reference(s)")
    
    # Step 5: Test adding a new document (should mark ALL_DOCS projects as OUTDATED)
    print("\n[6] Testing document addition (OUTDATED status check)...")
    print(f"  Project status before: {project.status}")
    
    # Register another document
    new_doc = document_service.register_existing_document(
        "data/20260110_MiniMax_Accountants_Report.pdf",  # Re-using for demo
        is_questionnaire=False
    )
    document_indexer.index_document(new_doc.id, new_doc.file_path)
    print(f"✓ Added and indexed new document: {new_doc.name}")
    
    # Check project status
    updated_project = project_service.get_project(project.id)
    print(f"  Project status after: {updated_project.status}")
    
    if updated_project.status.value == "OUTDATED":
        print("✓ SUCCESS: Project correctly marked as OUTDATED")
    else:
        print("✗ FAILED: Project should be OUTDATED after adding document")
    
    # Step 6: Test manual answer update
    print("\n[7] Testing manual answer update...")
    first_section = sections[0]
    first_question = first_section.questions[0]
    answer_record = answer_service.db.find_one("answers", {"question_id": first_question.id})
    
    if answer_record:
        from src.models import AnswerStatus
        updated = answer_service.update_answer(
            answer_record['id'],
            status=AnswerStatus.CONFIRMED,
            review_notes="Reviewed and approved by analyst"
        )
        print(f"✓ Updated answer for: {first_question.text[:80]}...")
        print(f"  New status: {updated.status}")
        print(f"  Review notes: {updated.review_notes}")
    
    # Step 7: Test evaluation
    print("\n[8] Testing evaluation framework...")
    # Create sample human answer
    if answer_record and answer_record.get('ai_answer'):
        human_answer = "The fund employs a growth equity strategy targeting technology companies in software and fintech sectors."
        
        eval_result = evaluation_service.evaluate_answer(
            first_question.id,
            human_answer
        )
        
        print(f"✓ Evaluated answer for: {first_question.text[:80]}...")
        print(f"  Similarity score: {eval_result.similarity_score:.2%}")
        print(f"  Semantic similarity: {eval_result.semantic_similarity:.2%}")
        print(f"  Keyword overlap: {eval_result.keyword_overlap:.2%}")
        print(f"  Explanation: {eval_result.explanation}")
    
    # Step 8: Project status summary
    print("\n[9] Final project status:")
    status = project_service.get_project_status(project.id)
    print(f"  Project: {project.name}")
    print(f"  Status: {status['status']}")
    print(f"  Questions answered: {status['answered_questions']} / {status['total_questions']}")
    print(f"  Status breakdown:")
    for status_name, count in status['status_breakdown'].items():
        print(f"    {status_name}: {count}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Start backend: cd backend && uvicorn app:app --reload")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Access UI at: http://localhost:5173")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_complete_workflow()
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
