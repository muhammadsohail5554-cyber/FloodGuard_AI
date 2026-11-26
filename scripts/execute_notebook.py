"""Execute notebook cells with IPython in-process and record actual outputs.

Useful in restricted environments where Jupyter's kernel sockets are unavailable.
This executes the same Python cells; it does not simulate model results.
Run from the project root: python scripts/execute_notebook.py
"""
from pathlib import Path
import os
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

root=Path(__file__).resolve().parents[1]
os.chdir(root)
path=root/'notebooks/FloodGuard_AI.ipynb'
nb=nbformat.read(path,as_version=4)
shell=InteractiveShell.instance()
count=0
for cell in nb.cells:
    if cell.cell_type!='code':continue
    count+=1
    with capture_output(stdout=True,stderr=True,display=True) as captured:
        result=shell.run_cell(cell.source,store_history=True)
    if result.error_before_exec or result.error_in_exec:
        raise RuntimeError(f'Notebook cell {count} failed: {result.error_before_exec or result.error_in_exec}')
    cell.execution_count=count
    cell.outputs=[]
    if captured.stdout:cell.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
    if captured.stderr:cell.outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
    for output in captured.outputs:
        cell.outputs.append(nbformat.v4.new_output('display_data',data=output.data,metadata=output.metadata))
nb.metadata['execution_method']='Actual sequential IPython execution in-process; kernel sockets unavailable in build environment.'
nbformat.validate(nb)
nbformat.write(nb,path)
print(f'Executed {count} code cells; no errors. Outputs saved in {path.name}.')
