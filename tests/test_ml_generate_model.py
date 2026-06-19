import os
from ml import generate_dummy_model


def test_generate_model(tmp_path):
    out = tmp_path / 'm.h5'
    generate_dummy_model.build_and_save(str(out))
    assert out.exists()
