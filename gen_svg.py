import html
import json
import sys

WIDTH = 360
HEIGHT = 200
SCALE = 2
SVG_W = 1150
SVG_H = 1150


def create_key_buttons(keys_info):
  out = []
  for info in keys_info:
    key = info["key"]
    label = html.escape(info.get("value") or key)
    x = info["x"]
    y = info["y"]
    w = info["width"]
    h = info["height"]
    key_js = json.dumps(key)
    if info.get("toggle"):
      raw_handler = f"button_toggle({key_js})"
      handler = f'onclick="{html.escape(raw_handler, quote=True)}"'
    else:
      d_js = html.escape(f"button_down({key_js})", quote=True)
      u_js = html.escape(f"button_up({key_js})", quote=True)
      handler = f'onmousedown="{d_js}" onmouseup="{u_js}" onmouseleave="{u_js}"'
    out.append(
        f'<button type="button" id="button_{html.escape(key, quote=True)}" '
        f'style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
        f'font-size:9px;padding:0;cursor:pointer;" {handler}>{label}</button>'
    )
  return "\n".join(out)


def create_keys_row(keys, x, y, width, height, gap):
  out = []
  for i, key in enumerate(keys):
    new_x = x + i * (width + gap)
    key_js = json.dumps(key)
    out.append(
        f'<button type="button" id="button_{html.escape(key)}" '
        f'style="position:absolute;left:{new_x}px;top:{y}px;width:{width}px;'
        f'height:{height}px;font-size:9px;padding:0;cursor:pointer;" '
        f'onmousedown="{html.escape(f"button_down({key_js})", quote=True)}" '
        f'onmouseup="{html.escape(f"button_up({key_js})", quote=True)}" '
        f'onmouseleave="{html.escape(f"button_up({key_js})", quote=True)}">{html.escape(key.upper())}</button>'
    )
  return "\n".join(out)


if __name__ == "__main__":
  with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as f:
    js = f.read()

  # Evita fechar acidentalmente a tag <script> no SVG
  safe_js = js.replace("</script>", "<\\/script>").replace("]]>", "]]]]><![CDATA[>")

  fb_lines = "\n".join(
      f'<div id="field_{i}" style="height:3.6px;line-height:3.6px;font-size:3.6px;letter-spacing:0px;white-space:pre;font-family:monospace;color:#9df;overflow:hidden;"></div>'
      for i in range(HEIGHT)
  )

  console_lines = "\n".join(
      f'<div id="console_{i}" style="height:8px;line-height:8px;font-size:7px;'
      f'white-space:pre;font-family:monospace;"></div>'
      for i in range(25)
  )

  key_buttons_html = create_key_buttons([
      dict(key="Esc", x=220, y=170, width=20, height=12),
      dict(key="`", x=220, y=148, width=12, height=16),
      dict(key="Backspace", value="<----", x=550, y=148, width=50, height=16),
      dict(key="Tab", x=220, y=128, width=24, height=16),
      dict(key="\\", x=562, y=128, width=38, height=16),
      dict(key="CapsLock", value="Caps", x=220, y=108, width=30, height=16),
      dict(key="Enter", x=542, y=108, width=58, height=16),
      dict(key="Shift", x=220, y=88, width=44, height=16, toggle=True),
      dict(key="RShift", x=530, y=88, width=70, height=16),
      dict(key="Ctrl", x=220, y=68, width=36, height=16, toggle=True),
      dict(key="Alt", x=260, y=68, width=36, height=16, toggle=True),
      dict(key="Space", x=300, y=68, width=174, height=16),
      dict(key="RAlt", value="Alt", x=480, y=68, width=36, height=16, toggle=True),
      dict(key="ContextMenu", value="Menu", x=522, y=68, width=36, height=16),
      dict(key="RCtrl", value="Ctrl", x=564, y=68, width=36, height=16, toggle=True),
      dict(key="Home", x=608, y=148, width=32, height=16),
      dict(key="Insert", value="Ins", x=608, y=128, width=32, height=16),
      dict(key="Delete", value="Del", x=608, y=108, width=32, height=16),
      dict(key="End", x=646, y=148, width=32, height=16),
      dict(key="PgUp", x=646, y=128, width=32, height=16),
      dict(key="PgDn", x=646, y=108, width=32, height=16),
      dict(key="ArrowUp", value="^", x=633, y=88, width=20, height=16),
      dict(key="ArrowLeft", value="<", x=608, y=68, width=20, height=16),
      dict(key="ArrowDown", value="v", x=633, y=68, width=20, height=16),
      dict(key="ArrowRight", value=">", x=658, y=68, width=20, height=16),
  ])

  rows_html = "\n".join([
      create_keys_row([f"F{i}" for i in range(1, 13)], 246, 170, 22, 12, 6),
      create_keys_row("1234567890-=", 238, 148, 20, 16, 6),
      create_keys_row("qwertyuiop[]", 250, 128, 20, 16, 6),
      create_keys_row("asdfghjkl;'", 256, 108, 20, 16, 6),
      create_keys_row("zxcvbnm,./", 270, 88, 20, 16, 6),
  ])

  shim_js = """
(function() {
  const _cache = Object.create(null);
  function wrapEl(el) {
    return {
      get value() {
        if (!el) return "";
        return "value" in el ? el.value : el.textContent;
      },
      set value(v) {
        if (!el) return;
        const s = v == null ? "" : String(v);
        if ("value" in el) {
          el.value = s;
        } else {
          el.textContent = s;
        }
      }
    };
  }
  if (typeof globalThis.ENVIRONMENT_IS_SHELL === "undefined") {
    globalThis.ENVIRONMENT_IS_SHELL = true;
  }
  if (typeof globalThis.print !== "function" && typeof console !== "undefined" && console.log) {
    globalThis.print = function(msg) {
      console.log(msg);
    };
  }

  if (typeof globalThis.scriptDirectory === "undefined") {
    var _baseHref = (typeof window !== "undefined" && window.location && window.location.href)
      ? window.location.href.replace(/[^/\\?#]*([?#].*)?$/, "")
      : "./";
    globalThis.scriptDirectory = _baseHref;
  }
  if (typeof globalThis.Module === "object" && globalThis.Module !== null && typeof globalThis.Module.locateFile !== "function") {
    globalThis.Module.locateFile = function(path, prefix) {
      return (prefix || globalThis.scriptDirectory || "./") + path;
    };
  }

  if (typeof globalThis.app === "undefined") {
    globalThis.app = {
      setInterval: function(fn, ms) {
        return window.setInterval(fn, ms);
      },
      setTimeOut: function(fn, ms) {
        return window.setTimeout(fn, ms);
      },
      setTimeout: function(fn, ms) {
        return window.setTimeout(fn, ms);
      },
      clearTimeOut: function(id) {
        return window.clearTimeout(id);
      },
      clearInterval: function(id) {
        return window.clearInterval(id);
      },
      alert: function(msg) {
        if (typeof console !== "undefined" && console.error) {
          console.error(msg);
        }
        if (typeof window.alert === "function") {
          window.alert(msg);
        }
      }
    };
  }

  if (typeof globalThis.getField !== "function") {
    globalThis.getField = function(name) {
      if (!_cache[name]) {
        _cache[name] = wrapEl(document.getElementById(name));
      }
      return _cache[name];
    };
  }
})();
"""

  svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">
  <foreignObject x="0" y="0" width="{SVG_W}" height="{SVG_H}">
    <div xmlns="http://www.w3.org/1999/xhtml" style="position:relative;width:{SVG_W}px;height:{SVG_H}px;background:#fff;overflow:hidden;font-family:monospace;">
      <div style="position:absolute;left:220px;top:10px;font-size:20px;font-weight:bold;">LinuxSVG</div>
      <div id="console_box" style="position:absolute;left:8px;top:8px;width:200px;height:204px;border:1px solid #ccc;padding:2px;overflow:hidden;">
        {console_lines}
      </div>
      <div id="speed_indicator" style="position:absolute;left:582px;top:10px;width:110px;height:14px;font-size:10px;">Loading...</div>
      <div id="key_status" style="position:absolute;left:220px;top:42px;width:260px;height:14px;font-size:10px;">Pressed:</div>
      <input id="key_input" type="text" value="Type here for keyboard inputs."
             style="position:absolute;left:500px;top:40px;width:185px;height:16px;font-size:10px;"
             oninput="key_pressed(this.value)" />
      {key_buttons_html}
      {rows_html}
      <div style="position:absolute;left:220px;top:192px;font-size:8px;">Baseado no linuxPDF — </div>
      <div id="fb_box" style="position:absolute;left:0px;top:220px;width:{SVG_W}px;height:820px;background:#000;color:#9df;overflow-x:hidden;overflow-y:auto;">
        {fb_lines}
      </div>
    </div>
  </foreignObject>
  <script type="application/ecmascript"><![CDATA[
{shim_js}
{safe_js}
  ]]></script>
</svg>
"""

  with open(sys.argv[2], "w", encoding="utf-8") as f:
    f.write(svg)
