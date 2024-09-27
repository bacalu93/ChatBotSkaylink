import os
import uuid
import logging
import boto3
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text
from pypdf import PdfReader
from embedding import calculate_document_embeddings


def process_file(file_key, bucket_name, s3_client, contents, page_numbers, sources, embeddings):
    """Process a file and extract its contents, page numbers, and embeddings."""
    logging.info(f"Reading file: {file_key}")

    # Get the object
    file_obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    if file_key.endswith('.pdf'):
        file_name_tmp = f'{str(uuid.uuid4())}.pdf'
        s3_client.download_file(bucket_name, file_key, f"/tmp/{file_name_tmp}")
        reader = PdfReader(f"/tmp/{file_name_tmp}")
        page_labels = reader.page_labels
        elements = partition_pdf(f"/tmp/{file_name_tmp}", strategy="auto", chunking_strategy="by_title")
        page_numbers.extend([page_labels[int(el.metadata.page_number)-1] for el in elements])
    elif file_key.endswith('.docx'):
        file_name_tmp = f'{str(uuid.uuid4())}.docx'
        s3_client.download_file(bucket_name, file_key, f"/tmp/{file_name_tmp}")
        elements = partition_docx(f"/tmp/{file_name_tmp}", strategy="auto", chunking_strategy="by_title")
        page_numbers.extend([str(el.metadata.page_number) for el in elements])
    elif file_key.endswith('.txt'):
        file_name_tmp = f'{str(uuid.uuid4())}.txt'
        s3_client.download_file(bucket_name, file_key, f"/tmp/{file_name_tmp}")
        elements = partition_text(f"/tmp/{file_name_tmp}", chunking_strategy="by_title")
        page_numbers.extend(['1' for x in range(len(elements))])
    else:
        logging.warning(f"Unsupported file type: {file_key}")
        return [], [], []

    contents.extend([str(el) for el in elements])
    sources.extend([{"sourceUrl":f"s3://{bucket_name}/{file_key}"} for x in range(len(elements))])
    embeddings.extend(calculate_document_embeddings([str(el) for el in elements]))     

    return contents, page_numbers, sources, embeddings