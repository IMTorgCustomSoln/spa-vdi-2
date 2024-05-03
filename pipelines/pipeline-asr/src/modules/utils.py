

from pathlib import Path
import os
import json
import gzip, zipfile
import shutil




#TODO:determine valididty of audio files
#ref: https://librosa.org/doc/main/generated/librosa.util.valid_audio.html

def absoluteFilePaths(directory):
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
            yield Path( os.path.abspath(os.path.join(dirpath, f)) )


def get_next_batch(lst, batch_count):
    """...."""
    final_idx = int(len(lst)/batch_count-1)
    index_list = list(range( final_idx + 1  ))
    remainder = len(lst)%batch_count
    for idx in index_list:
        init = idx * batch_count
        if remainder>0 and idx==final_idx:
            batch = lst[init: (idx+1) * batch_count+remainder]
        else:
            batch = lst[init: (idx+1) * batch_count]
        yield batch


def get_decompressed_filepath(filepath, target_extension=[]):
    """Return path of all decompressed files.
    
    Check if file is compressed.  Provide file path if it is not.  If it is, then decompress
    to directory, and return files of correct target extension.

    ref: https://stackoverflow.com/questions/3703276/how-to-tell-if-a-file-is-gzip-compressed
    """
    def get_dirs_from_path(path):
        result = []
        for file in os.scandir(path):
            if os.path.isdir(file):
                if not any( [x in file.path for x in ['.DS_Store','__MACOSX']] ):
                    result.append(file)
        return result

    #zip format options
    suffixes_archives = ['.gz', '.zip']
    def gz_file(filepath):
        with gzip.open(filepath, 'rb') as f_in:
            f_out_name = f'{filepath}.OUT'
            with open(f_out_name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return f_out_name
    
    def zip_file(filepath):
        extract_dir = filepath.resolve().parent / 'PROCESSED'
        original_dirs = get_dirs_from_path(extract_dir)
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        current_dirs = get_dirs_from_path(extract_dir)
        new_dirs = list( set(current_dirs).difference(original_dirs) )
        files_to_keep = []
        #files_to_remove = []
        for dir in new_dirs:
            for file in absoluteFilePaths(dir):
                if Path(file).suffix in ['.wav', '.mp3']:
                    files_to_keep.append(file)
        return files_to_keep

    options = {
        b'\x1f\x8b': gz_file,
        b'PK': zip_file
    }

    #workflow
    filepath = Path(filepath)
    if os.path.isdir(filepath):
        return [None]
    check_compressed = (False, b'')
    with open(filepath, 'rb') as test_f:
        bytes = test_f.read(2)
        if (bytes == b'\x1f\x8b') or (bytes == b'PK'):
            check_compressed = (True, bytes)

    result = []
    if not check_compressed[0] and filepath.suffix in target_extension:
        result.append(filepath)
    elif not check_compressed[0] and not filepath.suffix in suffixes_archives:
        print(f'filepath bytes does not look like archive file, but contained suffix: {filepath.suffix}')
        result.append(None)
    else:
        if check_compressed[1] in options.keys():
            lst_of_filepaths = options[ check_compressed[1] ](filepath)
            result.extend( lst_of_filepaths)
        else:
            print('ERROR: not a recognized decompression format')
    return result


def format_dialogue_timestamps(dialogue):
    """..."""
    mod_dialogue = dialogue
    return mod_dialogue


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
    try:
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
    except Exception as e:
        print(e)
        #TODO:Whisper did not predict an ending timestamp, which can happen if audio is cut off in the middle of a word.  Also make sure WhisperTimeStampLogitsProcessor was used during generation.
        return None

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


def get_schema_from_workspace(filepath):
    """..."""

    #get schema
    filepath_original_wksp_gzip = Path(filepath)             #Path('./tests/input/VDI_ApplicationStateData_v0.2.1.gz') 

    with gzip.open(filepath_original_wksp_gzip, 'rb') as f_in:
        workspace_json = json.load(f_in)

    #create empty schema
    workspace_schema = copy.deepcopy(workspace_json)
    sample_item = workspace_schema['documentsIndex']['documents'][0]
    for k,v in sample_item.items():
        sample_item[k] = None
    documents_schema = copy.deepcopy(sample_item)
    workspace_schema['documentsIndex']['indices']['lunrIndex'] = {}
    workspace_schema['documentsIndex']['documents'] = documents_schema

    return workspace_schema


def export_to_vdi_workspace(workspace, dialogues, filepath):
    """..."""
    workspace_schema = copy.deepcopy(workspace)
    documents_schema = workspace_schema['documentsIndex']['documents']

    #to string
    pdfs = []
    for dialogue in dialogues:
        mod_dialogue = format_dialogue_timestamps(dialogue)
        pdf = output_to_pdf(
            dialogue=mod_dialogue,
            output_type='str'
        )
        if pdf!=None:
            pdfs.append(pdf)

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
    #json.dumps(workspace_schema) == json.dumps(workspace_json)
    #list(workspace_json['documentsIndex']['documents'][0]['dataArray'].values())
    #list( pdf['byte_string'] )

    #export
    #filepath_export_wksp_gzip = Path('./tests/results/VDI_ApplicationStateData_vTEST.gz')
    filepath_export_wksp_gzip = filepath

    with gzip.open(filepath_export_wksp_gzip, 'wb') as f_out:
        f_out.write( bytes(json.dumps(workspace_schema), encoding='utf8') )

    return True
        

    










if __name__ == "__main__":
    output_to_pdf()