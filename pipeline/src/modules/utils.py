

from pathlib import Path
import json





#TODO:determine valididty of audio files
#ref: https://librosa.org/doc/main/generated/librosa.util.valid_audio.html



def output_to_pdf(dialogue, filename=None, output_type='file'):
    """Transform output and convert to PDF.
    file_path = Path('./output.json')
    with open(file_path, ) as f:
        output = json.load(f)
    lines = output['chunks']

    'results.pdf'
    """
    results = []
    
    lines = dialogue['chunks']
    timestamps = [line['timestamp'] for line in lines]
    stamps = [[-1,-1] for idx in range(len(timestamps))]
    trigger = False
    for idx in range(len(timestamps)):
        if idx==0:
            stamps[0] = timestamps[0]
        elif (timestamps[idx][0] == timestamps[idx-1][1]) and trigger==False:
            stamps[idx]= timestamps[idx]
        elif trigger==True:
            stamps[idx] = [ (stamps[idx-1])[1], stamps[idx-1][1] + timestamps[idx][1] ]
        else:
            stamps[idx] = [ timestamps[idx-1][1], timestamps[idx-1][1] + timestamps[idx][1] ]
            trigger = True

    for idx in range(len(timestamps)):
        item = f'{stamps[idx]}  -  {lines[idx]["text"]} \n'
        results.append(item)

    #print( ('').join(results) )
    str_results = ('').join(results)
    pdf = text_to_pdf(str_results)

    if output_type=='file':
        pdf.output(filename, 'F')
        return True
    elif output_type=='str':
        result = {
            'dialogue': dialogue,
            'object':pdf, 
            'byte_string': pdf.output(dest='S').encode('latin-1')
            }
        return result
    elif output_type=='object':
        return pdf
    else:
        raise TypeError(f'argument "output_type" must be: "file" or "str"; parameter provided: {output_type}')


import textwrap
from fpdf import FPDF

def text_to_pdf(text):
    """Convert text to PDF object.
    
    ref: https://stackoverflow.com/questions/10112244/convert-plain-text-to-pdf-in-python
    """
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    return pdf


from pypdf import PdfReader
import io
import gzip
import copy

def export_to_vdi_workspace(pdfs):
    """..."""

    #get schema
    filepath_original_wksp_gzip = Path('./tests/input/VDI_ApplicationStateData_v0.2.1.gz') 

    with gzip.open(filepath_original_wksp_gzip, 'rb') as f_in:
        workspace_json = json.load(f_in)

    #create empty schema
    workspace_schema = copy.deepcopy(workspace_json)
    sample_item = workspace_schema['documentsIndex']['documents'][0]
    for k,v in sample_item.items():
        sample_item[k] = None
    documents_schema = copy.deepcopy(sample_item)

    #load documents
    documents = []
    for idx, pdf in enumerate(pdfs):
        document_record = copy.deepcopy(documents_schema)
        pdf_pages = {}
        with io.BytesIO(pdf['byte_string']) as open_pdf_file:
            reader = PdfReader(open_pdf_file)
            for page in range( len(reader.pages) ):
                text = reader.pages[page].extract_text()
                pdf_pages[page+1] = text

        #raw
        document_record['id'] = str(idx)
        document_record['body_chars'] = {idx+1: len(page) for idx, page in enumerate(pdf_pages.values())}                 #{1: 3958, 2: 3747, 3: 4156, 4: 4111,
        document_record['body_pages'] = pdf_pages                                                                           #{1: 'Weakly-Supervised Questions for Zero-Shot Relation…a- arXiv:2301.09640v1 [cs.CL] 21 Jan 2023<br><br>', 2: 'tive approach without using any gold question temp…et al., 2018) with unanswerable questions<br><br>', 3: 'by generating a special unknown token in the out- …ng training. These spurious questions can<br><b
        document_record['date_created'] = None
        #document_record['length_lines'] = None    #0
        #document_record['length_lines_array'] = None    #[26, 26, 7, 
        document_record['page_nos'] = pdf['object'].pages.__len__()
        data_array = {idx: val for idx,val in enumerate(list( pdf['byte_string'] ))}        #new list of integers that are the ascii values of the byte string
        document_record['dataArray'] = data_array
        document_record['toc'] = []
        document_record['pp_toc'] = ''
        document_record['clean_body'] = ' '.join( list(pdf_pages.values()) )
        
        #file info
        document_record['file_extension'] = pdf['dialogue']['file_name'].split('.')[1]
        document_record['file_size_mb'] = None
        document_record['filename_original'] = pdf['dialogue']['file_name']
        document_record['filepath'] = pdf['dialogue']['file_path']
        document_record['filetype'] = 'audio'
        document_record['date'] = None
        document_record['reference_number'] = None
        document_record['sort_key'] = 0
        document_record['hit_count'] = 0
        document_record['snippets'] = []
        document_record['summary'] = "TODO:summary"
        document_record['_showDetails'] = False
        document_record['_activeDetailsTab'] = 0

        document_record['models'] = pdf['dialogue']['classifier']




        '''
        #original
        document_record['id'] = idx
        document_record['filepath'] = pdf['dialogue']['file_path']
        document_record['filename_original'] = pdf['dialogue']['file_name']
        document_record['filename_modified'] = pdf['dialogue']['file_name']
        document_record['file_extension'] = pdf['dialogue']['file_name'].split('.')[1]
        document_record['filetype'] = 'audio'
        document_record['page_nos'] = pdf['object'].pages.__len__()

        document_record['dataArray'] = None
        data_array = {idx: val for idx,val in enumerate(list( pdf['byte_string'] ))}        #new list of integers that are the ascii values of the byte string
        document_record['dataArray'] = data_array
        document_record['length_lines'] = None
        document_record['file_size_mb'] = None
        document_record['date'] = None
        document_record['toc'] = None
        document_record['pp_toc'] = ''

        'accumPageChars'
        'body_chars'
        'html_body'
        document_record['body_chars'] = None
        document_record['body_pages'] = None
        document_record['clean_body'] = ' '.join( list(pdf_pages.values()) )

        document_record['sort_key'] = 0
        document_record['hit_count'] = 0
        document_record['snippets'] = []
        document_record['selected_snippet_page'] = 1
        document_record['_showDetails'] = False
        document_record['_activeDetailsTab'] = 0
        document_record['accumPageLines'] = None
        '''

        documents.append(document_record)

    #load lunr index => TODO:REMOVE
    #workspace_schema['documentsIndex']['indices']['lunrIndex'] = {}


    #compare
    workspace_schema['documentsIndex']['documents'] = documents
    json.dumps(workspace_schema) == json.dumps(workspace_json)
    #list(workspace_json['documentsIndex']['documents'][0]['dataArray'].values())
    #list( pdf['byte_string'] )

    #export
    filepath_export_wksp_gzip = Path('./tests/results/VDI_ApplicationStateData_vTEST.gz')

    with gzip.open(filepath_export_wksp_gzip, 'wb') as f_out:
        f_out.write( bytes(json.dumps(workspace_schema), encoding='utf8') )

    return True
        

    










if __name__ == "__main__":
    output_to_pdf()