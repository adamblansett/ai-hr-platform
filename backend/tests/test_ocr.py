from backend.app.services.document_ocr_service import document_ocr_service

def test_i9_document_ocr():
    sample_content = b"%PDF-1.4 ... Employment Eligibility Verification Form I-9 ... Signed: Elena Rostova"
    res = document_ocr_service.verify_document_content("Elena_I9_Signed.pdf", sample_content, "Elena Rostova")
    assert res.form_type == "FORM_I9"
    assert res.compliance_status == "VERIFIED"
    assert res.confidence_score >= 0.85
    assert res.signature_detected is True

def test_w4_document_ocr():
    sample_content = b"%PDF-1.4 ... Form W-4 Employee's Withholding Certificate ... Sig"
    res = document_ocr_service.verify_document_content("W4_Tax_Form.pdf", sample_content, "Alex Chen")
    assert res.form_type == "FORM_W4"
    assert res.compliance_status == "VERIFIED"

def test_unverified_document_flagged():
    sample_content = b"Draft notes without signature or valid certificate"
    res = document_ocr_service.verify_document_content("unclear_image.png", sample_content, "Marcus Vance")
    assert res.signature_detected is False
    assert res.compliance_status == "FLAGGED_FOR_MANUAL_REVIEW"
