from chromeguard.scanners.signature_matcher import SignatureMatcher


def test_signature_matcher_detects_base64_eval() -> None:
    matcher = SignatureMatcher()
    findings = matcher.scan_blob("eval(atob('c3VzcGVjdA=='))")
    assert any(f["name"] == "Base64 payload exfil" for f in findings)


def test_signature_matcher_detects_domain() -> None:
    matcher = SignatureMatcher()
    findings = matcher.scan_blob("fetch('https://deepaichats.com/api')")
    assert any("Chat exfil domain" in f["name"] for f in findings)

