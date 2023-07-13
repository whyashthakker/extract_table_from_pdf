import os
import glob
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import tabula

os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@11"

def pdf_splitter(path):
    fname = os.path.splitext(os.path.basename(path))[0]
    pdf = PdfReader(path)
    for page in range(len(pdf.pages)):
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf.pages[page])
        output_filename = '{}_page_{}.pdf'.format(fname, page+1)
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
        print('Created: {}'.format(output_filename))

def pdf_to_tables(pdf_files):
    all_tables = []
    for pdf_file in pdf_files:
        tables = tabula.read_pdf(pdf_file, pages="all", multiple_tables=True)
        for table in tables:
            all_tables.append(table)
    return pd.concat(all_tables)

st.title('PDF Table Extractor')
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())
    pdf_splitter('temp.pdf')
    pdf_files = glob.glob("*.pdf")
    df = pdf_to_tables(pdf_files)
    st.write(df)
