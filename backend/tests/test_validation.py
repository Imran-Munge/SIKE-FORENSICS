from app.services.file_validation import validate_upload
def test_invalid_upload():
    ok,reason=validate_upload("x.jpg",b"not an image","image/jpeg")
    assert not ok
def test_empty_filename():
    ok,_=validate_upload("",b"abc","")
    assert not ok
