/* OrcaRouter Cyber Inference settings: provider switch, dual authentication,
   live model discovery and the PKCE connect lifecycle. */

(() => {
  const $orca = (selector) => document.querySelector(selector);
  const state = {
    provider: 'gemini',
    models: [],
    selected: '',
    catalogDegraded: false,
    attemptId: null,
    generation: 0,
    poll: null,
    busy: false,
  };

  const el = {
    provider: () => $orca('#aiProvider'),
    panel: () => $orca('#orcaAuthPanel'),
    apiKey: () => $orca('#orcaApiKey'),
    keyStatus: () => $orca('#orcaKeyStatus'),
    clearKey: () => $orca('#orcaClearKey'),
    connect: () => $orca('#orcaConnect'),
    cancel: () => $orca('#orcaCancelConnect'),
    connectStatus: () => $orca('#orcaConnectStatus'),
    authorizeLink: () => $orca('#orcaAuthorizeLink'),
    trigger: () => $orca('#orcaModelTrigger'),
    label: () => $orca('#orcaModelLabel'),
    list: () => $orca('#orcaModelPanel'),
    hidden: () => $orca('#orcaModelValue'),
    catalogStatus: () => $orca('#orcaCatalogStatus'),
  };

  async function orcaRequest(url, options = {}) {
    const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
    let payload = {};
    try { payload = await response.json(); } catch (_) { /* not JSON */ }
    if (!response.ok) throw new Error(payload.error || 'Request failed');
    return payload;
  }

  function setKeyStatus(text, tone = '') {
    const node = el.keyStatus();
    if (!node) return;
    node.textContent = text;
    node.classList.toggle('orca-status-error', tone === 'error');
    node.classList.toggle('orca-status-ok', tone === 'ok');
  }

  function setConnectStatus(text, tone = '') {
    const node = el.connectStatus();
    if (!node) return;
    node.textContent = text;
    node.classList.toggle('orca-status-error', tone === 'error');
    node.classList.toggle('orca-status-ok', tone === 'ok');
  }

  function setBusy(busy) {
    state.busy = busy;
    const connect = el.connect();
    const cancel = el.cancel();
    if (connect) {
      connect.disabled = busy;
      connect.textContent = busy ? 'Waiting for authorization…' : 'Connect with OrcaRouter';
    }
    if (cancel) cancel.hidden = !busy;
  }

  function badgeFor(model) {
    if (model.default) return '<span class="orca-model-badge">default</span>';
    if (model.recommended_for_security_teams) return '<span class="orca-model-badge">security teams</span>';
    if (model.fallback) return '<span class="orca-model-badge">fallback</span>';
    if (model.verified) return '<span class="orca-model-badge">verified</span>';
    return '';
  }

  function renderModels() {
    const list = el.list();
    if (!list) return;
    list.innerHTML = state.models.map((model, index) => {
      const active = model.id === state.selected ? ' active' : '';
      const description = model.description ? `<small>${String(model.description).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))}</small>` : '';
      return `<button type="button" class="orca-model-option${active}" role="option" aria-selected="${model.id === state.selected}" data-model-id="${model.id}" data-model-index="${index}"><span>${model.id}${badgeFor(model)}</span>${description}</button>`;
    }).join('');
    list.querySelectorAll('[data-model-id]').forEach((option) => {
      option.addEventListener('click', () => selectModel(option.dataset.modelId));
    });
  }

  function selectModel(modelId) {
    const model = state.models.find((item) => item.id === modelId);
    if (!model) return;
    state.selected = modelId;
    const hidden = el.hidden();
    if (hidden) hidden.value = modelId;
    const label = el.label();
    if (label) label.textContent = modelId + (model.default ? ' (default)' : '');
    renderModels();
    closeModelPanel();
  }

  function openModelPanel() {
    const list = el.list();
    const trigger = el.trigger();
    if (!list || !trigger) return;
    list.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
    list.scrollIntoView({ block: 'nearest' });
  }

  function closeModelPanel() {
    const list = el.list();
    const trigger = el.trigger();
    if (list) list.hidden = true;
    if (trigger) trigger.setAttribute('aria-expanded', 'false');
  }

  async function loadModels() {
    const label = el.label();
    const status = el.catalogStatus();
    if (label) label.textContent = 'Loading models…';
    if (status) { status.textContent = ''; status.classList.remove('orca-status-error'); }
    const previous = state.selected;
    try {
      const payload = await orcaRequest('/api/ai/models?provider=orcarouter&capability=chat');
      state.models = Array.isArray(payload.models) ? payload.models : [];
      state.catalogDegraded = Boolean(payload.degraded);
      const ids = state.models.map((model) => model.id);
      const desired = state.selected || previous;
      if (desired && !ids.includes(desired)) {
        state.selected = '';
        setConnectStatus('The previously selected model is no longer available. Choose another.', 'error');
      } else if (desired) {
        state.selected = desired;
      }
      if (!state.selected) {
        const fallback = state.models.find((model) => model.default) || state.models[0];
        state.selected = fallback ? fallback.id : '';
      }
      if (state.selected) selectModel(state.selected);
      else if (label) label.textContent = 'No compatible models';
      if (status) {
        if (!state.models.length) {
          status.textContent = 'No compatible chat models are available right now.';
          status.classList.add('orca-status-error');
        } else if (payload.degraded) {
          status.textContent = `Live catalog unavailable (${payload.error || 'no detail'}); showing verified fallback models.`;
        } else {
          status.textContent = `${state.models.length} chat models discovered from the live OrcaRouter catalog.`;
        }
      }
    } catch (error) {
      state.models = [];
      state.selected = '';
      state.catalogDegraded = true;
      if (label) label.textContent = 'Catalog unavailable';
      if (status) { status.textContent = error.message; status.classList.add('orca-status-error'); }
      renderModels();
    }
  }

  async function refreshConfig() {
    try {
      const config = await orcaRequest('/api/config');
      state.provider = config.ai_provider === 'orcarouter' ? 'orcarouter' : 'gemini';
      const provider = el.provider();
      if (provider) provider.value = state.provider;
      applyProvider(state.provider, { resetModels: false });
      const orca = config.orcarouter || {};
      if (orca.configured) {
        const how = orca.credential_source === 'pkce' ? 'OrcaRouter sign-in' : 'stored API key';
        setKeyStatus(`A credential from ${how} is stored. Enter a new key to replace it.`, 'ok');
      } else {
        setKeyStatus('No OrcaRouter credential stored. Paste a key or connect your account.');
      }
      if (orca.needs_reauth) {
        setConnectStatus('OrcaRouter rejected the stored credential. Connect again or paste a new key.', 'error');
      }
      if (config.orcarouter_model) {
        state.selected = config.orcarouter_model;
        const hidden = el.hidden();
        if (hidden) hidden.value = state.selected;
      }
      return config;
    } catch (error) {
      setKeyStatus(error.message, 'error');
      return null;
    }
  }

  function applyProvider(provider, { resetModels = true } = {}) {
    state.provider = provider;
    const panel = el.panel();
    if (panel) panel.hidden = provider !== 'orcarouter';
    if (provider === 'orcarouter' && resetModels) loadModels();
    if (provider === 'orcarouter' && !resetModels && !state.models.length) loadModels();
  }

  function stopPolling() {
    if (state.poll) {
      clearInterval(state.poll);
      state.poll = null;
    }
  }

  async function pollAttempt(attemptId, generation) {
    if (generation !== state.generation) return;
    try {
      const payload = await orcaRequest(`/api/ai/connect/status?attempt_id=${encodeURIComponent(attemptId)}`);
      if (generation !== state.generation) return;
      if (payload.status === 'pending') return;
      stopPolling();
      state.attemptId = null;
      setBusy(false);
      const link = el.authorizeLink();
      if (link) link.hidden = true;
      if (payload.status === 'success') {
        setConnectStatus('Connected. The OrcaRouter key is stored locally for this workspace.', 'ok');
        await refreshConfig();
      } else if (payload.status === 'cancelled') {
        setConnectStatus('Authorization cancelled.');
      } else {
        setConnectStatus(payload.error || 'Authorization failed; start again.', 'error');
      }
    } catch (error) {
      if (generation !== state.generation) return;
      stopPolling();
      state.attemptId = null;
      setBusy(false);
      setConnectStatus(error.message, 'error');
    }
  }

  async function startConnect() {
    if (state.busy) return;
    stopPolling();
    state.generation += 1;
    const generation = state.generation;
    setBusy(true);
    setConnectStatus('Starting the OrcaRouter authorization…');
    try {
      const payload = await orcaRequest('/api/ai/connect/start', { method: 'POST', body: '{}' });
      if (generation !== state.generation) return;
      state.attemptId = payload.attempt_id;
      const link = el.authorizeLink();
      if (link) { link.href = payload.authorize_url; link.hidden = false; }
      setConnectStatus('Approve the request in your browser. This panel updates automatically.');
      window.open(payload.authorize_url, '_blank', 'noopener');
      state.poll = setInterval(() => pollAttempt(payload.attempt_id, generation), 1200);
    } catch (error) {
      if (generation !== state.generation) return;
      state.attemptId = null;
      setBusy(false);
      setConnectStatus(error.message, 'error');
    }
  }

  async function cancelConnect() {
    const attemptId = state.attemptId;
    state.generation += 1;
    state.attemptId = null;
    stopPolling();
    setBusy(false);
    const link = el.authorizeLink();
    if (link) link.hidden = true;
    setConnectStatus('Authorization cancelled.');
    if (attemptId) {
      try {
        await orcaRequest('/api/ai/connect/cancel', { method: 'POST', body: JSON.stringify({ attempt_id: attemptId }) });
      } catch (_) { /* the server-side attempt expires on its own */ }
    }
  }

  async function clearKey() {
    try {
      await orcaRequest('/api/ai/credentials', { method: 'POST', body: JSON.stringify({ method: 'clear' }) });
      const input = el.apiKey();
      if (input) input.value = '';
      setKeyStatus('Stored OrcaRouter credential cleared.');
      setConnectStatus('');
    } catch (error) {
      setKeyStatus(error.message, 'error');
    }
  }

  // pagehide must clear the busy state synchronously: the browser may restore
  // this page from the back-forward cache without running any guarded finally.
  window.addEventListener('pagehide', () => {
    if (!state.attemptId) return;
    const attemptId = state.attemptId;
    state.attemptId = null;
    state.generation += 1;
    stopPolling();
    state.busy = false;
    const connect = el.connect();
    if (connect) { connect.disabled = false; connect.textContent = 'Connect with OrcaRouter'; }
    const cancel = el.cancel();
    if (cancel) cancel.hidden = true;
    setConnectStatus('Authorization interrupted. Start again when ready.');
    try {
      fetch('/api/ai/connect/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ attempt_id: attemptId }),
        keepalive: true,
      }).catch(() => {});
    } catch (_) { /* best effort */ }
  });

  function wire() {
    const provider = el.provider();
    if (provider) {
      provider.addEventListener('change', () => applyProvider(provider.value === 'orcarouter' ? 'orcarouter' : 'gemini'));
    }
    const connect = el.connect();
    if (connect) connect.addEventListener('click', startConnect);
    const cancel = el.cancel();
    if (cancel) cancel.addEventListener('click', cancelConnect);
    const clear = el.clearKey();
    if (clear) clear.addEventListener('click', clearKey);
    const trigger = el.trigger();
    if (trigger) {
      trigger.addEventListener('click', () => {
        if (el.list() && el.list().hidden) openModelPanel();
        else closeModelPanel();
      });
    }
    document.addEventListener('click', (event) => {
      const picker = document.querySelector('.orca-model-picker');
      if (picker && !picker.contains(event.target)) closeModelPanel();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeModelPanel();
    });
    refreshConfig();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire, { once: true });
  } else {
    wire();
  }
})();
