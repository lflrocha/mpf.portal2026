(() => {
        const form = document.getElementById("feedback-form");
        if (!form) return;

        const alertBox = document.getElementById("form-alert");

        const anonimo = document.getElementById("anonimo");
        const emailWrapper = document.getElementById("email-wrapper");
        const email = document.getElementById("email");

        const fields = {
          categoria: {
            el: document.getElementById("categoria"),
            err: document.getElementById("categoria-erro"),
            validate: (el) => !!el.value
          },
          nota: {
            el: form.querySelector('input[name="nota"]'),
            err: document.getElementById("nota-erro"),
            validate: () => !!form.querySelector('input[name="nota"]:checked')
          },
          positivo: {
            el: document.getElementById("positivo"),
            err: document.getElementById("positivo-erro"),
            validate: (el) => el.value.trim().length > 0
          },
          melhorar: {
            el: document.getElementById("melhorar"),
            err: document.getElementById("melhorar-erro"),
            validate: (el) => el.value.trim().length > 0
          },
          consentimento: {
            el: document.getElementById("consentimento"),
            err: document.getElementById("consentimento-erro"),
            validate: (el) => el.checked
          },
          pagina: {
            el: document.getElementById("pagina"),
            err: document.getElementById("pagina-erro"),
            validate: (el) => {
              const v = el.value.trim();
              if (!v) return true;
              try {
                const u = new URL(v);
                return u.protocol === "https:" || u.protocol === "http:";
              } catch {
                return false;
              }
            }
          },
          email: {
            el: document.getElementById("email"),
            err: document.getElementById("email-erro"),
            validate: (el) => {
              if (anonimo && anonimo.checked) return true;
              const v = el.value.trim();
              if (!v) return true; // opcional
              return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
            }
          }
        };

        const setError = (key, hasError) => {
          const f = fields[key];
          if (!f || !f.el || !f.err) return;

          if (hasError) {
            f.el.setAttribute("aria-invalid", "true");
            f.el.classList.add("border-red-300");
            f.el.classList.add("focus:ring-red-200");
            f.err.classList.remove("hidden");
          } else {
            f.el.removeAttribute("aria-invalid");
            f.el.classList.remove("border-red-300");
            f.el.classList.remove("focus:ring-red-200");
            f.err.classList.add("hidden");
          }
        };

        const validateAll = () => {
          let firstInvalid = null;
          let invalidCount = 0;

          // valida campos simples
          Object.keys(fields).forEach((key) => {
            const f = fields[key];
            if (!f) return;

            // não marcar erro de email se estiver oculto por anônimo
            if (key === "email" && anonimo && anonimo.checked) {
              setError("email", false);
              return;
            }

            const ok = typeof f.validate === "function"
              ? f.validate(f.el)
              : true;

            const hasError = !ok;
            setError(key, hasError);

            if (hasError && !firstInvalid) firstInvalid = f.el;
            if (hasError) invalidCount++;
          });

          // valida radiogroup (nota): foco vai para o primeiro input
          if (!fields.nota.validate()) {
            invalidCount++;
            fields.nota.err.classList.remove("hidden");
            if (!firstInvalid) firstInvalid = form.querySelector('input[name="nota"]');
          } else {
            fields.nota.err.classList.add("hidden");
          }

          if (alertBox) {
            if (invalidCount > 0) alertBox.classList.remove("hidden");
            else alertBox.classList.add("hidden");
          }

          return { ok: invalidCount === 0, firstInvalid };
        };

        // Anônimo: esconde e limpa email
        const syncAnonimo = () => {
          if (!anonimo || !emailWrapper || !email) return;
          const on = anonimo.checked;

          if (on) {
            email.value = "";
            emailWrapper.classList.add("hidden");
            email.setAttribute("tabindex", "-1");
            email.setAttribute("aria-hidden", "true");
            setError("email", false);
          } else {
            emailWrapper.classList.remove("hidden");
            email.removeAttribute("tabindex");
            email.removeAttribute("aria-hidden");
          }
        };

        if (anonimo) {
          anonimo.addEventListener("change", syncAnonimo);
          syncAnonimo();
        }

        // remove erro conforme usuário digita/seleciona
        ["change", "input", "blur"].forEach((evt) => {
          form.addEventListener(evt, (e) => {
            const target = e.target;
            if (!target || !(target instanceof HTMLElement)) return;

            const map = {
              categoria: "categoria",
              positivo: "positivo",
              melhorar: "melhorar",
              pagina: "pagina",
              email: "email",
              consentimento: "consentimento"
            };

            if (target.id && map[target.id]) {
              const key = map[target.id];
              const ok = fields[key].validate(fields[key].el);
              setError(key, !ok);
              if (alertBox) alertBox.classList.add("hidden");
            }

            // nota
            if (target.matches && target.matches('input[name="nota"]')) {
              if (fields.nota.validate()) fields.nota.err.classList.add("hidden");
              if (alertBox) alertBox.classList.add("hidden");
            }
          }, true);
        });

        form.addEventListener("submit", (e) => {
          const { ok, firstInvalid } = validateAll();
          if (!ok) {
            e.preventDefault();
            if (firstInvalid && firstInvalid.focus) firstInvalid.focus();
            if (alertBox) alertBox.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      })();

// feedback.js — seta dos selects (controle por classe .is-open)
(() => {
  const wraps = Array.from(document.querySelectorAll(".feedback-select"));
  if (!wraps.length) return;

  const closeAll = (except = null) => {
    wraps.forEach((w) => {
      if (w !== except) w.classList.remove("is-open");
    });
  };

  const isInsideAny = (target) => wraps.some((w) => w.contains(target));

  wraps.forEach((wrap) => {
    const sel = wrap.querySelector("select");
    if (!sel) return;

    // abrir ao interagir (mousedown/pointerdown é mais confiável que focus)
    sel.addEventListener("pointerdown", () => {
      closeAll(wrap);
      wrap.classList.add("is-open");
    });

    // fechar ao mudar a opção
    sel.addEventListener("change", () => {
      wrap.classList.remove("is-open");
    });

    // fechar ao perder foco (tab/shift+tab)
    sel.addEventListener("blur", () => {
      wrap.classList.remove("is-open");
    });

    // ESC fecha (quando o select estiver focado)
    sel.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        wrap.classList.remove("is-open");
        sel.blur();
      }
    });
  });

  // clique fora fecha tudo (capture=true ajuda muito)
  document.addEventListener(
    "pointerdown",
    (e) => {
      if (!isInsideAny(e.target)) closeAll(null);
    },
    true
  );

  // fallback para quem navega por teclado: foco foi pra outro lugar
  document.addEventListener(
    "focusin",
    (e) => {
      if (!isInsideAny(e.target)) closeAll(null);
    },
    true
  );
})();


