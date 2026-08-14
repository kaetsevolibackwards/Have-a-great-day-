(function(){
  const statusEl = document.getElementById('status');
  const msgEl = document.getElementById('message');
  const refresh = document.getElementById('refresh');
  const server = (new URL(window.location)).origin;

  function setStatus(s){ statusEl.textContent = s }

  async function fetchMessage(){
    try{
      setStatus('Connecting...')
      const res = await fetch(server + '/api/message');
      if(!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      msgEl.textContent = JSON.stringify(data, null, 2);
      setStatus('Online')
    }catch(e){
      setStatus('Offline')
      msgEl.textContent = '(failed to fetch) ' + e.message
    }
  }

  refresh.addEventListener('click', fetchMessage);
  fetchMessage();
})();
