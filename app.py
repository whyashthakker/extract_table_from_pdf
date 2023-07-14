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
    return glob.glob(f'{fname}_page_*.pdf')

def pdf_to_tables(pdf_files):
    all_tables = []
    for pdf_file in pdf_files:
        tables = tabula.read_pdf(pdf_file, pages="all", multiple_tables=True)
        for table in tables:
            all_tables.append(table)
    return all_tables

st.title('PDF Table Extractor')
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())
    pdf_files = pdf_splitter('temp.pdf')
    tables = pdf_to_tables(pdf_files)

    # Write to Excel
    excel_file = 'tables.xlsx'
    with pd.ExcelWriter(excel_file) as writer:
        for i, table in enumerate(tables, start=1):
            table.to_excel(writer, sheet_name=f'Table {i}')

    # Offer the Excel file for download
    with open(excel_file, 'rb') as f:
        bytes = f.read()
        st.download_button(
            label="Download Excel file",
            data=bytes,
            file_name='tables.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    for i, table in enumerate(tables, start=1):
        st.subheader(f'Table {i}')
        st.dataframe(table)

    # Remove temporary files
    for file in pdf_files:
        os.remove(file)
    os.remove("temp.pdf")
    os.remove(excel_file)
