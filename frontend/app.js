async function request(path, options){
 const target=document.getElementById('result'); target.textContent='Обработка...';
 try {const response=await fetch(path,options); const result=await response.json(); target.textContent=JSON.stringify(result,null,2);}
 catch(e){target.textContent='Нет связи с локальным сервером.';}
}
document.getElementById('analyze').onclick=()=>request('/analyzetext',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:document.getElementById('text').value})});
document.getElementById('vision').onclick=()=>{const file=document.getElementById('image').files[0];if(!file){document.getElementById('result').textContent='Сначала выберите изображение.';return;}const data=new FormData();data.append('file',file);request('/analyzeimage',{method:'POST',body:data});};
document.getElementById('parse').onclick=()=>request('/parsedemo',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:document.getElementById('url').value})});
document.getElementById('history').onclick=()=>request('/history');
