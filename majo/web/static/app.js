/* Mejora progresiva: sin JS la app sigue funcionando con formularios normales. */
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const money=n=>'$'+Math.round(n).toLocaleString('es-CO');
const root=document.documentElement;

/* Tema claro / oscuro */
const tb=$('#themeBtn');
const paint=()=>tb.textContent=root.dataset.theme==='dark'?'☀️':'🌙';paint();
tb.onclick=()=>{root.dataset.theme=root.dataset.theme==='dark'?'light':'dark';localStorage.setItem('mj_theme',root.dataset.theme);paint()};

/* Aviso de cookies */
const ck=$('#ck');if(!localStorage.getItem('mj_ck'))ck.style.display='flex';
$('#ckOk').onclick=()=>{localStorage.setItem('mj_ck','1');ck.style.display='none'};

/* Avisos (toast) */
$$('.toast').forEach(t=>{$('button',t).onclick=()=>t.remove();setTimeout(()=>t.remove(),5000)});

/* Confirmación antes de acciones destructivas: <form data-confirm="mensaje"> */
const dlg=$('#confirm');let pending=null;
$$('form[data-confirm]').forEach(f=>f.addEventListener('submit',e=>{e.preventDefault();pending=f;$('#confirmMsg').textContent=f.dataset.confirm;dlg.showModal()}));
dlg.addEventListener('click',e=>{const v=e.target.value;if(!v)return;dlg.close();if(v==='si'&&pending){const f=pending;pending=null;f.removeAttribute('data-confirm');f.submit()}});

/* Filtro por categoría (chips) y búsqueda */
$$('[data-filter]').forEach(g=>g.addEventListener('click',e=>{
  const c=e.target.closest('.chip');if(!c)return;
  $$('.chip',g).forEach(x=>x.classList.toggle('on',x===c));
  $$('[data-cat-item]').forEach(i=>i.classList.toggle('hide',!!c.dataset.cat&&i.dataset.catItem!==c.dataset.cat));
}));
const q=$('#search');
if(q)q.addEventListener('input',()=>{const t=q.value.toLowerCase();$$('[data-name]').forEach(i=>i.classList.toggle('hide',!i.dataset.name.includes(t)))});

/* Punto de venta */
const pos=$('#pos');
if(pos){
  const tiles=$$('.tile',pos),sum=$('#summary'),totalEl=$('#total'),btn=$('#sellBtn'),bar=$('#barTotal'),recv=$('#recv'),chg=$('#change');
  const calc=()=>{
    let t=0,rows='';
    tiles.forEach(el=>{const n=+$('input',el).value,p=+el.dataset.price;el.classList.toggle('sel',n>0);$('output',el).textContent=n;
      if(n){t+=n*p;rows+=`<div class="line"><span>${n} × ${el.dataset.label}</span><b>${money(n*p)}</b></div>`}});
    sum.innerHTML=rows||'<p class="note">Toca + en un producto para empezar el pedido.</p>';
    totalEl.textContent=money(t);bar.textContent=money(t);btn.disabled=t===0;pos.dataset.t=t;chk();
  };
  const chk=()=>{const t=+pos.dataset.t,r=+recv.value||0,cash=$('input[name=pay]:checked').value==='Efectivo';
    $('#cash').classList.toggle('hide',!cash);chg.textContent=r>=t&&t?money(r-t):'—'};
  tiles.forEach(el=>el.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;const i=$('input',el);i.value=Math.max(0,+i.value+(b.dataset.d==='+'?1:-1));calc()}));
  $$('input[name=pay]',pos).forEach(r=>r.addEventListener('change',chk));recv.addEventListener('input',chk);
  $('#clear').onclick=()=>{tiles.forEach(el=>$('input',el).value=0);recv.value='';calc()};
  calc();
}
