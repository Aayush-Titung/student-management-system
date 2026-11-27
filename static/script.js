'use strict';
const $ = id => document.getElementById(id);
const fields = ['student_id','name','major','cgpa'];
let records = [], editing = null, filter = null, busy = false;
function status(message, type='') { $('status').textContent=message; $('status').className='status '+type; }
function draw(data) {
  records=data.records;
  for (const [key,value] of Object.entries(data.statistics)) $(key).textContent=value;
  const shown=filter===null?records:records.filter(r=>r.student_id===filter);
  $('count').textContent=shown.length; $('rows').replaceChildren(); $('empty').hidden=shown.length!==0;
  for (const record of shown) {
    const tr=document.createElement('tr'); if (record.student_id===editing) tr.className='selected';
    for (const key of fields) { const td=document.createElement('td'); td.textContent=key==='cgpa'?record[key].toFixed(2):record[key]; tr.append(td); }
    const td=document.createElement('td'), button=document.createElement('button'); button.type='button';button.className='secondary';button.textContent='Edit';button.setAttribute('aria-label','Edit '+record.student_id);button.addEventListener('click',()=>select(record));td.append(button);tr.append(td);$('rows').append(tr);
  }
}
let lastState=null;
function refresh(){if(lastState)draw(lastState);}
function select(record){editing=record.student_id;for(const key of fields)$(key).value=key==='cgpa'?record[key].toFixed(2):record[key];$('student_id').readOnly=true;$('formTitle').textContent='Edit student';$('formHint').textContent='Student ID is fixed. Blank fields keep their old value.';$('save').textContent='Update student';$('delete').hidden=false;refresh();status('Selected '+record.student_id+' for editing.');}
function clearForm(){editing=null;for(const key of fields)$(key).value='';$('student_id').readOnly=false;$('formTitle').textContent='Add student';$('formHint').textContent='Enter all four fields to create a record.';$('save').textContent='Add student';$('delete').hidden=true;refresh();}
function setBusy(value){busy=value;for(const id of ['save','samples','viewAll','delete','clear','confirmDelete'])$(id).disabled=value;}
async function request(action, values={}){
  if(busy)return;setBusy(true);
  try{
    const response=await fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action,...values})});
    const data=await response.json();
    if(data.records){lastState=data;if(action==='search'&&response.ok)filter=data.found.student_id;else if(action==='search'&&!response.ok)filter=null;else if(response.ok&&action!=='search')filter=null;draw(data);}
    if(!response.ok){status(data.message||'Request failed.','error');return;}
    if(action==='add'||action==='update'||action==='delete')clearForm();
    status(data.message,'success');
  }catch(error){status('Unable to connect. Please reload and try again.','error');}finally{setBusy(false);}
}
$('studentForm').addEventListener('submit',e=>{e.preventDefault();const values=Object.fromEntries(fields.map(k=>[k,$(k).value]));request(editing?'update':'add',values);});
$('searchForm').addEventListener('submit',e=>{e.preventDefault();request('search',{student_id:$('searchId').value});});
$('viewAll').addEventListener('click',()=>{filter=null;$('searchId').value='';refresh();status('Showing all student records.');});
$('samples').addEventListener('click',()=>request('samples'));
$('clear').addEventListener('click',()=>{clearForm();status('Form cleared.');});
$('delete').addEventListener('click',()=>{if(editing){$('confirmText').textContent='Remove '+editing+' from this session? This action cannot be undone.';$('confirmDialog').showModal();}});
$('cancelDelete').addEventListener('click',()=>$('confirmDialog').close());
$('confirmDelete').addEventListener('click',()=>{const student_id=editing;$('confirmDialog').close();if(student_id)request('delete',{student_id});});
(async()=>{setBusy(true);try{const response=await fetch('/api/state');if(!response.ok)throw Error();lastState=await response.json();draw(lastState);}catch(error){status('Unable to load records. Please reload.','error');}finally{setBusy(false);}})();
