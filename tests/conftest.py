from marker.v2.providers.pdf import PdfProvider
import tempfile

import datasets
import pytest

from marker.v2.models import setup_layout_model, setup_texify_model, setup_recognition_model, setup_table_rec_model, \
    setup_detection_model
from marker.v2.builders.document import DocumentBuilder
from marker.v2.builders.layout import LayoutBuilder
from marker.v2.builders.ocr import OcrBuilder
from marker.v2.schema.document import Document


@pytest.fixture(scope="session")
def layout_model():
    layout_m = setup_layout_model()
    yield layout_m
    del layout_m


@pytest.fixture(scope="session")
def detection_model():
    detection_m = setup_detection_model()
    yield detection_m
    del detection_m


@pytest.fixture(scope="session")
def texify_model():
    texify_m = setup_texify_model()
    yield texify_m
    del texify_m


@pytest.fixture(scope="session")
def recognition_model():
    ocr_m = setup_recognition_model()
    yield ocr_m
    del ocr_m


@pytest.fixture(scope="session")
def table_rec_model():
    table_rec_m = setup_table_rec_model()
    yield table_rec_m
    del table_rec_m


@pytest.fixture(scope="function")
def pdf_document(request, layout_model, recognition_model, detection_model) -> Document:
    mark = request.node.get_closest_marker("filename")
    if mark is None:
        filename = "adversarial.pdf"
    else:
        filename = mark.args[0]

    dataset = datasets.load_dataset("datalab-to/pdfs", split="train")
    idx = dataset['filename'].index(filename)

    temp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf")
    temp_pdf.write(dataset['pdf'][idx])
    temp_pdf.flush()

    provider = PdfProvider(temp_pdf.name)
    layout_builder = LayoutBuilder(layout_model)
    ocr_builder = OcrBuilder(detection_model, recognition_model)
    builder = DocumentBuilder()
    document = builder(provider, layout_builder, ocr_builder)
    return document
