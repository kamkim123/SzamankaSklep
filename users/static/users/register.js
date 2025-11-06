// 1) Zabezpieczenie przed podwójnym wysłaniem
    (function(){
      const form = document.getElementById('registerForm');
      const btn  = document.getElementById('submitBtn');
      if(form && btn){
        form.addEventListener('submit', function(){
          btn.disabled = true;
          btn.textContent = 'Wysyłanie…';
        });
      }
    })();

    // 2) Zamaskuj e-mail w karcie "Sprawdź maila" bez grzebania w backendzie
    (function(){
      const target = document.getElementById('emailMask');
      if(!target) return;
      // skorzystaj z POST danych wyrenderowanych przez Django:
      const raw = "{{ request.POST.email|default:'' }}";
      function maskEmail(email){
        if(!email) return '—';
        const [local, domain] = email.split('@');
        if(!domain) return email;
        const [dom, ...tldParts] = domain.split('.');
        const tld = tldParts.join('.') || '';
        const m = s => s.length <= 2 ? s[0] + '*' : s[0] + '*'.repeat(s.length-2) + s.slice(-1);
        return `${m(local)}@${m(dom)}${tld ? '.'+tld : ''}`;
      }
      target.textContent = maskEmail(raw);
    })();